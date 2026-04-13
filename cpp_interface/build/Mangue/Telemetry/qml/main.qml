import QtQuick
import QtQuick.Controls
import Mangue.Telemetry

Window {
    id: mainWindow // Added ID to access from anywhere
    width: 1280
    height: 720
    visible: true
    title: "Engineering Suite"
    color: "#0a0a0a"

    Backend {
        id: appBackend
    }

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: MainMenu {
            
            // Inside qml/main.qml
            onLoadTelemetry: function(ipAddress) {
                appBackend.connectToServer("ws://" + ipAddress + ":8000/ws/telemetry")
                
                // ADD: "serverIp": ipAddress
                stackView.push("TelemetryDash.qml", { 
                    "backend": appBackend, 
                    "router": stackView,
                    "serverIp": ipAddress
                })
            }

            // Trigger the toast notification instead of just console.log
            onLoadCAN: showToast("CAN Interface not built yet", "#FF3333")
            onLoadHarness: showToast("Harness Interface not built yet", "#FFFF00")
        }
    }

    // --- GLOBAL WARNING BALLOON (TOAST) ---
    Rectangle {
        id: toast
        width: toastText.width + 40
        height: 40
        color: "#FF3333"
        radius: 4
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 20
        opacity: 0 // Hidden by default
        z: 100 // Ensures it renders over everything

        // Smooth fade in/out
        Behavior on opacity { NumberAnimation { duration: 250 } }

        Text {
            id: toastText
            anchors.centerIn: parent
            color: "#000000"
            font.family: "Consolas"
            font.bold: true
            font.pixelSize: 14
        }

        Timer {
            id: toastTimer
            interval: 3000 // Disappears after 3 seconds
            onTriggered: toast.opacity = 0
        }
    }

    // Function to trigger the toast from any screen
    function showToast(message, bgColor) {
        toastText.text = message
        toast.color = bgColor || "#FF3333"
        toast.opacity = 1
        toastTimer.restart()
    }
}
