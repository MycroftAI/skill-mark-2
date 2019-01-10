import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Item {
    function getLength(volume, pos) {
        var val = (volume * 2 + pos);
        if (val < 0)
            val = 0;
        else if (val > 10)
        val = 10;
        console.log(val)
        return 36 + 36 * val;
    }

    ColumnLayout {
        id: grid
        width: parent.width
	height: parent.height
        spacing: Kirigami.Units.largeSpacing

        Item {
            height: Kirigami.Units.largeSpacing * 5
        }
        RowLayout {
            id: frame1
            visible: true
	height: parent.height
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Rectangle {
                    id: f11
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    width: 36
                    radius: 18
                    height: getLength(sessionData.volume, -2)
                    color: "#40DBB0"
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Rectangle {
                    id: f12
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    width: 36
                    radius: 18
                    height: getLength(sessionData.volume, -1)
                    color: "#40DBB0"
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Rectangle {
                    id: f13
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    width: 36
                    radius: 18
                    height: getLength(sessionData.volume, 0)
                    color: "#40DBB0"
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Rectangle {
                    id: f14
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    width: 36
                    radius: 18
                    height: getLength(sessionData.volume, -1)
                    color: "#40DBB0"
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Rectangle {
                    id: f15
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    width: 36
                    radius: 18
                    height: getLength(sessionData.volume, -2)
                    color: "#40DBB0"
                }
            }
        }
    }
}
