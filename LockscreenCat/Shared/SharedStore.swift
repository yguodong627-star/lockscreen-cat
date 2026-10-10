import Foundation

/// App Group UserDefaults 读写（App 和小组件共用）。
/// 示例数据模式下用 "demo." 前缀的独立历史，不污染真实记录。
final class SharedStore {
    static let shared = SharedStore()

    let defaults: UserDefaults
    init(defaults: UserDefaults = AppConfig.sharedDefaults) { self.defaults = defaults }

    private enum K {
        static let useSample = "useSampleData"
        static let samplePreset = "samplePreset"
        static let phaseOverride = "phaseOverride"
        static let reminderEnabled = "reminderEnabled"
        static let reminderHour = "reminderHour"
        static let reminderMinute = "reminderMinute"
        static let onboarded = "onboardingDone"
        static let pet = "pet"
        static let snapshot = "snapshot"
        static let days = "dayStates"
        static let history = "lineHistory"
    }

    private var prefix: String { useSampleData ? "demo." : "" }

    // MARK: 设置

    var useSampleData: Bool {
        get { defaults.bool(forKey: K.useSample) }
        set { defaults.set(newValue, forKey: K.useSample) }
    }
    var samplePreset: SamplePreset {
        get { SamplePreset(rawValue: defaults.string(forKey: K.samplePreset) ?? "") ?? .mixed }
        set { defaults.set(newValue.rawValue, forKey: K.samplePreset) }
    }
    /// 调试：强制时段（nil = 自动）
    var phaseOverride: DayPhase? {
        get { defaults.string(forKey: K.phaseOverride).flatMap { DayPhase(rawValue: $0) } }
        set { defaults.set(newValue?.rawValue, forKey: K.phaseOverride) }
    }
    var reminderEnabled: Bool {
        get { defaults.bool(forKey: K.reminderEnabled) }
        set { defaults.set(newValue, forKey: K.reminderEnabled) }
    }
    var reminderHour: Int {
        get { defaults.object(forKey: K.reminderHour) as? Int ?? ToneRule.defaultReminderHour }
        set { defaults.set(newValue, forKey: K.reminderHour) }
    }
    var reminderMinute: Int {
        get { defaults.object(forKey: K.reminderMinute) as? Int ?? ToneRule.defaultReminderMinute }
        set { defaults.set(newValue, forKey: K.reminderMinute) }
    }
    /// 形象（未上线的形象读出来时退回猫）
    var pet: Pet {
        get {
            let p = Pet(rawValue: defaults.string(forKey: K.pet) ?? "") ?? .cat
            return p.isAvailable ? p : .cat
        }
        set { defaults.set(newValue.rawValue, forKey: K.pet) }
    }
    var onboardingDone: Bool {
        get { defaults.bool(forKey: K.onboarded) }
        set { defaults.set(newValue, forKey: K.onboarded) }
    }

    // MARK: 健康快照

    /// 当前可用的快照（示例模式下直接返回示例数据）。
    /// 各字段按“它属于哪一天”分别判断是否仍有效：
    ///  · 步数只属于它被读取的那一天（北京时间）。过了 0 点一律清空，绝不把昨天的步数当今天的。
    ///  · 入睡时间属于“它结束的那个早上”（18:00 后入睡算第二天的“昨晚”）。只要还是今天的“昨晚”就保留，
    ///    所以 23:30 存下的入睡时间，到 0:30、8:00 依然有效。
    func currentSnapshot(now: Date = Date()) -> HealthSnapshot {
        if useSampleData { return samplePreset.snapshot(now: now) }
        guard let s: HealthSnapshot = load(K.snapshot) else { return .empty(now) }
        return SharedStore.validPart(of: s, now: now)
    }

    /// 只保留在 now 这一天仍然有效的字段
    static func validPart(of s: HealthSnapshot, now: Date) -> HealthSnapshot {
        let today = BJ.dayKey(now)
        var out = HealthSnapshot.empty(now)
        out.fetchedAt = s.fetchedAt
        if s.dayKey == today { out.steps = s.steps }
        if let bed = s.bedtime, SleepRule.nightKey(for: bed) == today {
            out.bedtime = bed
            out.bedtimeSource = s.bedtimeSource
        }
        return out
    }

    /// 把新读到的数据合并进已有快照后保存：新数据缺的字段（比如锁屏时读不到）沿用旧的、且仍属于今天的值。
    @discardableResult
    func mergeAndSave(_ fresh: HealthSnapshot, now: Date = Date()) -> HealthSnapshot {
        let old: HealthSnapshot = load(K.snapshot).map { SharedStore.validPart(of: $0, now: now) } ?? .empty(now)
        let merged = SharedStore.merge(old: old, fresh: fresh, now: now)
        save(merged, K.snapshot)
        return merged
    }

    static func merge(old: HealthSnapshot, fresh: HealthSnapshot, now: Date) -> HealthSnapshot {
        let f = validPart(of: fresh, now: now)
        var m = HealthSnapshot.empty(now)
        m.fetchedAt = fresh.fetchedAt
        // 同一天步数只增不减；新读数缺失时用旧值
        switch (f.steps, old.steps) {
        case let (a?, b?): m.steps = max(a, b)
        case let (a?, nil): m.steps = a
        case let (nil, b): m.steps = b
        }
        if f.bedtime != nil {
            m.bedtime = f.bedtime; m.bedtimeSource = f.bedtimeSource
        } else {
            m.bedtime = old.bedtime; m.bedtimeSource = old.bedtimeSource
        }
        return m
    }

    func saveSnapshot(_ s: HealthSnapshot) { save(s, K.snapshot) }

    // MARK: 每日状态

    func dayState(_ dayKey: String) -> DayState {
        let all: [String: DayState] = load(prefix + K.days) ?? [:]
        return all[dayKey] ?? DayState(dayKey: dayKey)
    }

    func saveDayState(_ st: DayState) {
        var all: [String: DayState] = load(prefix + K.days) ?? [:]
        all[st.dayKey] = st
        // 只保留最近 40 天
        let cutoff = BJ.dayKey(BJ.addDays(-40, to: Date()))
        all = all.filter { $0.key >= cutoff }
        save(all, prefix + K.days)
    }

    /// 最近 n 天的基调，下标 0 = 昨天
    func recentTones(before dayKey: String, days n: Int, now: Date = Date()) -> [Tone?] {
        let all: [String: DayState] = load(prefix + K.days) ?? [:]
        return (1...max(1, n)).map { i in
            let k = BJ.dayKey(BJ.addDays(-i, to: now))
            let t = all[k]?.tone
            return t == .neutral ? nil : t
        }
    }

    // MARK: 用句历史

    var history: [LineUse] {
        get { load(prefix + K.history) ?? [] }
        set {
            let cutoff = BJ.dayKey(BJ.addDays(-40, to: Date()))
            save(newValue.filter { $0.dayKey >= cutoff }, prefix + K.history)
        }
    }

    /// 清空示例模式的历史
    func resetDemoHistory() {
        defaults.removeObject(forKey: "demo." + K.days)
        defaults.removeObject(forKey: "demo." + K.history)
    }

    // MARK: Codable helpers

    private func load<T: Decodable>(_ key: String) -> T? {
        guard let d = defaults.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(T.self, from: d)
    }
    private func save<T: Encodable>(_ v: T, _ key: String) {
        if let d = try? JSONEncoder().encode(v) { defaults.set(d, forKey: key) }
    }
}
