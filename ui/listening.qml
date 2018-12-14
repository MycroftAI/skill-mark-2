import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.4 as Kirigami

import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    skillBackgroundSource: Qt.resolvedUrl('bg.png')
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
            visible: false
	height: parent.height
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f11
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Ellipse.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f12
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Ellipse.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f13
                    fillMode: Image.PreserveAspectFit
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    source: Qt.resolvedUrl("listen2/Ellipse.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f14
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Ellipse.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f15
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Ellipse.svg")
                }
            }
        }
        RowLayout {
            id: frame2
            visible: false
	    height: parent.height
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f21
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Ellipse.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f22
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Rectangle2.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f23
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Rectangle3.svg")
                }	
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f24
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Rectangle2.svg")
                }	
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f25
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen2/Ellipse.svg")
                }
            }
        }
        RowLayout {
            id: frame3
            visible: false
	height: parent.height
            Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f31
                    fillMode: Image.PreserveAspectFit
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    source: Qt.resolvedUrl("listen3/Rectangle1.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f32
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen3/Rectangle3.svg")
                }	
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f33
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen3/Rectangle5.svg")
                }	
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f34
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen3/Rectangle3.svg")
                }
            }
            Rectangle {
                height: 600
                width: 60
                color: "#00000000"
                Image {
                    id: f35
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.verticalCenter: parent.verticalCenter
                    fillMode: Image.PreserveAspectFit
                    source: Qt.resolvedUrl("listen3/Rectangle1.svg")
                }
            }
        }
    }
    // Timed update of which element to show
    Timer {
        id: tmr
        interval: 200
        running: true
        repeat: true
        property int frame: 1

        onTriggered: frame = Qt.binding(function() {
            // The frame variable here can be replaced with a volume level
            // variable.

            switch (sessionData.volume) {
                case 0:
                    frame1.visible = true;
                    frame2.visible = false;
                    frame3.visible = false;
                    break;
                case 1:
                    frame1.visible = false;
                    frame2.visible = true;
                    frame3.visible = false;
                    break;
                default:
                    frame1.visible = false;
                    frame2.visible = false;
                    frame3.visible = true;
                    break;
                case 4:
                    frame1.visible = false;
                    frame2.visible = true;
                    frame3.visible = false;
                    break;
            }
            if (frame < 4) {
                return frame + 1
            }
            else
            {
                return 1;
            }
	});

    }
}
