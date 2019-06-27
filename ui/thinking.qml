import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

Item {
    id: "thinking"

    AnimatedImage {
        id: thinkingGIF
        height: Math.min(parent.width, parent.height)
        anchors.centerIn: parent
        source: Qt.resolvedUrl("ring_ball.gif")
        fillMode: Image.PreserveAspectFit
        playing: true
    }

// Commented out Lottie for now.  The Lottie player is crashing.
//
//    LottieAnimation {
//        id: thinkingAnimation
//        anchors.centerIn: parent
//        height: Math.min(parent.width, parent.height)
//        source: Qt.resolvedUrl("face/thinking.json")
//        loops: Animation.Infinite
//        fillMode: Image.PreserveAspectFit
//        running: true
//    }
}
