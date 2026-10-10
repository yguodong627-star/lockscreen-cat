import SwiftUI
import UIKit
import BackgroundTasks
import WidgetKit

@main
struct LockscreenCatApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @StateObject private var model = AppModel()
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(model)
                .onChange(of: scenePhase) { _, phase in
                    if phase == .active {
                        Task { await model.refresh() }
                    } else if phase == .background {
                        BackgroundRefresh.schedule()
                    }
                }
                .task { await model.refresh() }
                // 解锁后（健康数据解密可读）立刻重读一次，并刷新小组件
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.protectedDataDidBecomeAvailableNotification)) { _ in
                    Task { await model.refresh() }
                }
        }
    }
}

final class AppDelegate: NSObject, UIApplicationDelegate {
    /// App 在后台存活时（例如后台刷新刚跑完）用户解锁，也顺手刷新一次
    func applicationProtectedDataDidBecomeAvailable(_ application: UIApplication) {
        Task { await AppModel.backgroundUpdate() }
    }

    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        BackgroundRefresh.register()
        return true
    }
}

/// BGAppRefreshTask：尽力而为，系统决定什么时候跑（可能很久不跑）。
enum BackgroundRefresh {
    static func register() {
        BGTaskScheduler.shared.register(forTaskWithIdentifier: AppConfig.refreshTaskID, using: nil) { task in
            guard let task = task as? BGAppRefreshTask else { task.setTaskCompleted(success: false); return }
            schedule()
            let work = Task {
                await AppModel.backgroundUpdate()
                task.setTaskCompleted(success: true)
            }
            task.expirationHandler = { work.cancel() }
        }
    }

    static func schedule() {
        let req = BGAppRefreshTaskRequest(identifier: AppConfig.refreshTaskID)
        req.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60)
        try? BGTaskScheduler.shared.submit(req)
    }
}

struct RootView: View {
    @EnvironmentObject var model: AppModel
    var body: some View {
        Group {
            if model.showOnboarding {
                OnboardingView()
            } else {
                ContentView()
            }
        }
        .animation(.easeInOut, value: model.showOnboarding)
    }
}
