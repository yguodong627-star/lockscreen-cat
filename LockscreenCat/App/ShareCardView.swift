import SwiftUI
import UIKit
import Photos

/// 分享卡（ImageRenderer 渲染成图片）
struct ShareCardView: View {
    let state: PetState

    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Text(dateText).font(.system(size: 15, weight: .medium))
                Spacer()
                if let badge = state.tone?.badge {
                    Text(badge)
                        .font(.system(size: 13, weight: .bold))
                        .padding(.horizontal, 10).padding(.vertical, 4)
                        .background(Capsule().fill(Theme.orange.opacity(0.25)))
                }
            }
            Image(state.assetName)
                .resizable().scaledToFit()
                .frame(width: 230, height: 230)
            Text(state.line ?? state.caption)
                .font(.system(size: 22, weight: .bold))
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
                .padding(.horizontal, 8)
            HStack(spacing: 24) {
                Label(state.snapshot.stepsText + " 步", systemImage: "figure.walk")
                Label(state.snapshot.bedtimeText, systemImage: "moon.zzz.fill")
            }
            .font(.system(size: 15, weight: .semibold))
            .foregroundStyle(Theme.brown.opacity(0.75))
            Spacer(minLength: 0)
            Text(Copy.cardFooter)
                .font(.system(size: 12))
                .foregroundStyle(Theme.brown.opacity(0.5))
                .frame(maxWidth: .infinity, alignment: .trailing)
        }
        .foregroundStyle(Theme.brown)
        .padding(24)
        .frame(width: 360, height: 520)
        .background(
            RoundedRectangle(cornerRadius: 32)
                .fill(Theme.cream)
                .overlay(RoundedRectangle(cornerRadius: 32).stroke(Theme.orange, lineWidth: 4))
        )
    }

    private var dateText: String {
        let c = BJ.calendar.dateComponents([.month, .day], from: state.date)
        return "\(c.month ?? 0)月\(c.day ?? 0)日 · \(state.pet.displayName)观察日记"
    }
}

@MainActor
struct ShareCardSheet: View {
    let state: PetState
    @Environment(\.dismiss) private var dismiss
    @State private var image: UIImage?
    @State private var message: String?

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                ShareCardView(state: state)
                    .scaleEffect(0.85)
                    .frame(height: 450)
                if let image {
                    HStack(spacing: 14) {
                        Button {
                            save(image)
                        } label: {
                            Label(Copy.saveCardButton, systemImage: "square.and.arrow.down")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.borderedProminent)
                        .tint(Theme.deepOrange)

                        ShareLink(item: Image(uiImage: image),
                                  preview: SharePreview("\(state.pet.displayName)观察日记", image: Image(uiImage: image))) {
                            Label("分享", systemImage: "square.and.arrow.up")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)
                        .tint(Theme.brown)
                    }
                    .controlSize(.large)
                    .padding(.horizontal, 24)
                }
                if let message {
                    Text(message).font(.callout).foregroundStyle(Theme.brown)
                }
                Spacer()
            }
            .padding(.top, 12)
            .background(Theme.cream.opacity(0.5).ignoresSafeArea())
            .navigationTitle("吐槽卡")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("关闭") { dismiss() } } }
            .onAppear(perform: render)
        }
    }

    private func render() {
        let renderer = ImageRenderer(content: ShareCardView(state: state))
        renderer.scale = 3
        image = renderer.uiImage
    }

    private func save(_ image: UIImage) {
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else {
                DispatchQueue.main.async { message = "没有相册权限。去「设置 > \(AppConfig.appDisplayName) > 照片」里允许“仅添加照片”。" }
                return
            }
            PHPhotoLibrary.shared().performChanges({
                PHAssetChangeRequest.creationRequestForAsset(from: image)
            }) { ok, _ in
                DispatchQueue.main.async { message = ok ? Copy.saveCardSuccess : "保存失败，再试一次？" }
            }
        }
    }
}
