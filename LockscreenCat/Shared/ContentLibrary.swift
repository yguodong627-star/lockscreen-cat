import Foundation

/// 句库加载器。读取 App 包里的 roasts.json 与 encouragements.json（图文 Bot 产出），
/// 对结构做宽松兼容：
///  · 吐槽：roasts.json 的 "roasts"（步数桶 → 入睡桶 → [句子]）
///  · 鼓励：encouragements.json 的 "encouragements"；也接受 roasts.json 里的 "encouragements"/"encouragement"/"encourage"/"praise"
///  · 读不到睡眠：各自文件里的 "no_sleep_data"（步数桶 → [句子]）
///  · 某个桶直接是数组（不分入睡桶）时，视为对所有入睡桶适用
///  缺什么就用内置的占位句兜底（见 builtin*）。
struct ContentLibrary {
    typealias Grid = [String: [String: [String]]]   // step -> bedtime -> lines
    typealias Row = [String: [String]]              // step -> lines

    var roast: Grid = [:]
    var encourage: Grid = [:]
    var roastNoSleep: Row = [:]
    var encourageNoSleep: Row = [:]
    /// 是否用到了内置占位鼓励句
    var usesPlaceholderEncouragements = false

    /// 是否借用了猫的句库（小狗句库文件还没放进来时）
    var borrowedCatLines = false

    /// 当前形象的句库
    static var shared: ContentLibrary { forPet(Pet.current) }

    private static var cache: [Pet: ContentLibrary] = [:]
    private static let cacheLock = NSLock()

    static func forPet(_ pet: Pet, bundle: Bundle = .main) -> ContentLibrary {
        cacheLock.lock(); defer { cacheLock.unlock() }
        if let c = cache[pet] { return c }
        let lib = load(pet: pet,
                       roastsData: data("roasts" + pet.contentSuffix, bundle: bundle),
                       encouragementsData: data("encouragements" + pet.contentSuffix, bundle: bundle),
                       catRoastsData: { data("roasts", bundle: bundle) },
                       catEncouragementsData: { data("encouragements", bundle: bundle) })
        cache[pet] = lib
        return lib
    }

    /// 按形象加载：cat → roasts.json / encouragements.json；
    /// dog → roasts_dog.json / encouragements_dog.json，缺哪个就借猫的那个（只替换“本猫/橘猫”称呼）。
    static func load(pet: Pet, roastsData: Data?, encouragementsData: Data?,
                     catRoastsData: () -> Data?, catEncouragementsData: () -> Data?) -> ContentLibrary {
        var r = roastsData, e = encouragementsData
        var borrowR = false, borrowE = false
        if pet != .cat {
            if r == nil { r = catRoastsData(); borrowR = r != nil }
            if e == nil { e = catEncouragementsData(); borrowE = e != nil }
        }
        var lib = load(roastsData: r, encouragementsData: e)
        let v: (String) -> String = { pet.voiceForBorrowedLine($0) }
        if borrowR {
            lib.roast = lib.roast.mapValues { $0.mapValues { $0.map(v) } }
            lib.roastNoSleep = lib.roastNoSleep.mapValues { $0.map(v) }
        }
        if borrowE {
            lib.encourage = lib.encourage.mapValues { $0.mapValues { $0.map(v) } }
            lib.encourageNoSleep = lib.encourageNoSleep.mapValues { $0.map(v) }
        }
        lib.borrowedCatLines = borrowR || borrowE
        return lib
    }

    static func load(roastsData: Data?, encouragementsData: Data?) -> ContentLibrary {
        var lib = ContentLibrary()
        let roastsDict = parse(roastsData)
        let encDict = parse(encouragementsData)

        if let r = roastsDict {
            lib.roast = grid(r["roasts"])
            lib.roastNoSleep = row(r["no_sleep_data"])
            for k in ["encouragements", "encouragement", "encourage", "praise"] where lib.encourage.isEmpty {
                lib.encourage = grid(r[k])
            }
        }
        if let e = encDict {
            for k in ["encouragements", "encouragement", "encourage", "praise", "roasts"] {
                let g = grid(e[k])
                if !g.isEmpty { lib.encourage = g; break }
            }
            let ns = row(e["no_sleep_data"])
            if !ns.isEmpty { lib.encourageNoSleep = ns }
        }
        if lib.roast.isEmpty { lib.roast = builtinRoast }
        if lib.roastNoSleep.isEmpty { lib.roastNoSleep = builtinRoastNoSleep }
        if lib.encourage.isEmpty {
            lib.encourage = builtinEncourage
            lib.usesPlaceholderEncouragements = true
        }
        if lib.encourageNoSleep.isEmpty {
            lib.encourageNoSleep = builtinEncourageNoSleep
            lib.usesPlaceholderEncouragements = true
        }
        return lib
    }

    // MARK: 查询

    /// 候选句。bedtimeBucket 为 nil 时用 no_sleep_data 句库。桶为空时逐级兜底。
    func candidates(tone: Tone, stepBucket: String, bedtimeBucket: String?) -> [String] {
        let g = tone == .encourage ? encourage : roast
        let ns = tone == .encourage ? encourageNoSleep : roastNoSleep
        if let bb = bedtimeBucket {
            if let lines = g[stepBucket]?[bb], !lines.isEmpty { return lines }
            let sameStep = (g[stepBucket] ?? [:]).values.flatMap { $0 }
            if !sameStep.isEmpty { return sameStep }
        } else {
            if let lines = ns[stepBucket], !lines.isEmpty { return lines }
            // no_sleep_data 缺失：用不含 {bedtime} 的普通句
            let noBed = (g[stepBucket] ?? [:]).values.flatMap { $0 }.filter { !$0.contains("{bedtime}") }
            if !noBed.isEmpty { return noBed }
        }
        let fallback = tone == .encourage ? ContentLibrary.builtinEncourageNoSleep : ContentLibrary.builtinRoastNoSleep
        return fallback[stepBucket] ?? ["今日观察记录暂缺，我先去睡了。"]
    }

    /// 把模板里的 {steps} {bedtime} 换成真实数据（步数千分位，入睡 HH:mm 北京时间）
    static func render(_ template: String, steps: Int?, bedtime: Date?) -> String {
        template
            .replacingOccurrences(of: "{steps}", with: steps.map { BJ.steps($0) } ?? "0")
            .replacingOccurrences(of: "{bedtime}", with: bedtime.map { BJ.hhmm($0) } ?? "--:--")
    }

    // MARK: JSON 解析（宽松）

    private static func data(_ name: String, bundle: Bundle) -> Data? {
        guard let url = bundle.url(forResource: name, withExtension: "json") else { return nil }
        return try? Data(contentsOf: url)
    }

    private static func parse(_ data: Data?) -> [String: Any]? {
        guard let data, let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else { return nil }
        return obj
    }

    static func grid(_ any: Any?) -> Grid {
        guard let dict = any as? [String: Any] else { return [:] }
        var out: Grid = [:]
        for (step, v) in dict {
            if let inner = v as? [String: Any] {
                var m: [String: [String]] = [:]
                for (bed, lines) in inner {
                    if let arr = lines as? [String] { m[bed] = arr.filter { !$0.isEmpty } }
                }
                if !m.isEmpty { out[step] = m }
            } else if let arr = v as? [String] {
                var m: [String: [String]] = [:]
                for bb in ToneRule.bedtimeBuckets { m[bb] = arr }
                out[step] = m
            }
        }
        return out
    }

    static func row(_ any: Any?) -> Row {
        if let arr = any as? [String] {
            var m: Row = [:]
            for sb in ToneRule.stepBuckets { m[sb] = arr }
            return m
        }
        guard let dict = any as? [String: Any] else { return [:] }
        var out: Row = [:]
        for (step, v) in dict {
            if let arr = v as? [String] { out[step] = arr.filter { !$0.isEmpty } }
        }
        return out
    }

    // MARK: 内置兜底句（占位，只在 JSON 缺失时使用）

    static let builtinRoast: Grid = {
        var g: Grid = [:]
        for sb in ToneRule.stepBuckets {
            g[sb] = [:]
            for bb in ToneRule.bedtimeBuckets {
                g[sb]?[bb] = ["【占位】该人类今日 {steps} 步，{bedtime} 入睡，不予置评。"]
            }
        }
        return g
    }()

    static let builtinEncourage: Grid = {
        var g: Grid = [:]
        for sb in ToneRule.stepBuckets {
            g[sb] = [:]
            for bb in ToneRule.bedtimeBuckets {
                g[sb]?[bb] = [
                    "【占位】{steps} 步，今天的你，勉强认可。",
                    "【占位】{bedtime} 入睡，明天继续保持。",
                ]
            }
        }
        return g
    }()

    static let builtinRoastNoSleep: Row = {
        var r: Row = [:]
        for sb in ToneRule.stepBuckets { r[sb] = ["【占位】{steps} 步，睡眠记录空空，无从下嘴。"] }
        return r
    }()

    static let builtinEncourageNoSleep: Row = {
        var r: Row = [:]
        for sb in ToneRule.stepBuckets { r[sb] = ["【占位】{steps} 步，今天也算交了作业。"] }
        return r
    }()
}
