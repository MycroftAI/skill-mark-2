import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Item {
    id: "thinking"
    Item {
        id: top_spacing
        anchors.top: parent.top
        height: 176
    }
    Rectangle {
        id: eyes
        anchors.top: top_spacing.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        height: 141
        color: "#00000000"
        Rectangle {
            id: rectangle
            anchors.left: parent.left
            anchors.leftMargin: 12
            width: 141
            color: "#00000000"
            Image {
                id: left_eye
                anchors.horizontalCenter: parent.horizontalCenter
                y: 0
                width: 141
                source: Qt.resolvedUrl("face/Eyeball.svg")
                fillMode: Image.PreserveAspectFit
            }
            Image {
                id: left_eye_upper
                anchors.horizontalCenter: parent.horizontalCenter
                width: 141
                fillMode: Image.PreserveAspectFit
                source: Qt.resolvedUrl("face/upper-lid.svg")
            }
        } 
        Rectangle {
            anchors.right: parent.right
            anchors.rightMargin: 12
            id: rectangle2
            width: 141
            color: "#00000000"

            Image {
                id: right_eye
                anchors.horizontalCenter: parent.horizontalCenter
                width: 141
                fillMode: Image.PreserveAspectFit
                source: Qt.resolvedUrl("face/Eyeball.svg")
            }
            Image {
                id: right_eye_upper
                anchors.horizontalCenter: parent.horizontalCenter
                width: 141
                fillMode: Image.PreserveAspectFit
                source: Qt.resolvedUrl("face/upper-lid.svg")
            }
        }
    }
    
    Item {
        id: mid_spacing
        anchors.top: eyes.bottom
        height: 112
    }

    Rectangle {
        id: mouth_rectangle
        anchors.top: mid_spacing.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        width: 266
        height: 115
        color: "#00000000"
        Image {
            id: smile
            opacity: 1
            anchors.centerIn: parent
            anchors.horizontalCenter: parent.horizontalCenter
            fillMode: Image.PreserveAspectFit
            width: 266
            source: Qt.resolvedUrl('face/Smile.svg')
        }
    }
    Rectangle {
        id: hide_smile
        color: "black"
        y: 450
        x: 20
        width: 80
        height: 80
    }

    SequentialAnimation {
        loops: Animation.Infinite
        running: true
        PropertyAnimation {
            id: fade;
            target: hide_smile;
            property: "x";
            to: 450;
            duration: 500
        }
        PropertyAnimation {
            id: unfade;
            target: hide_smile;
            property: "x";
            to: 50;
            duration: 500
        }
    }
}
