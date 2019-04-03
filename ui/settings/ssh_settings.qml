/*
 * Copyright 2018 Aditya Mehra <aix.m@outlook.com>
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.5 as Kirigami
import org.kde.plasma.core 2.0 as PlasmaCore
import Mycroft 1.0 as Mycroft

Item {
    id: sshSettingsView
    anchors.fill: parent
    property bool connectionActive: false
        
    Item {
        id: topArea
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        height: Kirigami.Units.gridUnit * 2
        
        Kirigami.Heading {
            id: brightnessSettingPageTextHeading
            level: 1
            wrapMode: Text.WordWrap
            anchors.centerIn: parent
            font.bold: true
            text: "SSH Settings"
            color: Kirigami.Theme.linkColor
        }
    }

    Item {
        anchors.top: topArea.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: areaSep.top
        
        ColumnLayout {
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: Kirigami.Units.smallSpacing
            
            Kirigami.Heading {
                id: warnText
                level: 3
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: "By enabling SSH Mode, anyone can access, change or delete anything on this device by connecting to it via another device."
            }
            
            Item {
                Layout.fillWidth: true
                Layout.preferredHeight: Kirigami.Units.largeSpacing
            }
            
            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: serviceActiveLabel.implicitHeight + Kirigami.Units.smallSpacing
                Label {
                    id: serviceActiveLabel
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignLeft
                    text: "Service Active:"
                }
                Label {
                    id: serviceActionState
                    Layout.alignment: Qt.AlignRight
                    text: connectionActive ? "Actived" : "Deactived"
                    color: connectionActive ? "Green" : "Red"
                }
            }
            
            Kirigami.Separator {
                Layout.fillWidth: true
            }
            
            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: enableServiceLabel.implicitHeight + Kirigami.Units.smallSpacing    
                Label {
                    id: enableServiceLabel
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignLeft
                    text: "Enable SSH Service:"
                }
                
                CheckBox {
                    Layout.alignment: Qt.AlignRight
                    checked: false
                    
                    onCheckedChanged: {
                        if(checked){
                            connectionActive = true
                        }
                        else {
                            connectionActive = false
                        }
                    }
                }
            }
            
            
            Kirigami.Separator {
                Layout.fillWidth: true
            }
            
            RowLayout {
                Layout.fillWidth: true
            
                Label {
                    id: autoEnableServiceLabel
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignLeft
                    text: "Enable On Boot:"
                }
                
                CheckBox {
                    Layout.alignment: Qt.AlignRight
                    checked: false
                    enabled: connectionActive ? 1 : 0
                }
            }
        }
    }

    Kirigami.Separator {
        id: areaSep
        anchors.bottom: bottomArea.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 1
    }
    
    Item {
        id: bottomArea
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: Kirigami.Units.largeSpacing * 1.15
        height: backIcon.implicitHeight + Kirigami.Units.largeSpacing * 1.15

        RowLayout {
            anchors.fill: parent
            
            Kirigami.Icon {
                id: backIcon
                source: "go-previous"
                Layout.preferredHeight: Kirigami.Units.iconSizes.medium
                Layout.preferredWidth: Kirigami.Units.iconSizes.medium
            }
            
            Kirigami.Heading {
                level: 2
                wrapMode: Text.WordWrap
                font.bold: true
                text: "Device Settings"
                Layout.fillWidth: true
                Layout.preferredHeight: Kirigami.Units.gridUnit * 2
            }
        }
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                triggerGuiEvent("mycroft.device.settings", {})
            }
        }
    }
} 
