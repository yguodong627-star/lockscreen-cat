import Foundation

/// 演示用示例数据（设置 → 调试 → 使用示例数据）
enum SamplePreset: String, CaseIterable, Identifiable {
    case great, good, mixed, lazyLate, noSleep, noData
    var id: String { rawValue }

    var title: String {
        switch self {
        case .great: return "走得多·睡得早（12,400 步 / 22:40）"
        case .good: return "还不错（8,230 步 / 00:15）"
        case .mixed: return "一般般（4,560 步 / 00:15）"
        case .lazyLate: return "躺平熬夜（1,820 步 / 01:47）"
        case .noSleep: return "没睡眠记录（8,230 步）"
        case .noData: return "什么都没读到"
        }
    }

    func snapshot(now: Date = Date()) -> HealthSnapshot {
        let today = BJ.startOfDay(now)
        func bed(_ h: Int, _ m: Int) -> Date {
            // h >= 18 属于昨晚（前一天日期），否则是今天凌晨
            let base = h >= 18 ? BJ.addDays(-1, to: today) : today
            return BJ.time(h, m, on: base)
        }
        var s = HealthSnapshot.empty(now)
        s.isSample = true
        switch self {
        case .great: s.steps = 12400; s.bedtime = bed(22, 40)
        case .good: s.steps = 8230; s.bedtime = bed(0, 15)
        case .mixed: s.steps = 4560; s.bedtime = bed(0, 15)
        case .lazyLate: s.steps = 1820; s.bedtime = bed(1, 47)
        case .noSleep: s.steps = 8230
        case .noData: break
        }
        if s.bedtime != nil { s.bedtimeSource = .asleep }
        return s
    }
}
