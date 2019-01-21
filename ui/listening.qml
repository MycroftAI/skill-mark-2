import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Item {
    function getOpacity(volume) {
        if (volume < 2)
            return 0.7;
        else if (volume < 5)
            return 0.8;
        else if (volume < 8)
            return 0.9;
        else
            return 1.0;
    }

    function getLength(volume, pos) {
        var val = (volume * 2) + (pos * 2);
        if (val < 0)
            val = 0;
        else if (val > 10)
            val = 10;
        return 36 + 36 * val;
    }
    property var volume: sessionData.volume

    onVolumeChanged: {
        af11.running = true
        af12.running = true
        af13.running = true
        af14.running = true
        af15.running = true
    }
    PropertyAnimation {
        id: af11
        target: f11
        property: "height"
        to: getLength(sessionData.volume, -2)
        duration: 50
    }
    PropertyAnimation {
        id: af12
        target: f12
        property: "height"
        to: getLength(sessionData.volume, -1)
        duration: 50
    }
    PropertyAnimation {
        id: af13
        target: f13
        property: "height"
        to: getLength(sessionData.volume, 0)
        duration: 50
    }
    PropertyAnimation {
        id: af14
        target: f14
        property: "height"
        to: getLength(sessionData.volume, -1)
        duration: 50
    }
    PropertyAnimation {
        id: af15
        target: f15
        property: "height"
        to: getLength(sessionData.volume, -2)
        duration: 50
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
                VolumeBar {
                    id: f11
                    opacity: getOpacity(sessionData.volume)
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                VolumeBar {
                    id: f12
                    opacity: getOpacity(sessionData.volume)
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                VolumeBar {
                    id: f13
                    opacity: getOpacity(sessionData.volume)
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                VolumeBar {
                    id: f14
                    opacity: getOpacity(sessionData.volume)
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                VolumeBar {
                    id: f15
                    opacity: getOpacity(sessionData.volume)
                }
            }
        }
    }
}
