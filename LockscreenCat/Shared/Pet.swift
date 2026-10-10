import Foundation

/// 形象（小猫 / 小狗）。存进 App Group，App 和小组件都按它切换素材、句库和称呼。
///
/// 素材命名：`<rawValue>-<表情>` 和 `<rawValue>-<表情>-mono`，例如 cat-happy、dog-happy-mono。
/// 句库：cat 用 roasts.json / encouragements.json；dog 用 roasts_dog.json / encouragements_dog.json
///      （缺失时退回猫的句库，并做称呼替换）。
enum Pet: String, CaseIterable, Codable, Identifiable {
    case cat
    case dog

    var id: String { rawValue }

    /// 已开放选择的形象。新形象素材放进 Assets.xcassets 后，加进这里即可（一行改动）。
    static let availablePets: Set<Pet> = [.cat, .dog]

    var isAvailable: Bool { Pet.availablePets.contains(self) }

    /// 形象名（copy.md 里的 {pet}）：小猫 / 小狗
    var displayName: String {
        switch self {
        case .cat: return "小猫"
        case .dog: return "小狗"
        }
    }

    /// 自称：本猫 / 本汪
    var selfRef: String {
        switch self {
        case .cat: return "本猫"
        case .dog: return "本汪"
        }
    }

    /// 句库文件后缀：cat → ""（roasts.json），dog → "_dog"（roasts_dog.json）
    var contentSuffix: String {
        switch self {
        case .cat: return ""
        case .dog: return "_dog"
        }
    }

    /// 实际使用的素材形象：还没上线的形象先用猫的图（理论上选不到，只是兜底）
    var artPet: Pet { isAvailable ? self : .cat }

    /// 当前选中的形象（App Group）
    static var current: Pet { SharedStore.shared.pet }

    /// 界面文案里的 {pet} 换成形象名（copy.md 约定）；{self} 换成自称（本猫 / 本汪），备用
    func fill(_ text: String) -> String {
        text.replacingOccurrences(of: "{pet}", with: displayName)
            .replacingOccurrences(of: "{self}", with: selfRef)
    }

    /// 句库借用猫的句子时用的温和替换：只换“本猫 / 橘猫 / 小猫”，不动“猫粮碗、猫科”等词
    func voiceForBorrowedLine(_ text: String) -> String {
        guard self != .cat else { return text }
        return text
            .replacingOccurrences(of: "本猫", with: selfRef)
            .replacingOccurrences(of: "橘猫", with: displayName)
            .replacingOccurrences(of: "小猫", with: displayName)
    }
}
