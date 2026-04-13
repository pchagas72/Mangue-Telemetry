import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root

    // Signal to tell the main window to switch views
    signal loadTelemetry(string ipAddress)
    signal loadCAN()
    signal loadHarness()

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 40

        // Title
        ColumnLayout {
            spacing: 5
            Layout.alignment: Qt.AlignHCenter
            Text {
                text: "MANGUE BAJA"
                color: "#00FFFF"
                font.pixelSize: 36
                font.bold: true
                font.family: "Consolas"
                font.letterSpacing: 4
            }
            Text {
                text: "ENGINEERING SUITE v1.0"
                color: "#666666"
                font.pixelSize: 14
                font.family: "Consolas"
                font.letterSpacing: 2
                Layout.alignment: Qt.AlignHCenter
            }
        }

        // Connection Settings
        ColumnLayout {
            spacing: 10
            Layout.alignment: Qt.AlignHCenter
            
            Text { text: "TARGET IP ADDRESS"; color: "#a0a0a0"; font.pixelSize: 10; font.family: "Consolas" }
            
            TextField {
                id: ipInput
                text: "127.0.0.1" // Default localhost
                font.family: "Consolas"
                font.pixelSize: 16
                color: "#00FF00"
                Layout.preferredWidth: 300
                horizontalAlignment: TextInput.AlignHCenter
                background: Rectangle {
                    color: "#000000"
                    border.color: "#333333"
                    border.width: 1
                }
            }
        }

        // Tool Selection Buttons
        RowLayout {
            spacing: 20
            Layout.alignment: Qt.AlignHCenter

            Button {
                text: "TELEMETRY"
                Layout.preferredWidth: 140
                Layout.preferredHeight: 40
                onClicked: root.loadTelemetry(ipInput.text)
                background: Rectangle { color: "#1e1e1e"; border.color: "#00FFFF" }
                contentItem: Text { text: parent.text; color: "#00FFFF"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.family: "Consolas" }
            }

            Button {
                text: "CAN BUS"
                Layout.preferredWidth: 140
                Layout.preferredHeight: 40
                onClicked: root.loadCAN()
                background: Rectangle { color: "#1e1e1e"; border.color: "#FF3333" }
                contentItem: Text { text: parent.text; color: "#FF3333"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.family: "Consolas" }
            }

            Button {
                text: "HARNESS"
                Layout.preferredWidth: 140
                Layout.preferredHeight: 40
                onClicked: root.loadHarness()
                background: Rectangle { color: "#1e1e1e"; border.color: "#FFFF00" }
                contentItem: Text { text: parent.text; color: "#FFFF00"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; font.family: "Consolas" }
            }
        }
    }
}
