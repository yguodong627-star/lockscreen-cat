import Foundation
import HealthKit

/// 只读 HealthKit：今日步数 + 昨晚入睡时间。所有时间按北京时间。
final class HealthReader {
    static let shared = HealthReader()
    private let store = HKHealthStore()

    static var isAvailable: Bool { HKHealthStore.isHealthDataAvailable() }

    private var readTypes: Set<HKObjectType> {
        var s = Set<HKObjectType>()
        if let t = HKObjectType.quantityType(forIdentifier: .stepCount) { s.insert(t) }
        if let t = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) { s.insert(t) }
        return s
    }

    /// 弹系统授权（只能在 App 里调用；小组件不能弹窗）
    func requestAuthorization() async -> Bool {
        guard Self.isAvailable else { return false }
        return await withCheckedContinuation { cont in
            store.requestAuthorization(toShare: [], read: readTypes) { ok, _ in
                cont.resume(returning: ok)
            }
        }
    }

    /// 是否已经弹过授权框（不代表用户同意——读权限被拒 HealthKit 不会告诉我们）
    func hasRequestedAuthorization() async -> Bool {
        guard Self.isAvailable else { return false }
        return await withCheckedContinuation { cont in
            store.getRequestStatusForAuthorization(toShare: [], read: readTypes) { status, _ in
                cont.resume(returning: status == .unnecessary)
            }
        }
    }

    /// 读取结果。protectedDataUnavailable = iPhone 锁着、健康数据加密读不到（小组件早上常见）
    struct FetchResult {
        var snapshot: HealthSnapshot
        var protectedDataUnavailable: Bool
    }

    func fetchSnapshot(now: Date = Date()) async -> HealthSnapshot {
        await fetch(now: now).snapshot
    }

    func fetch(now: Date = Date()) async -> FetchResult {
        var snap = HealthSnapshot.empty(now)
        guard Self.isAvailable else { return FetchResult(snapshot: snap, protectedDataUnavailable: false) }
        async let steps = todaySteps(now: now)
        async let bed = lastNightBedtime(now: now)
        let st = await steps
        let b = await bed
        snap.steps = st.value
        if let v = b.value {
            snap.bedtime = v.date
            snap.bedtimeSource = v.source
        }
        snap.fetchedAt = Date()
        return FetchResult(snapshot: snap, protectedDataUnavailable: st.locked || b.locked)
    }

    private static func isLocked(_ error: Error?) -> Bool {
        guard let e = error as? HKError else { return false }
        return e.code == .errorDatabaseInaccessible
    }

    /// 北京时间今天 0 点到现在的步数累计。没有样本 → nil（可能是没授权，也可能真没数据）
    func todaySteps(now: Date = Date()) async -> (value: Int?, locked: Bool) {
        guard let type = HKQuantityType.quantityType(forIdentifier: .stepCount) else { return (nil, false) }
        let start = BJ.startOfDay(now)
        let predicate = HKQuery.predicateForSamples(withStart: start, end: now, options: .strictStartDate)
        return await withCheckedContinuation { cont in
            let q = HKStatisticsQuery(quantityType: type, quantitySamplePredicate: predicate,
                                      options: .cumulativeSum) { _, stats, error in
                if let sum = stats?.sumQuantity() {
                    cont.resume(returning: (Int(sum.doubleValue(for: HKUnit.count()).rounded()), false))
                } else {
                    cont.resume(returning: (nil, HealthReader.isLocked(error)))
                }
            }
            store.execute(q)
        }
    }

    /// 昨晚入睡时间：窗口与过滤规则见 ToneRule.swift 里的 SleepRule。
    /// 优先“睡着”阶段（core/deep/REM/unspecified，iOS 16+ 分阶段），没有再用 inBed
    /// （iPhone「使用 iPhone 追踪卧床时间」或手动记录写入）；都没有 → nil。
    func lastNightBedtime(now: Date = Date()) async -> (value: (date: Date, source: BedtimeSource)?, locked: Bool) {
        guard let type = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else { return (nil, false) }
        let w = SleepRule.window(for: now)
        guard w.end > w.start else { return (nil, false) }
        let predicate = HKQuery.predicateForSamples(withStart: w.start, end: w.end, options: [])
        let sort = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: true)

        let result: ([HKCategorySample], Bool) = await withCheckedContinuation { cont in
            let q = HKSampleQuery(sampleType: type, predicate: predicate, limit: HKObjectQueryNoLimit,
                                  sortDescriptors: [sort]) { _, results, error in
                cont.resume(returning: ((results as? [HKCategorySample]) ?? [], HealthReader.isLocked(error)))
            }
            store.execute(q)
        }
        let samples = result.0

        let asleepValues: Set<Int> = [
            HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue,
            HKCategoryValueSleepAnalysis.asleepCore.rawValue,
            HKCategoryValueSleepAnalysis.asleepDeep.rawValue,
            HKCategoryValueSleepAnalysis.asleepREM.rawValue,
        ]
        let inBedValue = HKCategoryValueSleepAnalysis.inBed.rawValue
        let asleep = samples.filter { asleepValues.contains($0.value) }
            .map { SleepRule.Segment(start: $0.startDate, end: $0.endDate) }
        let inBed = samples.filter { $0.value == inBedValue }
            .map { SleepRule.Segment(start: $0.startDate, end: $0.endDate) }
        if let found = SleepRule.bedtime(asleep: asleep, inBed: inBed, windowStart: w.start, windowEnd: w.end) {
            return ((found.0, found.1), result.1)
        }
        return (nil, result.1)
    }
}
