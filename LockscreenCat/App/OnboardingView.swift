import SwiftUI

/// 首次打开：三屏介绍（copy.md）→ 健康授权 → 通知预提示 → 教你加锁屏小组件
struct OnboardingView: View {
    @EnvironmentObject var model: AppModel
    @State private var page = 0
    @State private var step: Step = .pet
    @State private var pet: Pet = SharedStore.shared.pet

    enum Step { case pet, intro, notification, widget }

    private var pages: [(String, String)] {
        [
            (PetMood.proud.assetName(for: pet), Copy.onboarding1),
            (PetMood.happy.assetName(for: pet), Copy.onboarding2),
            (PetMood.nodata.assetName(for: pet), Copy.onboarding3),
        ]
    }

    var body: some View {
        ZStack {
            Theme.cream.ignoresSafeArea()
            switch step {
            case .pet: petChoice
            case .intro: intro
            case .notification: notification
            case .widget: widgetGuide
            }
        }
        .foregroundStyle(Theme.brown)
    }

    private var petChoice: some View {
        VStack(spacing: 28) {
            Spacer()
            Text("选一个住在你锁屏上的形象").font(.title2.bold())
            PetPicker(selection: $pet)
                .padding(.horizontal, 28)
            Text("之后可以在「设置 > 形象」里随时换。")
                .font(.footnote)
                .foregroundStyle(Theme.brown.opacity(0.6))
            Spacer()
            Button {
                model.setPet(pet)
                withAnimation { step = .intro }
            } label: {
                Text("就它了").font(.headline).frame(maxWidth: .infinity).padding(.vertical, 6)
            }
            .buttonStyle(.borderedProminent)
            .tint(Theme.deepOrange)
            .padding(.horizontal, 32)
            .padding(.bottom, 32)
        }
    }

    private var intro: some View {
        VStack(spacing: 24) {
            TabView(selection: $page) {
                ForEach(pages.indices, id: \.self) { i in
                    VStack(spacing: 28) {
                        Image(pages[i].0).resizable().scaledToFit().frame(height: 260)
                        Text(pages[i].1)
                            .font(.title3.weight(.semibold))
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 32)
                    }
                    .tag(i)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .always))
            .indexViewStyle(.page(backgroundDisplayMode: .always))

            Button {
                if page < pages.count - 1 {
                    withAnimation { page += 1 }
                } else {
                    Task {
                        await model.requestHealth()
                        withAnimation { step = .notification }
                    }
                }
            } label: {
                Text(page < pages.count - 1 ? "下一步" : Copy.onboardingButton)
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 6)
            }
            .buttonStyle(.borderedProminent)
            .tint(Theme.deepOrange)
            .padding(.horizontal, 32)
            .padding(.bottom, 32)
        }
    }

    private var notification: some View {
        VStack(spacing: 28) {
            Spacer()
            Image(PetMood.sleepy.assetName(for: pet)).resizable().scaledToFit().frame(height: 220)
            Text(Copy.notificationPrePrompt)
                .font(.title3.weight(.semibold))
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)
            Spacer()
            VStack(spacing: 12) {
                Button {
                    Task {
                        let ok = await NotificationScheduler.requestPermission()
                        model.store.reminderEnabled = ok
                        await NotificationScheduler.reschedule()
                        withAnimation { step = .widget }
                    }
                } label: {
                    Text(Copy.notificationYes).font(.headline).frame(maxWidth: .infinity).padding(.vertical, 6)
                }
                .buttonStyle(.borderedProminent)
                .tint(Theme.deepOrange)
                Button(Copy.notificationNo) {
                    model.store.reminderEnabled = false
                    withAnimation { step = .widget }
                }
                .tint(Theme.brown)
            }
            .padding(.horizontal, 32)
            .padding(.bottom, 32)
        }
    }

    private var widgetGuide: some View {
        VStack(spacing: 20) {
            Spacer()
            Image(PetMood.happy.assetName(for: pet)).resizable().scaledToFit().frame(height: 180)
            Text("把\(pet.displayName)放到锁屏上").font(.title2.bold())
            WidgetGuideSteps()
                .padding(.horizontal, 28)
            Spacer()
            Button {
                model.finishOnboarding()
            } label: {
                Text("知道了").font(.headline).frame(maxWidth: .infinity).padding(.vertical, 6)
            }
            .buttonStyle(.borderedProminent)
            .tint(Theme.deepOrange)
            .padding(.horizontal, 32)
            .padding(.bottom, 32)
        }
    }
}

/// 添加小组件的步骤（引导页和设置页共用）
struct WidgetGuideSteps: View {
    private var steps: [String] {
        let name = AppConfig.appDisplayName
        let pet = Pet.current.displayName
        return [
            "锁屏状态下长按屏幕，点「自定」→「锁定屏幕」。",
            "点时间下方的小组件区域，找到「\(name)」。",
            "选圆形（只有\(pet)）或长方形（\(pet) + 一句话），点空白处完成。",
            "桌面小组件：长按桌面空白处 → 左上角「编辑」→「添加小组件」→ 搜「\(name)」。",
        ]
    }
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ForEach(steps.indices, id: \.self) { i in
                HStack(alignment: .top, spacing: 10) {
                    Text("\(i + 1)")
                        .font(.caption.bold())
                        .frame(width: 22, height: 22)
                        .background(Circle().fill(Theme.orange.opacity(0.3)))
                    Text(steps[i]).font(.callout).fixedSize(horizontal: false, vertical: true)
                }
            }
        }
    }
}
