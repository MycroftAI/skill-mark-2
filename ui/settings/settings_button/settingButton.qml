import QtQuick 2.4
import QtQuick.Controls 2.0

RadioButton {
    property string buttonId;
    property var skillevent;
    property var key;
    property var value;
    signal clicked(string skillevent, string key, string value);
    
    onCheckedChanged: {
        if(checked){
            clicked(skillevent, key, value)
        }
    }
}
