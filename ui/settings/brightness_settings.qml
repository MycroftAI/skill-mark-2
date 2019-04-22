/*
 * Copyright 2018 by Marco Martin <mart@kde.org>
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
    id: brightnessSettingsView
    anchors.fill: parent
    property int screenBrightness
    readonly property int maximumScreenBrightness: pmSource.data["PowerDevil"] ? pmSource.data["PowerDevil"]["Maximum Screen Brightness"] || 0 : 0
    
    
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
            text: "Brightness Settings"
            color: Kirigami.Theme.linkColor
        }
    }

    Item {
        anchors.top: topArea.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: areaSep.top
        
        RowLayout {
            anchors.centerIn: parent
            spacing: Kirigami.Units.largeSpacing
            property alias slider: slider
            
            Kirigami.Icon {
                id: leftIcon
                source: "contrast"
                Layout.preferredWidth: Kirigami.Units.iconSizes.large
                Layout.preferredHeight: Layout.preferredWidth
            }
            
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing
                
                Kirigami.Heading {
                    id: brightnessSettingLabel
                    level: 2
                    wrapMode: Text.WordWrap
                    font.bold: true
                    text: "Display Brightness"
                    color: Kirigami.Theme.textColor
                }
                
                Slider {
                    id: slider
                    Layout.fillWidth: true
                    
                    PlasmaCore.DataSource {
                        id: pmSource
                        engine: "powermanagement"
                        connectedSources: ["PowerDevil"]
                        onSourceAdded: {
                            if (source === "PowerDevil") {
                                disconnectSource(source);
                                connectSource(source);
                            }
                        }
                        onDataChanged: {
                            brightnessSettingsView.screenBrightness = pmSource.data["PowerDevil"]["Screen Brightness"];
                        }
                    }

                    value: brightnessSettingsView.screenBrightness
                    onMoved: {
                        var service = pmSource.serviceForSource("PowerDevil");
                        var operation = service.operationDescription("setBrightness");
                        operation.brightness = slider.value;
                        operation.silent = true
                        service.startOperationCall(operation);
                    }
                    from: slider.to > 100 ? 1 : 0
                    to: brightnessSettingsView.maximumScreenBrightness
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
