import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    skillBackgroundSource: Qt.resolvedUrl('bg.png')
    ColumnLayout {
        id: grid
        Layout.fillWidth: true
        width: parent.width
        spacing: Kirigami.Units.largeSpacing

        Item {
            height: Kirigami.Units.largeSpacing * 5
        }
        RowLayout {
           Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
           id: row1
           Rectangle {
                id: rectangle
                width: 200
                height: 200
                color: "#00000000"
                
                Image {
                    id: left_lower_lid
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: 86
                    width: 78
                    height: 50
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("face/lid.svg")
                }
            } 
            Rectangle {
                id: rectangle2
                width: 200
                height: 200
                color: "#00000000"

                Image {
                    id: right_lower_lid
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: 86
                    width: 78
                    height: 50
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("face/lid.svg")
                }
            }
        }
        
        Item {
            height: Kirigami.Units.largeSpacing * 9
        }
        Image {
            id: smile
            Layout.alignment: Qt.AlignHCenter
	    fillMode: Image.PreserveAspectFit
	    source: Qt.resolvedUrl("face/GreySmile.svg")
	}
    }
}
