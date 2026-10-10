import Foundation

// ============================================================================
//  ToneRule.swift —— 「什么时候夸、什么时候嫌弃、猫摆什么脸」全部规则都在这一个文件里。
//  想改规则只改这里（数字都是常量），其他文件不用动。
//  当前规则（对应 confirm.md 第 3 节）：
//    · 步数 ≥ 6000 且 23 点前入睡 → 夸
//    · 步数 < 3000 且 1 点后入睡 → 嫌弃
//    · 其他情况 → 一半一半随机
//    · 连续嫌弃 3 天后，第 4 天一定夸一次
//    · 最近 7 天用过的句子不再出现
//  所有时间均为北京时间。
// ============================================================================

enum ToneRule {

    // MARK: - 可调常量

    /// 多少天内不重复同一句（含今天）
    static let noRepeatDays = 7
    /// 连续吐槽多少天后，下一天强制夸
    static let forceEncourageAfterRoastDays = 3
    /// 强制夸是否也覆盖“步数 <3000 且 1 点后”这种必吐槽的日子
    static let forcedEncourageOverridesHardRoast = true
    /// 「其他情况」里夸的概率
    static let encourageProbability = 0.5
    /// 读不到睡眠时，夸的概率（no_sleep_data 句库）
    static let encourageProbabilityWithoutSleep = 0.5

    /// 夸：步数 ≥ 这个值 且 入睡早于 goodBedtime
    static let goodSteps = 6000
    /// 嫌弃：步数 < 这个值 且 入睡晚于 badBedtime
    static let badSteps = 3000

    /// 晚上几点开始给出当天那句旁白（小组件在此之前只显示状态小字）
    static let eveningLineHour = 18

    /// 小组件时间线刷新点（北京时间 时, 分）
    static let timelinePoints: [(Int, Int)] = [(8, 0), (12, 30), (18, 0), (21, 30)]

    /// 小组件读健康失败（锁屏数据加密）时，多少分钟后重试
    static let widgetRetryMinutes = 20
    /// 只在这个时段（北京时间，[开始, 结束) 小时）读失败才提前重试；其他时段等下一个固定时间点
    static let widgetRetryStartHour = 5
    static let widgetRetryEndHour = 12

    static func isRetryWindow(_ date: Date) -> Bool {
        let h = BJ.hourMinute(date).hour
        return h >= widgetRetryStartHour && h < widgetRetryEndHour
    }

    /// 每晚提醒默认时间（北京时间）
    static let defaultReminderHour = 22
    static let defaultReminderMinute = 0

    // MARK: - 分桶（与 roasts.json / encouragements.json 的键一致）

    static let stepBuckets = ["<3000", "3000-6000", "6000-10000", ">10000"]
    static let bedtimeBuckets = ["23点前", "23-1点", "1点后"]

    static func stepBucket(_ steps: Int) -> String {
        switch steps {
        case ..<3000: return "<3000"
        case 3000..<6000: return "3000-6000"
        case 6000...10000: return "6000-10000"
        default: return ">10000"
        }
    }

    /// 入睡时间距当晚 18:00 的分钟数（凌晨入睡算前一晚）
    static func minutesAfterSixPM(_ bedtime: Date) -> Int {
        let hm = BJ.hourMinute(bedtime)
        let m = hm.hour * 60 + hm.minute
        return m >= 18 * 60 ? m - 18 * 60 : m + 6 * 60
    }

    static func bedtimeBucket(_ bedtime: Date) -> String {
        let m = minutesAfterSixPM(bedtime)
        if m < 5 * 60 { return "23点前" }        // 18:00–22:59
        if m < 7 * 60 { return "23-1点" }        // 23:00–00:59
        return "1点后"                            // 01:00–
    }

    // MARK: - 定基调

    /// - Parameters:
    ///   - steps: 今日步数（>0），没步数时不会调用这里
    ///   - bedtime: 昨晚入睡时间，nil = 没睡眠数据
    ///   - recentTones: 最近几天的基调，下标 0 = 昨天，1 = 前天 ……（只含有记录的天）
    static func decideTone(steps: Int, bedtime: Date?, recentTones: [Tone?],
                           random: () -> Double = { Double.random(in: 0..<1) }) -> Tone {
        // 连续吐槽 N 天 → 今天强制夸
        let streak = recentTones.prefix(forceEncourageAfterRoastDays).filter { $0 == .roast }.count
        let forceEncourage = recentTones.count >= forceEncourageAfterRoastDays
            && streak == forceEncourageAfterRoastDays

        guard let bedtime else {
            if forceEncourage { return .encourage }
            return random() < encourageProbabilityWithoutSleep ? .encourage : .roast
        }
        let bucket = bedtimeBucket(bedtime)
        if steps >= goodSteps && bucket == "23点前" { return .encourage }
        if steps < badSteps && bucket == "1点后" {
            return (forceEncourage && forcedEncourageOverridesHardRoast) ? .encourage : .roast
        }
        if forceEncourage { return .encourage }
        return random() < encourageProbability ? .encourage : .roast
    }

    // MARK: - 时段与表情

    static func phase(at date: Date) -> DayPhase {
        let h = BJ.hourMinute(date).hour
        switch h {
        case 5..<12: return .morning
        case 12..<18: return .daytime
        default: return .evening
        }
    }

    /// 早上看睡眠，白天/晚上看步数
    static func mood(for s: HealthSnapshot, phase: DayPhase) -> PetMood {
        switch phase {
        case .morning:
            guard let bed = s.bedtime else { return s.hasSteps ? .proud : .nodata }
            switch bedtimeBucket(bed) {
            case "23点前": return .happy
            case "23-1点": return .sleepy
            default: return .nightowl
            }
        case .daytime:
            guard let steps = s.steps, steps > 0 else { return .nodata }
            if steps >= 5000 { return .happy }
            if steps >= 2500 { return .proud }
            if steps >= 800 { return .disdain }
            return .collapsed
        case .evening:
            guard let steps = s.steps, steps > 0 else { return .nodata }
            if steps > 10000 { return .happy }
            if steps >= goodSteps { return .proud }
            if steps >= badSteps { return .disdain }
            return .collapsed
        }
    }

    /// 旁白出来之前，小组件上显示的一句状态小字
    static func caption(for s: HealthSnapshot, phase: DayPhase) -> String {
        switch phase {
        case .morning:
            if let bed = s.bedtime { return "昨晚 \(BJ.hhmm(bed)) 入睡" }
            return s.hasSteps ? "已走 \(s.stepsText) 步" : "没读到数据"
        case .daytime, .evening:
            if s.hasSteps { return "已走 \(s.stepsText) 步" }
            return "今天还一步没走"
        }
    }
}

// ============================================================================
//  SleepRule —— 怎么从健康的睡眠片段里认出“昨晚几点睡的”（同样都是常量，可直接改）
//  · 窗口：昨天 18:00 – 今天 12:00（北京时间），凌晨入睡算前一晚
//  · 先把相邻片段合并（间隔 < mergeGapMinutes 视为同一段）
//  · 一段只有在「开始时间 ≥ 21:00」或「合并后持续 ≥ minNapProofMinutes」时才算入睡，
//    避免把傍晚沙发上的小盹当成入睡时间
//  · 取符合条件的最早开始时间；先看“睡着”阶段，没有再看“卧床”(inBed)
// ============================================================================

enum SleepRule {
    /// 窗口开始：前一天几点（18 = 18:00）
    static let windowStartHour = 18
    /// 窗口结束：当天几点（12 = 12:00）
    static let windowEndHour = 12
    /// 这个时刻之后开始的片段直接算入睡（21 = 21:00，含凌晨）
    static let earliestBedtimeHour = 21
    /// 早于 earliestBedtimeHour 开始的片段，合并后至少持续这么久才算入睡（分钟）
    static let minNapProofMinutes = 60
    /// 相邻片段间隔小于这个值就合并成一段（分钟）
    static let mergeGapMinutes = 15

    struct Segment {
        var start: Date
        var end: Date
    }

    /// 某个入睡时间属于哪一天的“昨晚”（= 它结束的那个早上的 dayKey）
    static func nightKey(for bedtime: Date) -> String {
        let h = BJ.hourMinute(bedtime).hour
        return h >= windowStartHour ? BJ.dayKey(BJ.addDays(1, to: bedtime)) : BJ.dayKey(bedtime)
    }

    /// 今天这个“昨晚”的窗口
    static func window(for now: Date) -> (start: Date, end: Date) {
        let today = BJ.startOfDay(now)
        return (BJ.time(windowStartHour, 0, on: BJ.addDays(-1, to: today)),
                min(BJ.time(windowEndHour, 0, on: today), now))
    }

    /// 合并相邻片段（间隔 < mergeGapMinutes，或重叠）
    static func merge(_ segments: [Segment]) -> [Segment] {
        let sorted = segments.filter { $0.end > $0.start }.sorted { $0.start < $1.start }
        var out: [Segment] = []
        for s in sorted {
            if var last = out.last, s.start.timeIntervalSince(last.end) < Double(mergeGapMinutes) * 60 {
                last.end = max(last.end, s.end)
                out[out.count - 1] = last
            } else {
                out.append(s)
            }
        }
        return out
    }

    /// 是否算真正入睡（不是傍晚小盹）
    static func qualifies(_ s: Segment) -> Bool {
        let startsLateEnough = ToneRule.minutesAfterSixPM(s.start) >= (earliestBedtimeHour - 18) * 60
        let longEnough = s.end.timeIntervalSince(s.start) >= Double(minNapProofMinutes) * 60
        return startsLateEnough || longEnough
    }

    /// 从一组片段里找入睡时间：只看在窗口内开始的片段，合并后取最早符合条件的开始时间
    static func bedtime(from segments: [Segment], windowStart: Date, windowEnd: Date) -> Date? {
        let inWindow = segments.filter { $0.start >= windowStart && $0.start < windowEnd }
        return merge(inWindow).first(where: qualifies)?.start
    }

    /// 先“睡着”阶段，后“卧床”
    static func bedtime(asleep: [Segment], inBed: [Segment], windowStart: Date, windowEnd: Date) -> (Date, BedtimeSource)? {
        if let d = bedtime(from: asleep, windowStart: windowStart, windowEnd: windowEnd) { return (d, .asleep) }
        if let d = bedtime(from: inBed, windowStart: windowStart, windowEnd: windowEnd) { return (d, .inBed) }
        return nil
    }
}
