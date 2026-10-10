import Foundation

/// 选句引擎：每天定一次基调（ToneRule），从对应桶里挑一句最近 N 天没用过的。
/// App 和小组件共用同一份 App Group 存储，所以两边看到的是同一句。
struct LineEngine {
    var store: SharedStore = .shared
    var library: ContentLibrary = ContentLibrary.shared

    struct Result {
        var text: String
        var line: ChosenLine
    }

    /// 今天的旁白。
    /// - forceNew: 用户点了「换一句」
    func todayLine(snapshot s: HealthSnapshot, now: Date = Date(), forceNew: Bool = false) -> Result {
        guard let steps = s.steps, steps > 0 else {
            let l = ChosenLine(template: Copy.noStepsToday, tone: .neutral, stepBucket: nil, bedtimeBucket: nil)
            return Result(text: Copy.noStepsToday, line: l)
        }
        let key = BJ.dayKey(now)
        var st = store.dayState(key)
        let sb = ToneRule.stepBucket(steps)
        let bb = s.bedtime.map { ToneRule.bedtimeBucket($0) }

        let tone: Tone
        if let t = st.tone, t != .neutral {
            tone = t
        } else {
            tone = ToneRule.decideTone(steps: steps, bedtime: s.bedtime,
                                       recentTones: store.recentTones(before: key, days: ToneRule.forceEncourageAfterRoastDays, now: now))
            st.tone = tone
        }

        if let existing = st.line, !forceNew,
           existing.tone == tone, existing.stepBucket == sb, existing.bedtimeBucket == bb,
           library.candidates(tone: tone, stepBucket: sb, bedtimeBucket: bb).contains(existing.template) {
            store.saveDayState(st)
            return Result(text: ContentLibrary.render(existing.template, steps: steps, bedtime: s.bedtime), line: existing)
        }

        // 数据变了导致桶变化（不是用户主动换），把旧句从今天的历史里撤回
        if let existing = st.line, !forceNew {
            var h = store.history
            if let idx = h.lastIndex(where: { $0.dayKey == key && $0.template == existing.template }) { h.remove(at: idx) }
            store.history = h
        }

        let exclude = [st.line?.template, st.notificationLine?.template].compactMap { $0 }
        let template = pick(tone: tone, stepBucket: sb, bedtimeBucket: bb, now: now, alsoExclude: exclude)
        let chosen = ChosenLine(template: template, tone: tone, stepBucket: sb, bedtimeBucket: bb)
        st.line = chosen
        store.saveDayState(st)
        store.history.append(LineUse(dayKey: key, template: template))
        return Result(text: ContentLibrary.render(template, steps: steps, bedtime: s.bedtime), line: chosen)
    }

    /// 晚间通知用的句子：同一基调，但和小组件当天那句不同
    func notificationLine(snapshot s: HealthSnapshot, now: Date = Date()) -> String {
        let main = todayLine(snapshot: s, now: now)
        guard main.line.tone != .neutral, let steps = s.steps else { return main.text }
        let key = BJ.dayKey(now)
        var st = store.dayState(key)
        let sb = ToneRule.stepBucket(steps)
        let bb = s.bedtime.map { ToneRule.bedtimeBucket($0) }
        if let n = st.notificationLine, n.stepBucket == sb, n.bedtimeBucket == bb, n.template != main.line.template,
           library.candidates(tone: main.line.tone, stepBucket: sb, bedtimeBucket: bb).contains(n.template) {
            return ContentLibrary.render(n.template, steps: steps, bedtime: s.bedtime)
        }
        let template = pick(tone: main.line.tone, stepBucket: sb, bedtimeBucket: bb, now: now,
                            alsoExclude: [main.line.template])
        st.notificationLine = ChosenLine(template: template, tone: main.line.tone, stepBucket: sb, bedtimeBucket: bb)
        store.saveDayState(st)
        store.history.append(LineUse(dayKey: key, template: template))
        return ContentLibrary.render(template, steps: steps, bedtime: s.bedtime)
    }

    /// 从桶里挑一句：排除最近 noRepeatDays 天（含今天）用过的；全用过了就挑最久没用的。
    func pick(tone: Tone, stepBucket: String, bedtimeBucket: String?, now: Date, alsoExclude: [String]) -> String {
        let pool = library.candidates(tone: tone, stepBucket: stepBucket, bedtimeBucket: bedtimeBucket)
        let since = BJ.dayKey(BJ.addDays(-(ToneRule.noRepeatDays - 1), to: now))
        let hist = store.history
        let recent = Set(hist.filter { $0.dayKey >= since }.map { $0.template })
        let excluded = recent.union(alsoExclude)
        let fresh = pool.filter { !excluded.contains($0) }
        if let t = fresh.randomElement() { return t }

        // 全部用过：选最后一次使用最早的（且不是当前这句）
        var lastUsed: [String: String] = [:]
        for u in hist { lastUsed[u.template] = max(lastUsed[u.template] ?? "", u.dayKey) }
        let others = pool.filter { !alsoExclude.contains($0) }
        let candidates = others.isEmpty ? pool : others
        let oldest = candidates.min { (lastUsed[$0] ?? "") < (lastUsed[$1] ?? "") }
        return oldest ?? pool.first ?? Copy.noStepsToday
    }
}
