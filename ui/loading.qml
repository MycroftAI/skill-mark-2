import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Item {
    id: root

    Label {
        font.weight: Font.Bold
        Layout.fillWidth: true
        anchors.horizontalCenter: parent.horizontalCenter
        Layout.preferredHeight: Mycroft.Units.gridUnit * 12
        font.pixelSize: Mycroft.Units.gridUnit * 4
        color: "#22a7f0"
        text: "Loading Skills..."
    }

    Mycroft.BusyIndicator {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: Mycroft.Units.gridUnit * 4
        running: true
    }
}
