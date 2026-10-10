import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL

    @State private var reminderOn = SharedStore.shared.reminderEnabled
    @State private var reminderTime = BJ.time(SharedStore.shared.reminderHour, SharedStore.shared.reminderMinute)
    @State private var useSample = SharedStore.shared.useSampleData
    @State private var preset = SharedStore.shared.samplePreset
    @State private var phaseChoice = SharedStore.shared.phaseOverride?.rawValue ?? "auto"
    @State private var notifDenied = false
    @State private var pet = SharedStore.shared.pet

    private var store: SharedStore { model.store }
    private var lib: ContentLibrary { ContentLibrary.forPet(pet) }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    PetPicker(selection: $pet)
                        .onChange(of: pet) { _, v in model.setPet(v) }
                } header: { Text("形象") }

                Section {
                    Toggle("每晚提醒", isOn: $reminderOn)
                        .onChange(of: reminderOn) { _, on in
                            Task {
                                if on {
                                    let ok = await NotificationScheduler.requestPermission()
                                    notifDenied = !ok
                                    store.reminderEnabled = ok
                                    if !ok { reminderOn = false }
                                } else {
                                    store.reminderEnabled = false
                                }
                                await NotificationScheduler.reschedule()
                            }
                        }
                    if reminderOn {
                        DatePicker("提醒时间（北京时间）", selection: $reminderTime, displayedComponents: .hourAndMinute)
                            .environment(\.timeZone, BJ.timeZone)
                            .onChange(of: reminderTime) { _, t in
                                let hm = BJ.hourMinute(t)
                                store.reminderHour = hm.hour
                                store.reminderMinute = hm.minute
                                Task { await NotificationScheduler.reschedule() }
                            }
                    }
                    if notifDenied {
                        Text("通知权限没开。去「设置 > 通知 > \(AppConfig.appDisplayName)」里打开。")
                            .font(.footnote).foregroundStyle(.secondary)
                    }
                } header: { Text("提醒") } footer: { Text("通知标题「\(Copy.notificationTitle)」，正文从当天的句库里另抽一句。") }

                Section("锁屏 / 桌面小组件") {
                    WidgetGuideSteps()
                        .padding(.vertical, 4)
                }

                Section {
                    Button("重新请求健康授权") { Task { await model.requestHealth() } }
                    Button("打开「健康」App") {
                        if let u = URL(string: "x-apple-health://") { openURL(u) }
                    }
                } header: { Text("健康数据") } footer: {
                    Text("只读取步数和睡眠（含 iPhone 记录的卧床时间），不写入，不联网。\n\(Copy.noSleepHint)")
                }

                Section {
                    Toggle("使用示例数据（演示用）", isOn: $useSample)
                        .onChange(of: useSample) { _, v in store.useSampleData = v; model.settingsChanged() }
                    if useSample {
                        Picker("示例", selection: $preset) {
                            ForEach(SamplePreset.allCases) { Text($0.title).tag($0) }
                        }
                        .onChange(of: preset) { _, v in store.samplePreset = v; model.settingsChanged() }
                        Button("清空示例模式的用句历史") { store.resetDemoHistory(); model.settingsChanged() }
                    }
                    Picker("时段", selection: $phaseChoice) {
                        Text("自动（按北京时间）").tag("auto")
                        ForEach(DayPhase.allCases, id: \.rawValue) { Text($0.title).tag($0.rawValue) }
                    }
                    .onChange(of: phaseChoice) { _, v in
                        store.phaseOverride = DayPhase(rawValue: v)
                        model.settingsChanged()
                    }
                } header: { Text("调试") } footer: {
                    Text("示例数据有独立的用句历史，不影响真实记录。时段调试会同时影响小组件。")
                }

                Section("关于") {
                    LabeledContent("吐槽句库", value: "\(count(lib.roast)) + 无睡眠 \(count(lib.roastNoSleep))")
                    LabeledContent("鼓励句库", value: "\(count(lib.encourage)) + 无睡眠 \(count(lib.encourageNoSleep))")
                    if lib.borrowedCatLines {
                        Text("\(pet.displayName)句库还没放进来，暂时借用小猫的句子（“本猫”会换成“本汪”）。").font(.footnote).foregroundStyle(.orange)
                    }
                    if lib.usesPlaceholderEncouragements {
                        Text("鼓励句库缺失，正在使用内置占位句。").font(.footnote).foregroundStyle(.orange)
                    }
                    LabeledContent("不重复天数", value: "\(ToneRule.noRepeatDays) 天")
                    Button("重新看一遍引导") {
                        store.onboardingDone = false
                        model.showOnboarding = true
                        dismiss()
                    }
                }
            }
            .navigationTitle("设置")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) { Button("完成") { dismiss() } }
            }
        }
    }

    private func count(_ g: ContentLibrary.Grid) -> Int { g.values.flatMap { $0.values }.reduce(0) { $0 + $1.count } }
    private func count(_ r: ContentLibrary.Row) -> Int { r.values.reduce(0) { $0 + $1.count } }
}

/// 形象选择（设置页和引导页共用）。未上线的形象显示「即将上线」且不可选。
struct PetPicker: View {
    @Binding var selection: Pet

    var body: some View {
        HStack(spacing: 14) {
            ForEach(Pet.allCases) { p in
                Button {
                    if p.isAvailable { selection = p }
                } label: {
                    VStack(spacing: 6) {
                        ZStack {
                            if p.isAvailable {
                                Image(PetMood.proud.assetName(for: p))
                                    .resizable().scaledToFit()
                            } else {
                                Image(systemName: "pawprint.fill")
                                    .font(.system(size: 34))
                                    .foregroundStyle(Theme.brown.opacity(0.3))
                            }
                        }
                        .frame(width: 84, height: 84)
                        Text(p.displayName).font(.subheadline.bold())
                        if !p.isAvailable {
                            Text("即将上线")
                                .font(.caption2.bold())
                                .padding(.horizontal, 6).padding(.vertical, 2)
                                .background(Capsule().fill(Theme.brown.opacity(0.1)))
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(selection == p ? Theme.deepOrange : Theme.brown.opacity(0.15),
                                    lineWidth: selection == p ? 3 : 1)
                    )
                    .opacity(p.isAvailable ? 1 : 0.55)
                }
                .buttonStyle(.plain)
                .disabled(!p.isAvailable)
                .foregroundStyle(Theme.brown)
            }
        }
        .padding(.vertical, 4)
    }
}
