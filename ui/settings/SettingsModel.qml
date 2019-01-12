import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.5 as Kirigami
import Mycroft 1.0 as Mycroft

ListModel {
    id: settingsListModel
    
    ListElement {
        settingIcon: "network-wireless"
        settingName: "Wi-Fi"
        settingEvent: "mycroft.device.settings.wireless"
        settingCall: "show wireless settings" 
    }
    ListElement {
        settingIcon: "contrast"
        settingName: "Brightness"
        settingEvent: "mycroft.device.settings.brightness"
        settingCall: "show brightness settings" 
    }
    ListElement {
        settingIcon: "go-home"
        settingName: "Homescreen"
        settingEvent: "mycroft.device.settings.homescreen"
        settingCall: "show homescreen settings"
    }
    ListElement {
        settingIcon: "dialog-scripts"
        settingName: "Enable SSH"
        settingEvent: "mycroft.device.settings.ssh"
        settingCall: "show ssh settings" 
    }
    ListElement {
        settingIcon: "circular-arrow-shape"
        settingName: "Factory Reset"
        settingEvent: "mycroft.device.settings.reset"
        settingCall: ""
    }
    ListElement {
        settingIcon: "download"
        settingName: "Update Device"
        settingEvent: "mycroft.device.settings.update"
        settingCall: "" 
    }
    ListElement {
        settingIcon: "view-refresh"
        settingName: "Reboot"
        settingEvent: "mycroft.device.settings.restart"
        settingCall: "" 
    }
    ListElement {
        settingIcon: "lighttable"
        settingName: "Shutdown"
        settingEvent: "mycroft.device.settings.poweroff"
        settingCall: "" 
    }
}
