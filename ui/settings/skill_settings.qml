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
    id: skillSettingsView
    anchors.fill: parent
    property var skillConfig: mainLoaderView.skillConfig
    
    function selectSettingUpdated(skillevent, key, value){
        Mycroft.MycroftController.sendRequest(skillevent, {"setting_key": key, "setting_value": value})
    }
    
    Component.onCompleted: {
        console.log(skillConfig.configs)
    }
        
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
            text: "Skill Configuration"
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
            anchors.fill: parent
            spacing: Kirigami.Units.smallSpacing
            
            ListView {
                id: skillConfigView
                clip: true
                Layout.fillWidth: true
                Layout.fillHeight: true
                model: skillConfig.configs
                boundsBehavior: Flickable.StopAtBounds
                delegate: Control {
                    contentItem: Item {
                    implicitWidth: delegateLayout.implicitWidth;
                    implicitHeight: delegateLayout.implicitHeight;
            
                        ColumnLayout {
                            id: delegateLayout
                            width: skillConfigView.width
                            spacing: Kirigami.Units.largeSpacing
                            
                            anchors {
                                top: parent.top;
                            }
                            
                            Kirigami.Separator {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 1
                            }
                            
                            Kirigami.Heading {
                                id: skillName
                                Layout.alignment: Qt.AlignHCenter
                                height: paintedHeight
                                elide: Text.ElideRight
                                font.weight: Font.DemiBold
                                text: modelData.skill_id
                                textFormat: Text.PlainText
                                level: 2
                                
                                Kirigami.Separator {
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.bottom: parent.bottom
                                    height: 1
                                    color: Kirigami.Theme.linkColor
                                }
                            }
                        
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Math.round(units.gridUnit / 2)
                                
                                Kirigami.Heading {
                                    id: skillSettingName
                                    Layout.alignment: Qt.AlignLeft
                                    height: paintedHeight
                                    elide: Text.ElideRight
                                    text: modelData.setting_key
                                    textFormat: Text.PlainText
                                    level: 3
                                }
                                
                                GridLayout {
                                    id: skillSettingType
                                    Layout.preferredWidth: Kirigami.Units.gridUnit * 3
                                    Layout.alignment: Qt.AlignRight
                                    Layout.fillHeight: true
                                    columns: 3
                                                                        
                                    ButtonGroup {
                                        id: settingGroup
                                    }
                                    
                                    Component.onCompleted: {
                                        if (modelData.setting_type == "select") {
                                            var newObject = Qt.createComponent("settings_button/settingButton.qml")
                                            var skilleventname = modelData.skill_id + ".setting"
                                            for (var i = 0; i < modelData.available_values.length; i++) {
                                                var rbutton = newObject.createObject(skillSettingType, {checked: modelData.current_value == modelData.available_values[i] ? 1 : 0 , text: modelData.available_values[i], "skillevent": skilleventname, "key": modelData.setting_key, "value": modelData.available_values[i]});
                                                rbutton.clicked.connect(selectSettingUpdated)
                                            }
                                        } 
                                    }
                                }
                            }
                            
                            Kirigami.Separator {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 1
                            }
                        }
                    }
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
 
