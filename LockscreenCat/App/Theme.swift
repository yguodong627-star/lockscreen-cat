import SwiftUI

enum Theme {
    static let cream = Color(red: 1.0, green: 0.973, blue: 0.933)        // #FFF8EE
    static let brown = Color(red: 0.290, green: 0.173, blue: 0.114)      // #4A2C1D
    static let orange = Color(red: 0.957, green: 0.627, blue: 0.294)     // #F4A04B
    static let deepOrange = Color(red: 0.851, green: 0.455, blue: 0.165) // #D9742A
    static let card = Color.white
    static let encourage = Color(red: 0.36, green: 0.62, blue: 0.40)
}

extension Tone {
    var badge: String? {
        switch self {
        case .roast: return "今日吐槽"
        case .encourage: return "今日鼓励"
        case .neutral: return nil
        }
    }
}
