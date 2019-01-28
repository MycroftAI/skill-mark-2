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
    id: homeScreenSettingsView
    anchors.fill: parent
    property var modelItemList: mainLoaderView.idleScreenList
    
    onModelItemListChanged: {
       listIdleFaces.model = modelItemList.screenBlob
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
            text: "Homescreen Settings"
            color: Kirigami.Theme.linkColor
        }
    }

    Item {
        anchors.top: topArea.bottom
        anchors.topMargin: Kirigami.Units.largeSpacing
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: bottomArea.top
        
      ListView {
            id: listIdleFaces
            anchors.fill: parent
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            delegate: Kirigami.AbstractListItem {
                contentItem: Item {
                implicitWidth: delegateLayout.implicitWidth;
                implicitHeight: delegateLayout.implicitHeight;
                
                    ColumnLayout {
                        id: delegateLayout
                        anchors {
                            left: parent.left;
                            top: parent.top;
                            right: parent.right;
                        }
                    
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Math.round(units.gridUnit / 2)
                
                            Kirigami.Heading {
                                Layout.fillWidth: true
                                Layout.alignment: Qt.AlignHCenter
                                height: paintedHeight
                                elide: Text.ElideRight
                                font.weight: Font.DemiBold
                                text: modelData.screenName
                                textFormat: Text.PlainText
                                level: 2
                            }
                            
                            Kirigami.Icon {
                                id: selectedItemIcon
                                Layout.alignment: Qt.AlignVCenter | Qt.AlignRight
                                Layout.preferredHeight: units.iconSizes.medium
                                Layout.preferredWidth: units.iconSizes.medium
                                visible: model.activeFace
                                source: "answer"
                            }
                        }
                    }
                }
                
                onClicked: {
                    console.log(modelData.screenName)
                    sessionData.selected = modelData.screenName
                    model.activeFace = true // triggerEvent("device.activate.face", {"skillID": "idleFace"}) Requires API Logic
                }
            }
            
            Component.onCompleted: {
                listIdleFaces.count
            }
        }
    }
    Item {
        id: bottomArea
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: backIcon.implicitHeight + Kirigami.Units.largeSpacing
        
        Kirigami.Icon {
            id: backIcon
            source: "arrow-left"
            anchors.left: parent.left
            anchors.leftMargin: Kirigami.Units.largeSpacing
            width: Kirigami.Units.iconSizes.large
            height: implicitWidth
            
            MouseArea{
                anchors.fill: parent
                onClicked: {
                    triggerEvent("mycroft.device.settings", {})
                }
            }
        }
    }
} 
