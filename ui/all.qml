import QtQuick.Layouts 1.4
import QtQuick 2.4
import QtQuick.Controls 2.0
import org.kde.kirigami 2.5 as Kirigami
import Mycroft 1.0 as Mycroft

Mycroft.Delegate {
    id: mainLoaderView

    property var pageToLoad: sessionData.state
    property var securityType: sessionData.SecurityType
    property var connectionName: sessionData.ConnectionName
    property var devicePath: sessionData.DevicePath
    property var specificPath: sessionData.SpecificPath
    property var idleScreenList: sessionData.idleScreenList

    contentItem: Loader {
        id: rootLoader
    }

    onPageToLoadChanged: {
        console.log(sessionData.state)
        rootLoader.setSource(sessionData.state + ".qml")
    }
}
