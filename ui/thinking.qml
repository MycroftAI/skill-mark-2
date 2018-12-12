import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    ColumnLayout {
        id: grid
        Layout.fillWidth: true
        width: parent.width
        spacing: Kirigami.Units.largeSpacing

        Item {
            height: Kirigami.Units.largeSpacing * 5
        }

        Kirigami.Heading {
            id: title
            Layout.alignment: Qt.AlignHCenter
            level: 1
            Layout.columnSpan: 2
            wrapMode: Text.WordWrap
            font.capitalization: Font.AllUppercase
            text: "THINKING"
        }
        Kirigami.Heading {
            id: answer
            Layout.alignment: Qt.AlignHCenter
            level: 2
            wrapMode: Text.WordWrap
            font.capitalization: Font.Capitalize
            text: "TODO: Hourglass animation"
        }
    }
}