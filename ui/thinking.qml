import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft
import org.kde.lottie 1.0

Item {
    id: "thinking"
    LottieAnimation {
        id: thinkingAnimation
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        //Layout.alignment: Qt.AlignHCenter
        Layout.preferredWidth: 200
        Layout.preferredHeight: Layout.preferredWidth

        source: Qt.resolvedUrl("face/thinking.json")

        loops: Animation.Infinite
        fillMode: Image.PreserveAspectFit
        running: true
    }
}
