import Foundation
let base = "/workspace/lockscreen-cat/ios/LockscreenCat/Shared/Content/"
let lib0 = ContentLibrary.load(roastsData: FileManager.default.contents(atPath: base+"roasts.json"),
                              encouragementsData: FileManager.default.contents(atPath: base+"encouragements.json"))
let lib = lib0
func cnt(_ g: ContentLibrary.Grid) -> Int { g.values.flatMap{$0.values}.reduce(0){$0+$1.count} }
print("roast", cnt(lib.roast), "enc", cnt(lib.encourage), "roastNS", lib.roastNoSleep.values.reduce(0){$0+$1.count}, "encNS", lib.encourageNoSleep.values.reduce(0){$0+$1.count}, "placeholder", lib.usesPlaceholderEncouragements)
precondition(BJ.steps(8230) == "8,230" && BJ.steps(12400) == "12,400" && BJ.steps(900) == "900")
// bedtime buckets
let today = BJ.startOfDay(Date())
let y = BJ.addDays(-1, to: today)
for (d, exp) in [(BJ.time(22,59,on:y),"23点前"),(BJ.time(23,0,on:y),"23-1点"),(BJ.time(0,59,on:today),"23-1点"),(BJ.time(1,0,on:today),"1点后"),(BJ.time(18,30,on:y),"23点前")] {
  precondition(ToneRule.bedtimeBucket(d) == exp, "\(BJ.hhmm(d)) -> \(ToneRule.bedtimeBucket(d))")
}
precondition(ToneRule.stepBucket(2999)=="<3000" && ToneRule.stepBucket(3000)=="3000-6000" && ToneRule.stepBucket(6000)=="6000-10000" && ToneRule.stepBucket(10001)==">10000")
// tone rule
let early = BJ.time(22,40,on:y), late = BJ.time(1,47,on:today), mid = BJ.time(0,15,on:today)
precondition(ToneRule.decideTone(steps: 8000, bedtime: early, recentTones: [nil,nil,nil]) == .encourage)
precondition(ToneRule.decideTone(steps: 1000, bedtime: late, recentTones: [nil,nil,nil]) == .roast)
precondition(ToneRule.decideTone(steps: 1000, bedtime: late, recentTones: [.roast,.roast,.roast]) == .encourage)
precondition(ToneRule.decideTone(steps: 4000, bedtime: mid, recentTones: [.roast,.roast,.roast], random: {0.99}) == .encourage)
precondition(ToneRule.decideTone(steps: 4000, bedtime: mid, recentTones: [.roast,nil,.roast], random: {0.99}) == .roast)
precondition(ToneRule.decideTone(steps: 4000, bedtime: mid, recentTones: [nil,nil,nil], random: {0.1}) == .encourage)
// simulate 40 days with store
let ud = UserDefaults(suiteName: "logictest")!; ud.removePersistentDomain(forName: "logictest")
let store = SharedStore(defaults: ud)
let engine = LineEngine(store: store, library: lib)
var roastStreak = 0, maxStreak = 0
var used: [(Int,String)] = []
for day in 0..<60 {
  let now = BJ.time(21, 30, on: BJ.addDays(day, to: today))
  var s = HealthSnapshot.empty(now)
  s.steps = [1200, 4560, 2500, 8230][day % 4] ; s.bedtime = BJ.time(1, 47, on: BJ.startOfDay(now))
  if day % 7 == 6 { s.bedtime = nil }
  let r = engine.todayLine(snapshot: s, now: now)
  let r2 = engine.todayLine(snapshot: s, now: now) // stable
  precondition(r.text == r2.text)
  let sh = engine.todayLine(snapshot: s, now: now, forceNew: true)
  precondition(sh.line.template != r.line.template && sh.line.tone == r.line.tone)
  let n = engine.notificationLine(snapshot: s, now: now)
  precondition(n != sh.text)
  for t in [r.line.template, sh.line.template] { 
    if let prev = used.last(where: {$0.1 == t}) { precondition(day - prev.0 >= ToneRule.noRepeatDays, "repeat within window \(t)") }
    used.append((day, t)) }
  if r.line.tone == .roast { roastStreak += 1; maxStreak = max(maxStreak, roastStreak) } else { roastStreak = 0 }
  if day < 8 { print(day, r.line.tone, "|", r.text, "|", sh.text, "| 通知:", n) }
  precondition(!r.text.contains("{"))
}
print("max roast streak", maxStreak)
precondition(maxStreak <= 3)
// PetState
let st = PetState.make(at: BJ.time(8,0,on:today), snapshot: SamplePreset.lazyLate.snapshot(now: BJ.time(8,0,on:today)), store: store, persistLine: false)
print("morning mood", st.mood, st.caption, st.line ?? "nil")

// ---------- 睡眠：傍晚小盹过滤 ----------
func seg(_ d: Date, _ h: Int, _ m: Int, _ mins: Int) -> SleepRule.Segment { let s = BJ.time(h, m, on: d); return .init(start: s, end: s.addingTimeInterval(Double(mins)*60)) }
let now9 = BJ.time(9, 0, on: today); let w = SleepRule.window(for: now9)
// 19:10 打盹 40 分钟（不算）+ 23:20 入睡
var b = SleepRule.bedtime(from: [seg(y,19,10,40), seg(y,23,20,300)], windowStart: w.start, windowEnd: w.end)
precondition(b.map(BJ.hhmm) == "23:20", "nap \(String(describing: b))")
// 19:00 三段 25 分钟、间隔 10 分钟 → 合并 95 分钟 ≥ 60，算入睡
b = SleepRule.bedtime(from: [seg(y,19,0,25), seg(y,19,35,25), seg(y,20,10,25), seg(y,23,50,200)], windowStart: w.start, windowEnd: w.end)
precondition(b.map(BJ.hhmm) == "19:00", "merge \(String(describing: b))")
// 间隔 20 分钟不合并：19:00 25min + 19:45 25min 都不够 → 取 22:30
b = SleepRule.bedtime(from: [seg(y,19,0,25), seg(y,19,45,25), seg(y,22,30,30)], windowStart: w.start, windowEnd: w.end)
precondition(b.map(BJ.hhmm) == "22:30", "gap \(String(describing: b))")
// 21:00 整开始的短片段也算（≥21:00）
b = SleepRule.bedtime(from: [seg(y,21,0,10)], windowStart: w.start, windowEnd: w.end)
precondition(b.map(BJ.hhmm) == "21:00")
// 20:59 开始 50 分钟不算，凌晨 1:10 算
b = SleepRule.bedtime(from: [seg(y,20,59,50), seg(today,1,10,30)], windowStart: w.start, windowEnd: w.end)
precondition(b.map(BJ.hhmm) == "01:10")
// 窗口外（17:30 开始）不看
b = SleepRule.bedtime(from: [seg(y,17,30,300)], windowStart: w.start, windowEnd: w.end)
precondition(b == nil)
// 睡着阶段只有小盹 → 用 inBed
let both = SleepRule.bedtime(asleep: [seg(y,19,30,20)], inBed: [seg(y,22,45,480)], windowStart: w.start, windowEnd: w.end)
precondition(both.map { BJ.hhmm($0.0) } == "22:45" && both?.1 == .inBed)
print("nap filtering OK")

// ---------- 快照保留 ----------
let ud2 = UserDefaults(suiteName: "logictest2")!; ud2.removePersistentDomain(forName: "logictest2")
let st2 = SharedStore(defaults: ud2)
let d0 = BJ.addDays(-3, to: today), d1 = BJ.addDays(1, to: d0)
// d0 23:40 读到：今天 9,123 步，昨晚(d0 凌晨) 00:15 入睡
var f = HealthSnapshot.empty(BJ.time(23, 40, on: d0)); f.steps = 9123; f.bedtime = BJ.time(0, 15, on: d0); f.bedtimeSource = .asleep
st2.mergeAndSave(f, now: BJ.time(23, 40, on: d0))
var c = st2.currentSnapshot(now: BJ.time(23, 50, on: d0)); precondition(c.steps == 9123 && c.bedtime != nil)
// 过 0 点（d1 00:05）：步数必须清空（不能显示昨天的 9,123）；d0 凌晨的入睡属于上一晚，也过期
c = st2.currentSnapshot(now: BJ.time(0, 5, on: d1))
precondition(c.steps == nil, "steps must reset after midnight"); precondition(c.bedtime == nil); precondition(c.stepsText == "--")
// d1 00:40 手机还没锁时读到：d0 23:10 入睡、今天 35 步
var f2 = HealthSnapshot.empty(BJ.time(0, 40, on: d1)); f2.steps = 35; f2.bedtime = BJ.time(23, 10, on: d0); f2.bedtimeSource = .asleep
st2.mergeAndSave(f2, now: BJ.time(0, 40, on: d1))
// 旧快照里的“昨天的步数”合并也不会混进来
precondition(SharedStore.merge(old: SharedStore.validPart(of: f, now: BJ.time(0, 40, on: d1)), fresh: HealthSnapshot.empty(BJ.time(0, 40, on: d1)), now: BJ.time(0, 40, on: d1)).steps == nil)
// 08:00 锁屏读失败（全空）合并后：入睡保留、步数是今天的 35（不是昨天的 9,123）
var lockedRead = HealthSnapshot.empty(BJ.time(8, 0, on: d1))
c = st2.mergeAndSave(lockedRead, now: BJ.time(8, 0, on: d1))
precondition(c.steps == 35 && c.bedtime.map(BJ.hhmm) == "23:10")
precondition(ToneRule.mood(for: c, phase: .morning) == .sleepy, "morning should not be nodata")
// 解锁后读到 1,200 步（入睡读不到也保留旧的）
var unlocked = HealthSnapshot.empty(BJ.time(8, 30, on: d1)); unlocked.steps = 1200
c = st2.mergeAndSave(unlocked, now: BJ.time(8, 30, on: d1)); precondition(c.steps == 1200 && c.bedtime != nil)
// 之后锁屏读失败：步数不回退
c = st2.mergeAndSave(HealthSnapshot.empty(BJ.time(9, 0, on: d1)), now: BJ.time(9, 0, on: d1)); precondition(c.steps == 1200)
// 再过一天：入睡（属于 d1 的昨晚）也过期
c = st2.currentSnapshot(now: BJ.time(8, 0, on: BJ.addDays(1, to: d1))); precondition(c.steps == nil && c.bedtime == nil)
// 凌晨 1:30 入睡属于当天早上
precondition(SleepRule.nightKey(for: BJ.time(1, 30, on: d1)) == BJ.dayKey(d1))
precondition(SleepRule.nightKey(for: BJ.time(22, 0, on: d0)) == BJ.dayKey(d1))
print("snapshot retention OK")

// ---------- 形象 ----------
precondition(Pet.dog.fill("今天你还一步没走，{pet}也懒得说你。") == "今天你还一步没走，小狗也懒得说你。")
precondition(Pet.cat.fill("{pet}有话说") == "小猫有话说" && Pet.dog.fill("{pet}有话说") == "小狗有话说")
precondition(Pet.cat.fill("来自我的锁屏萌宠") == "来自我的锁屏萌宠")
precondition(Pet.dog.voiceForBorrowedLine("猫粮碗都替你尴尬，本猫无语") == "猫粮碗都替你尴尬，本汪无语")
precondition(Pet.cat.voiceForBorrowedLine("本猫宣布") == "本猫宣布")
precondition(PetMood.happy.assetName(for: .cat) == "cat-happy" && PetMood.happy.monoAssetName(for: .cat) == "cat-happy-mono")
precondition(Pet.dog.isAvailable && PetMood.happy.assetName(for: .dog) == "dog-happy" && PetMood.nodata.monoAssetName(for: .dog) == "dog-nodata-mono")
// 锁屏重试窗口：只在 05:00–12:00
precondition(ToneRule.isRetryWindow(BJ.time(5, 0, on: today)) && ToneRule.isRetryWindow(BJ.time(11, 59, on: today)))
precondition(!ToneRule.isRetryWindow(BJ.time(12, 0, on: today)) && !ToneRule.isRetryWindow(BJ.time(4, 59, on: today)) && !ToneRule.isRetryWindow(BJ.time(21, 30, on: today)))
let catR = FileManager.default.contents(atPath: base+"roasts.json"), catE = FileManager.default.contents(atPath: base+"encouragements.json")
let dogLib = ContentLibrary.load(pet: .dog, roastsData: nil, encouragementsData: nil, catRoastsData: { catR }, catEncouragementsData: { catE })
precondition(dogLib.borrowedCatLines && cnt(dogLib.roast) == 240 && cnt(dogLib.encourage) == 240)
precondition(!dogLib.roast.values.flatMap { $0.values.flatMap { $0 } }.contains { $0.contains("本猫") })
let dogOwn = ContentLibrary.load(pet: .dog, roastsData: #"{"roasts":{"<3000":{"23点前":["汪{steps}"]}},"no_sleep_data":{"<3000":["汪汪{steps}"]}}"#.data(using: .utf8), encouragementsData: nil, catRoastsData: { catR }, catEncouragementsData: { catE })
precondition(dogOwn.candidates(tone: .roast, stepBucket: "<3000", bedtimeBucket: "23点前") == ["汪{steps}"] && dogOwn.borrowedCatLines)
print("pet OK")
print("ALL OK")
