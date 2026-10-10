import SwiftUI
import UIKit

struct ContentView: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.openURL) private var openURL
    @State private var showSettings = false
    @State private var showShare = false

    private var s: PetState { model.state }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 18) {
                    header
                    Image(s.assetName)
                        .resizable()
                        .scaledToFit()
                        .frame(maxWidth: 280, maxHeight: 280)
                        .accessibilityLabel(s.mood.title)
                        .id(s.mood)
                        .transition(.scale.combined(with: .opacity))
                    lineCard
                    stats
                    if !model.useSample && !s.snapshot.hasAnyData && model.healthRequested {
                        deniedCard
                    } else if let hint = s.bedtimeHint {
                        Text(hint)
                            .font(.footnote)
                            .foregroundStyle(Theme.brown.opacity(0.6))
                            .padding(.horizontal)
                    }
                    if !model.healthRequested && !model.useSample {
                        Button("授权读取步数和睡眠") { Task { await model.requestHealth() } }
                            .buttonStyle(.borderedProminent)
                            .tint(Theme.deepOrange)
                    }
                }
                .padding(.horizontal, 20)
                .padding(.bottom, 40)
                .animation(.spring(duration: 0.35), value: s.mood)
            }
            .refreshable { await model.refresh() }
            .background(Theme.cream.ignoresSafeArea())
            .navigationTitle(AppConfig.appDisplayName)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button { showSettings = true } label: { Image(systemName: "gearshape") }
                        .tint(Theme.brown)
                }
            }
            .sheet(isPresented: $showSettings) { SettingsView() }
            .sheet(isPresented: $showShare) { ShareCardSheet(state: s) }
        }
    }

    private var header: some View {
        HStack {
            Text(dateTitle)
                .font(.subheadline.weight(.medium))
            Spacer()
            if model.useSample {
                Text("示例数据")
                    .font(.caption.bold())
                    .padding(.horizontal, 8).padding(.vertical, 3)
                    .background(Capsule().fill(Theme.orange.opacity(0.25)))
            }
            Text(s.mood.title)
                .font(.caption)
                .padding(.horizontal, 8).padding(.vertical, 3)
                .background(Capsule().fill(Theme.brown.opacity(0.08)))
        }
        .foregroundStyle(Theme.brown)
        .padding(.top, 8)
    }

    private var dateTitle: String {
        let c = BJ.calendar.dateComponents([.month, .day, .weekday], from: s.date)
        let w = ["日", "一", "二", "三", "四", "五", "六"][((c.weekday ?? 1) - 1) % 7]
        return "\(c.month ?? 0)月\(c.day ?? 0)日 周\(w) · \(s.phase.title)"
    }

    private var lineCard: some View {
        VStack(alignment: .leading, spacing: 12) {
            if let tone = s.tone, let badge = tone.badge {
                Text(badge)
                    .font(.caption.bold())
                    .foregroundStyle(tone == .encourage ? Theme.encourage : Theme.deepOrange)
            }
            if let line = s.line {
                Text(line)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(Theme.brown)
                    .fixedSize(horizontal: false, vertical: true)
                    .frame(maxWidth: .infinity, alignment: .leading)
                HStack {
                    Button {
                        withAnimation { model.shuffleLine() }
                    } label: {
                        Label("换一句", systemImage: "arrow.triangle.2.circlepath")
                    }
                    .buttonStyle(.bordered)
                    .tint(Theme.brown)
                    Spacer()
                    Button { showShare = true } label: {
                        Label("分享卡", systemImage: "square.and.arrow.up")
                    }
                    .buttonStyle(.borderedProminent)
                    .tint(Theme.deepOrange)
                }
            } else {
                Text(s.caption)
                    .font(.title3.weight(.semibold))
                    .foregroundStyle(Theme.brown)
                Text("每晚 \(ToneRule.eveningLineHour):00 后，\(s.pet.displayName)会给今天写一句旁白。")
                    .font(.footnote)
                    .foregroundStyle(Theme.brown.opacity(0.6))
                Button("让\(s.pet.displayName)先说一句") { withAnimation { model.revealLine() } }
                    .buttonStyle(.bordered)
                    .tint(Theme.deepOrange)
            }
        }
        .padding(18)
        .background(RoundedRectangle(cornerRadius: 22).fill(Theme.card))
        .shadow(color: Theme.brown.opacity(0.08), radius: 10, y: 4)
    }

    private var stats: some View {
        HStack(spacing: 12) {
            statBox(icon: "figure.walk", title: "今日步数", value: s.snapshot.stepsText)
            statBox(icon: "moon.zzz.fill",
                    title: s.snapshot.bedtimeSource == .inBed ? "昨晚上床（卧床）" : "昨晚入睡",
                    value: s.snapshot.bedtimeText)
        }
    }

    private func statBox(icon: String, title: String, value: String) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            Label(title, systemImage: icon)
                .font(.caption)
                .foregroundStyle(Theme.brown.opacity(0.7))
            Text(value)
                .font(.title2.weight(.bold).monospacedDigit())
                .foregroundStyle(Theme.brown)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(14)
        .background(RoundedRectangle(cornerRadius: 18).fill(Theme.card))
    }

    private var deniedCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(Copy.deniedText)
                .font(.callout)
                .foregroundStyle(Theme.brown)
                .fixedSize(horizontal: false, vertical: true)
            Button(Copy.deniedButton) {
                if let url = URL(string: "x-apple-health://") {
                    openURL(url) { ok in
                        if !ok, let settingsURL = URL(string: UIApplication.openSettingsURLString) { openURL(settingsURL) }
                    }
                }
            }
            .buttonStyle(.borderedProminent)
            .tint(Theme.deepOrange)
        }
        .padding(16)
        .background(RoundedRectangle(cornerRadius: 18).fill(Theme.orange.opacity(0.15)))
    }
}
