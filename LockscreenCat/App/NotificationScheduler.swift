import Foundation
import UserNotifications

/// 每晚本地提醒（UNUserNotificationCenter，不需要推送证书，免费账号可用）。
/// 本地通知内容必须提前写好：当天那条用当天数据选句（与小组件那句不同）；
/// 之后几天先排一条通用文案，App 每次打开/后台刷新都会用最新数据重排。
enum NotificationScheduler {
    static let idPrefix = "evening-"
    /// 往后排几天（没打开 App 的日子也能收到提醒）
    static let daysAhead = 7
    /// 未来几天（还没有数据时）的通知正文
    static let genericBody = "今天的旁白写好了，点开看看猫怎么说你。"

    static func requestPermission() async -> Bool {
        (try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])) ?? false
    }

    static func reschedule() async {
        let center = UNUserNotificationCenter.current()
        let pending = await center.pendingNotificationRequests()
        center.removePendingNotificationRequests(withIdentifiers: pending.map(\.identifier).filter { $0.hasPrefix(idPrefix) })

        let store = SharedStore.shared
        guard store.reminderEnabled else { return }
        let settings = await center.notificationSettings()
        guard settings.authorizationStatus == .authorized || settings.authorizationStatus == .provisional else { return }

        let now = Date()
        let today = BJ.startOfDay(now)
        for i in 0..<daysAhead {
            let day = BJ.addDays(i, to: today)
            let fire = BJ.time(store.reminderHour, store.reminderMinute, on: day)
            guard fire > now else { continue }

            let content = UNMutableNotificationContent()
            content.title = Copy.notificationTitle
            if i == 0 {
                let snap = store.currentSnapshot(now: now)
                content.body = snap.hasSteps
                    ? LineEngine(store: store, library: ContentLibrary.forPet(store.pet)).notificationLine(snapshot: snap, now: now)
                    : genericBody
            } else {
                content.body = genericBody
            }
            content.sound = .default

            var comps = BJ.calendar.dateComponents([.year, .month, .day, .hour, .minute], from: fire)
            comps.calendar = BJ.calendar
            comps.timeZone = BJ.timeZone
            let trigger = UNCalendarNotificationTrigger(dateMatching: comps, repeats: false)
            let req = UNNotificationRequest(identifier: idPrefix + BJ.dayKey(day), content: content, trigger: trigger)
            try? await center.add(req)
        }
    }
}
