import WidgetKit
import SwiftUI
import UIKit

@main
struct LockscreenCatWidgetBundle: WidgetBundle {
    var body: some Widget {
        LockscreenCatWidget()
    }
}

struct PetEntry: TimelineEntry {
    let date: Date
    let state: PetState
}

struct PetProvider: TimelineProvider {
    /// HealthKit 最多等这么久（秒）；超时就用 App 写进 App Group 的快照
    static let healthTimeout: TimeInterval = 6
    /// 整个 getTimeline 的兜底时限（秒）：无论发生什么都在这之前交出时间线，避免系统一直显示灰色占位块
    static let timelineDeadline: TimeInterval = 12

    func placeholder(in context: Context) -> PetEntry {
        let now = Date()
        var st = PetState.make(at: now, snapshot: SamplePreset.good.snapshot(now: now), persistLine: false)
        st.line = st.pet.voiceForBorrowedLine("8,230 步，腿今天很争气，本猫勉强鼓掌。")
        st.tone = .encourage
        return PetEntry(date: now, state: st)
    }

    func getSnapshot(in context: Context, completion: @escaping (PetEntry) -> Void) {
        if context.isPreview {
            completion(placeholder(in: context))
            return
        }
        let now = Date()
        completion(PetEntry(date: now, state: PetState.make(at: now)))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<PetEntry>) -> Void) {
        let done = OnceCompletion(completion)

        // 兜底：HealthKit 卡住或别的意外，到点直接用已存的快照交一份时间线
        DispatchQueue.global(qos: .utility).asyncAfter(deadline: .now() + Self.timelineDeadline) {
            guard !done.isDone else { return }
            let now = Date()
            done.call(Self.makeTimeline(now: now, snap: SharedStore.shared.currentSnapshot(now: now), needsRetry: true))
        }

        Task {
            let store = SharedStore.shared
            let now = Date()
            var snap = store.currentSnapshot(now: now)
            var needsRetry = false

            // 小组件不能弹授权，但如果 App 已经授权过，可以自己读一次最新数据（最多等 healthTimeout 秒）。
            // iPhone 锁着时健康数据是加密的、读不到：保留上次的快照（步数仍按北京时间当天、入睡时间按所属的“昨晚”判断）。
            // 早上（05:00–12:00）读失败会在 widgetRetryMinutes 分钟后重试，解锁后很快就能看到昨晚的睡眠。
            if !store.useSampleData && HealthReader.isAvailable {
                if let r = await Self.fetchHealth(now: now, timeout: Self.healthTimeout) {
                    snap = store.mergeAndSave(r.snapshot, now: now)
                    let failed = r.protectedDataUnavailable || !r.snapshot.hasAnyData
                    needsRetry = failed && ToneRule.isRetryWindow(now)
                } else {
                    needsRetry = ToneRule.isRetryWindow(now)   // 超时：用旧快照，早上稍后重试
                }
            }
            done.call(Self.makeTimeline(now: now, snap: snap, needsRetry: needsRetry))
        }
    }

    /// 生成时间线：现在 + 今天剩下的固定时间点（北京时间 08:00 / 12:30 / 18:00 / 21:30），最多 5 条。
    /// 每条只是几个字符串和数字，图片按名字引用（小组件自己的小图），内存很小。
    static func makeTimeline(now: Date, snap: HealthSnapshot, needsRetry: Bool) -> Timeline<PetEntry> {
        var entries = [PetEntry(date: now, state: PetState.make(at: now, snapshot: snap))]
        let points = ToneRule.timelinePoints
            .map { BJ.time($0.0, $0.1, on: now) }
            .filter { $0 > now }
        for t in points {
            entries.append(PetEntry(date: t, state: PetState.make(at: t, snapshot: snap, persistLine: false)))
        }
        // 到下一个时间点就重新生成（届时会读最新数据、到晚上会定下当天那句）；读失败则 retryMinutes 后重试
        let tomorrowFirst = BJ.time(ToneRule.timelinePoints[0].0, ToneRule.timelinePoints[0].1,
                                    on: BJ.addDays(1, to: now))
        var next = points.first ?? tomorrowFirst
        if needsRetry {
            next = min(next, now.addingTimeInterval(Double(ToneRule.widgetRetryMinutes) * 60))
        }
        return Timeline(entries: entries, policy: .after(next))
    }

    /// 带超时的 HealthKit 读取；超时返回 nil（HealthKit 的回调晚到也不会重复 resume）
    static func fetchHealth(now: Date, timeout: TimeInterval) async -> HealthReader.FetchResult? {
        await withCheckedContinuation { (cont: CheckedContinuation<HealthReader.FetchResult?, Never>) in
            let once = OnceFlag()
            Task {
                let r = await HealthReader.shared.fetch(now: now)
                if once.claim() { cont.resume(returning: r) }
            }
            DispatchQueue.global(qos: .utility).asyncAfter(deadline: .now() + timeout) {
                if once.claim() { cont.resume(returning: nil) }
            }
        }
    }
}

/// 线程安全的“只执行一次”标记
final class OnceFlag: @unchecked Sendable {
    private let lock = NSLock()
    private var claimed = false
    var isClaimed: Bool { lock.lock(); defer { lock.unlock() }; return claimed }
    /// 第一次调用返回 true，之后都返回 false
    func claim() -> Bool {
        lock.lock(); defer { lock.unlock() }
        if claimed { return false }
        claimed = true
        return true
    }
}

/// 保证 WidgetKit 的 completion 恰好调用一次
final class OnceCompletion<T>: @unchecked Sendable {
    private let flag = OnceFlag()
    private let body: (T) -> Void
    init(_ body: @escaping (T) -> Void) { self.body = body }
    var isDone: Bool { flag.isClaimed }
    func call(_ value: T) { if flag.claim() { body(value) } }
}

struct LockscreenCatWidget: Widget {
    var body: some WidgetConfiguration {
        StaticConfiguration(kind: AppConfig.widgetKind, provider: PetProvider()) { entry in
            PetWidgetView(entry: entry)
        }
        .configurationDisplayName(AppConfig.appDisplayName)
        .description("看你的步数和睡眠，嫌弃你，也鼓励你。")
        .supportedFamilies([.systemSmall, .systemMedium, .accessoryRectangular, .accessoryCircular])
    }
}

// MARK: - Views

private enum WTheme {
    static let cream = Color(red: 1.0, green: 0.973, blue: 0.933)
    static let brown = Color(red: 0.290, green: 0.173, blue: 0.114)
    static let orange = Color(red: 0.851, green: 0.455, blue: 0.165)
    static let green = Color(red: 0.36, green: 0.62, blue: 0.40)
}

struct PetWidgetView: View {
    let entry: PetEntry
    @Environment(\.widgetFamily) private var family
    @Environment(\.widgetRenderingMode) private var renderingMode

    private var s: PetState { entry.state }
    private var text: String { s.line ?? s.caption }

    var body: some View {
        content
            .containerBackground(for: .widget) {
                if renderingMode == .fullColor && !family.isAccessory {
                    WTheme.cream
                } else {
                    Color.clear
                }
            }
    }

    @ViewBuilder private var content: some View {
        switch family {
        case .accessoryCircular:
            ZStack {
                AccessoryWidgetBackground()
                catImage(mono: true).padding(3)
            }
        case .accessoryRectangular:
            HStack(spacing: 6) {
                catImage(mono: true)
                    .frame(width: 46, height: 46)
                VStack(alignment: .leading, spacing: 1) {
                    Text(text)
                        .font(.system(size: 13, weight: .semibold))
                        .lineLimit(3)
                        .minimumScaleFactor(0.8)
                        .widgetAccentable()
                }
                Spacer(minLength: 0)
            }
        case .systemMedium:
            HStack(spacing: 12) {
                catImage(mono: renderingMode != .fullColor)
                    .frame(width: 128, height: 128)
                VStack(alignment: .leading, spacing: 8) {
                    if let badge = badge {
                        Text(badge)
                            .font(.caption2.bold())
                            .foregroundStyle(s.tone == .encourage ? WTheme.green : WTheme.orange)
                    }
                    Text(text)
                        .font(.system(size: 15, weight: .semibold))
                        .foregroundStyle(WTheme.brown)
                        .lineLimit(4)
                        .minimumScaleFactor(0.85)
                    Spacer(minLength: 0)
                    HStack(spacing: 10) {
                        Label(s.snapshot.stepsText, systemImage: "figure.walk")
                        Label(s.snapshot.bedtimeText, systemImage: "moon.zzz.fill")
                    }
                    .font(.caption2.weight(.medium))
                    .foregroundStyle(WTheme.brown.opacity(0.65))
                }
                Spacer(minLength: 0)
            }
        default: // systemSmall
            VStack(spacing: 4) {
                catImage(mono: renderingMode != .fullColor)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                Text(text)
                    .font(.system(size: 11, weight: .semibold))
                    .foregroundStyle(WTheme.brown)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
                    .minimumScaleFactor(0.8)
            }
        }
    }

    private var badge: String? {
        switch s.tone {
        case .roast?: return "今日吐槽"
        case .encourage?: return "今日鼓励"
        default: return nil
        }
    }

    /// 图片来自小组件自己的 Widget/WidgetAssets.xcassets（66pt / 128pt 的小图，不是 App 的 1024px 原图）。
    /// 万一某张图没打进小组件，退回系统图标，而不是空白或崩溃。
    @ViewBuilder private func catImage(mono: Bool) -> some View {
        let name = mono ? s.monoAssetName : s.assetName
        if UIImage(named: name) == nil {
            Image(systemName: "pawprint.fill")
                .resizable()
                .scaledToFit()
                .padding(6)
                .foregroundStyle(mono ? Color.primary : WTheme.orange)
                .widgetAccentable()
        } else if mono {
            Image(name)
                .renderingMode(.template)
                .resizable()
                .scaledToFit()
                .widgetAccentable()
        } else {
            Image(name)
                .resizable()
                .scaledToFit()
        }
    }
}

private extension WidgetFamily {
    var isAccessory: Bool {
        switch self {
        case .accessoryCircular, .accessoryRectangular, .accessoryInline: return true
        default: return false
        }
    }
}
