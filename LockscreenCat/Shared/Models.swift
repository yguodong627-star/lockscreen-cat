import Foundation

/// 入睡时间的来源：优先 Apple Watch 等写入的“睡着”阶段，其次 iPhone“追踪卧床时间”写入的 inBed。
enum BedtimeSource: String, Codable {
    case asleep
    case inBed
}

/// App 读到的健康数据快照，写进 App Group 给小组件用。
struct HealthSnapshot: Codable, Equatable {
    /// 今日步数（北京时间 0 点起）；nil = 没数据（也可能是没授权，HealthKit 不告诉我们）
    var steps: Int?
    /// 昨晚入睡时间；nil = 没睡眠数据
    var bedtime: Date?
    var bedtimeSource: BedtimeSource?
    /// 这份数据属于哪一天（北京时间 dayKey）
    var dayKey: String
    var fetchedAt: Date
    var isSample: Bool = false

    static func empty(_ now: Date = Date()) -> HealthSnapshot {
        HealthSnapshot(steps: nil, bedtime: nil, bedtimeSource: nil, dayKey: BJ.dayKey(now), fetchedAt: now)
    }

    var hasSteps: Bool { (steps ?? 0) > 0 }
    var hasSleep: Bool { bedtime != nil }
    var hasAnyData: Bool { hasSteps || hasSleep }

    var stepsText: String { steps.map { BJ.steps($0) } ?? "--" }
    var bedtimeText: String { bedtime.map { BJ.hhmm($0) } ?? "--:--" }
}

enum Tone: String, Codable {
    case roast        // 吐槽
    case encourage    // 鼓励
    case neutral      // 没步数时的固定文案，不计入连续吐槽
}

/// 一天中的时段（北京时间）
enum DayPhase: String, Codable, CaseIterable {
    case morning   // 05:00–11:59 看睡眠
    case daytime   // 12:00–17:59 看步数
    case evening   // 18:00–04:59 看步数 + 当晚旁白

    var title: String {
        switch self {
        case .morning: return "早上"
        case .daytime: return "白天"
        case .evening: return "晚上"
        }
    }
}

/// 表情。素材名 = "<形象>-<表情>"，例如 cat-happy / dog-happy（单色版加 -mono）
enum PetMood: String, Codable, CaseIterable {
    case happy, proud, disdain, collapsed, sleepy, nightowl, nodata

    func assetName(for pet: Pet) -> String { "\(pet.artPet.rawValue)-\(rawValue)" }
    func monoAssetName(for pet: Pet) -> String { "\(pet.artPet.rawValue)-\(rawValue)-mono" }

    var title: String {
        switch self {
        case .happy: return "开心得意"
        case .proud: return "嘴上不说·尾巴翘起"
        case .disdain: return "嫌弃"
        case .collapsed: return "瘫倒"
        case .sleepy: return "困"
        case .nightowl: return "熬夜黑眼圈"
        case .nodata: return "没读到数据"
        }
    }
}

/// 某天定下来的一句话（存的是模板，显示时用当前数据替换占位符）
struct ChosenLine: Codable, Equatable {
    var template: String
    var tone: Tone
    var stepBucket: String?
    var bedtimeBucket: String?   // nil = no_sleep_data 句库 / 固定文案
}

/// 每天的状态
struct DayState: Codable, Equatable {
    var dayKey: String
    var tone: Tone?
    var line: ChosenLine?
    var notificationLine: ChosenLine?
}

/// 历史记录：用于“N 天内不重复”与“连续吐槽天数”
struct LineUse: Codable, Equatable {
    var dayKey: String
    var template: String
}
