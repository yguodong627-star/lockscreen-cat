import Foundation

/// 某一时刻萌宠的完整状态（App 和小组件都用它来画界面）
struct PetState {
    var date: Date
    var pet: Pet
    var snapshot: HealthSnapshot
    var phase: DayPhase
    var mood: PetMood
    /// 状态小字（例如“已走 4,560 步”）
    var caption: String
    /// 当天旁白；18:00 前且还没生成过时为 nil
    var line: String?
    var tone: Tone?

    var bedtimeHint: String? { snapshot.hasSteps && !snapshot.hasSleep ? Copy.noSleepHint : nil }

    var assetName: String { mood.assetName(for: pet) }
    var monoAssetName: String { mood.monoAssetName(for: pet) }

    /// - wantLine: true = 即使还没到晚上也生成/取出旁白（App 里点了按钮、示例模式等）
    /// - persistLine: false = 只读已有旁白，不新选（小组件为未来时间点预排时用）
    static func make(at date: Date = Date(), snapshot: HealthSnapshot? = nil,
                     store: SharedStore = .shared, wantLine: Bool = false, persistLine: Bool = true) -> PetState {
        let snap = snapshot ?? store.currentSnapshot(now: date)
        let pet = store.pet
        let phase = store.phaseOverride ?? ToneRule.phase(at: date)
        let mood = ToneRule.mood(for: snap, phase: phase)
        let caption = ToneRule.caption(for: snap, phase: phase)

        var line: String?
        var tone: Tone?
        let hour = BJ.hourMinute(date).hour
        let isEveningTime = phase == .evening || hour >= ToneRule.eveningLineHour
        let existing = store.dayState(BJ.dayKey(date)).line
        if !snap.hasSteps {
            if isEveningTime || wantLine { line = Copy.noStepsToday; tone = .neutral }
        } else if persistLine && (isEveningTime || wantLine || existing != nil) {
            let r = LineEngine(store: store, library: ContentLibrary.forPet(store.pet)).todayLine(snapshot: snap, now: date)
            line = r.text
            tone = r.line.tone
        } else if let e = existing {
            line = ContentLibrary.render(e.template, steps: snap.steps, bedtime: snap.bedtime)
            tone = e.tone
        }
        return PetState(date: date, pet: pet, snapshot: snap, phase: phase, mood: mood, caption: caption, line: line, tone: tone)
    }
}
