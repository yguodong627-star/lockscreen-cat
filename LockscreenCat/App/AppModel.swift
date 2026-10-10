import SwiftUI
import WidgetKit

@MainActor
final class AppModel: ObservableObject {
    @Published var state: PetState
    @Published var showOnboarding: Bool
    @Published var isLoading = false
    @Published var healthRequested = false

    let store = SharedStore.shared

    init() {
        state = PetState.make()
        showOnboarding = !SharedStore.shared.onboardingDone
    }

    var useSample: Bool { store.useSampleData }

    /// 读健康 → 写 App Group 快照 → 刷新界面 / 小组件 / 晚间提醒
    func refresh() async {
        isLoading = true
        defer { isLoading = false }
        if !store.useSampleData {
            healthRequested = await HealthReader.shared.hasRequestedAuthorization()
            if healthRequested {
                let r = await HealthReader.shared.fetch()
                // 合并保存：锁屏/读失败时缺的字段沿用旧快照里仍属于今天的值
                store.mergeAndSave(r.snapshot)
            }
        }
        rebuild()
        WidgetCenter.shared.reloadAllTimelines()
        await NotificationScheduler.reschedule()
    }

    func rebuild(wantLine: Bool = false) {
        state = PetState.make(wantLine: wantLine || state.line != nil)
    }

    /// 「让猫先说一句」（18:00 前提前生成）
    func revealLine() {
        rebuild(wantLine: true)
        WidgetCenter.shared.reloadAllTimelines()
    }

    /// 「换一句」：同一基调里换一句最近 7 天没用过的
    func shuffleLine() {
        let snap = store.currentSnapshot()
        guard snap.hasSteps else { rebuild(wantLine: true); return }
        _ = LineEngine(store: store, library: ContentLibrary.forPet(store.pet)).todayLine(snapshot: snap, forceNew: true)
        rebuild(wantLine: true)
        WidgetCenter.shared.reloadAllTimelines()
        Task { await NotificationScheduler.reschedule() }
    }

    func requestHealth() async {
        _ = await HealthReader.shared.requestAuthorization()
        await refresh()
    }

    func finishOnboarding() {
        store.onboardingDone = true
        showOnboarding = false
        Task { await refresh() }
    }

    /// 切换形象（未上线的形象会被忽略）
    func setPet(_ pet: Pet) {
        guard pet.isAvailable else { return }
        store.pet = pet
        settingsChanged()
    }

    func settingsChanged() {
        rebuild()
        WidgetCenter.shared.reloadAllTimelines()
        Task { await NotificationScheduler.reschedule() }
    }

    /// 后台刷新（BGAppRefreshTask）
    nonisolated static func backgroundUpdate() async {
        let store = SharedStore.shared
        if !store.useSampleData {
            let r = await HealthReader.shared.fetch()
            // 锁屏时 HealthKit 数据受保护读不到：合并保存，不会用空数据覆盖已有值
            store.mergeAndSave(r.snapshot)
        }
        WidgetCenter.shared.reloadAllTimelines()
        await NotificationScheduler.reschedule()
    }
}
