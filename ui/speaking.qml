import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Face {
    id: root

    eyesOpen: true
    mouth: speaking ? "" : "Smile.svg"
    property bool speaking: false

    property var startViseme: sessionData.viseme.start
    onStartVisemeChanged: {
        root.speaking = true;
    }

    function getVisemeImg(viseme){
        return "face/" + viseme + ".svg"
    }

    function getVisemeWidth(viseme){
        switch (viseme) {
            case "0": return 290 / 2;
            case "1": return 130 / 2;
            case "2": return 250 / 2;
            case "3": return 170 / 2;
            case "4": return 60 / 2;
            case "5": return 110 / 2;
            case "6": return 90 / 2;
        }
    }

    Rectangle {
        id: mouth_viseme
        visible: root.speaking
        parent: mouthItem
        anchors.centerIn: parent
        width: 40
        onWidthChanged: stopTimer.restart()
        height: width
        radius: width / 2
        color: "black"
        border.color: "white"
        border.width: 20
        Behavior on width {
            PropertyAnimation {
                property: "width"
                duration: 50
                easing.type: Easing.InOutQuad
            }
        }
    }

    Timer {
        id: stopTimer
        interval: 500
        onTriggered: {
            root.speaking = false
        }
    }

    Timer {
        id: tmr
        interval: 50 // every 50 ms
        running: root.speaking
        repeat: true
        onTriggered: {
            var now = Date.now() / 1000;
            var start = sessionData.viseme.start;
            var offset = start;
            // Compare viseme start/stop with current time and choose viseme
            // appropriately
            for (var i = 0; i < sessionData.viseme.visemes.length; i+=2) {
                if (sessionData.viseme.start == 0)
                    break;
                if (now >= offset &&
                        now < start + sessionData.viseme.visemes[i][1])
                {
                    mouth_viseme.width = getVisemeWidth(sessionData.viseme.visemes[i][0]);
                    offset = start + sessionData.viseme.visemes[i][1];
                    return
                }
            }
            // Outside of span show default smile
            //return Qt.resolvedUrl(getVisemeImg("Smile"));
        }
    }
}
