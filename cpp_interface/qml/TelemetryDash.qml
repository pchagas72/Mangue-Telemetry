import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtCharts
import QtQuick.Dialogs

Item {
    id: root
    property var backend
    property var router
    property string serverIp: "127.0.0.1"

    // Master X-Axis Time/Distance State
    property real sharedXMin: 0
    property real sharedXMax: 100
    property int timeTicks: 0
    signal xAxisModeChanged() 

    // Map/Lap Logic Properties
    property real minLat: 999; property real maxLat: -999
    property real minLon: 999; property real maxLon: -999
    property bool sfSet: false
    property real sfLat: 0; property real sfLon: 0
    property bool lapClosed: false
    property int sfSetTime: 0
    property int topZ: 1

    // FIX: A proper signal so dynamic maps know when S/F is updated
    signal sfLineUpdated()

    property var metricDef: {
        "Speed": { prop: "speed", max: 80, unit: "km/h", color: "#00FFFF" },
        "RPM": { prop: "rpm", max: 5000, unit: "RPM", color: "#00FF00" },
        "Voltage": { prop: "voltage", max: 15, unit: "V", color: "#FFFF00" },
        "Current": { prop: "current", max: 100, unit: "A", color: "#FF8800" },
        "Battery SOC": { prop: "soc", max: 100, unit: "%", color: "#FFFFFF" },
        "Motor Temp": { prop: "tempMotor", max: 120, unit: "°C", color: "#FF3333" },
        "CVT Temp": { prop: "tempCVT", max: 120, unit: "°C", color: "#FF8800" },
        "Acc X": { prop: "accX", max: 3, unit: "G", color: "#FF3333" },
        "Acc Y": { prop: "accY", max: 3, unit: "G", color: "#33FF33" },
        "Acc Z": { prop: "accZ", max: 3, unit: "G", color: "#3333FF" },
        "Roll": { prop: "roll", max: 45, unit: "°", color: "#00FFFF" },
        "Pitch": { prop: "pitch", max: 45, unit: "°", color: "#00FF00" }
    }
    property var availableMetrics: ["Speed", "RPM", "Voltage", "Current", "Battery SOC", "Motor Temp", "CVT Temp", "Acc X", "Acc Y", "Acc Z", "Roll", "Pitch"]

    function resetCharts() {
        if (modeTime.checked) { 
            sharedXMin = timeTicks; sharedXMax = timeTicks + 100 
        } else { 
            sharedXMin = backend.distance; sharedXMax = backend.distance + 50 
        }
        root.xAxisModeChanged() 
    }

    function haversine(lat1, lon1, lat2, lon2) {
        var R = 6371000
        var dLat = (lat2 - lat1) * Math.PI / 180
        var dLon = (lon2 - lon1) * Math.PI / 180
        var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2)
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
        return R * c
    }

    function setSFLine() {
        sfLat = backend.latitude; sfLon = backend.longitude
        sfSet = true; lapClosed = false; sfSetTime = timeTicks
        
        root.sfLineUpdated() // Broadcast to any active map widgets
        
        var xhr = new XMLHttpRequest()
        xhr.open("POST", "http://" + root.serverIp + ":8000/api/set-sf?lat=" + sfLat + "&lon=" + sfLon)
        xhr.send()
        console.log("[MAP] S/F Set. Waiting for closure...")
    }

    MessageDialog {
        id: sfConfirmDialog
        title: "Confirm S/F Change"
        text: "Are you sure you want to change the Start/Finish location?"
        buttons: MessageDialog.Yes | MessageDialog.No
        onButtonClicked: function(button, role) { if (button === MessageDialog.Yes) root.setSFLine() }
    }

    // =========================================================================
    // DYNAMIC WIDGET FACTORIES
    // =========================================================================

    component DraggableWindow: Rectangle {
        id: winRoot
        property string title: "Window"
        default property alias content: container.data 
        
        width: 450; height: 350; color: "#0a0a0a"; border.color: "#333"; border.width: 1
        x: 50 + (Math.random() * 100); y: 100 + (Math.random() * 100) 

        ColumnLayout {
            anchors.fill: parent; spacing: 0
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 30; color: "#1a1a1a"; border.color: "#333"; border.width: 1
                Text { text: winRoot.title; color: "#fff"; font.family: "Consolas"; font.bold: true; anchors.verticalCenter: parent.verticalCenter; anchors.left: parent.left; anchors.leftMargin: 10 }
                MouseArea { anchors.fill: parent; drag.target: winRoot }
                Button {
                    text: "✖"; anchors.right: parent.right; width: 40; anchors.top: parent.top; anchors.bottom: parent.bottom
                    background: Rectangle { color: parent.down ? "#FF3333" : "transparent" }
                    contentItem: Text { text: parent.text; color: "#fff"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    onClicked: winRoot.destroy() 
                }
            }
            Item { id: container; Layout.fillWidth: true; Layout.fillHeight: true }
        }
        MouseArea {
            width: 15; height: 15; anchors.right: parent.right; anchors.bottom: parent.bottom; cursorShape: Qt.SizeFDiagCursor
            property point clickPos
            onPressed: function(mouse) { clickPos = Qt.point(mouse.x, mouse.y) }
            onPositionChanged: function(mouse) {
                winRoot.width = Math.max(250, winRoot.width + (mouse.x - clickPos.x))
                winRoot.height = Math.max(200, winRoot.height + (mouse.y - clickPos.y))
            }
        }
        MouseArea { anchors.fill: parent; z: -1; onPressed: winRoot.z = ++root.topZ }
    }

    Component {
        id: factoryTrace
        DraggableWindow {
            property var metrics: []
            
            ChartView { 
                id: chart
                anchors.fill: parent; backgroundColor: "#000000"; plotAreaColor: "#0a0a0a"; legend.visible: true; legend.labelColor: "#fff"; margins { top: 0; bottom: 10; left: 10; right: 10 }
                
                ValueAxis { id: xTraceAxis; min: root.sharedXMin; max: root.sharedXMax; labelsColor: "#a0a0a0"; gridLineColor: "#333333" }
                ValueAxis { id: yTraceAxis; min: 0; max: 100; labelsColor: "#a0a0a0"; gridLineColor: "#1a1a1a" }
                
                property var seriesList: []

                Component.onCompleted: {
                    var localMax = 0
                    for (var i=0; i<metrics.length; i++) {
                        var m = root.metricDef[metrics[i]]
                        if (m.max > localMax) localMax = m.max
                        
                        var s = chart.createSeries(ChartView.SeriesTypeLine, metrics[i], xTraceAxis, yTraceAxis)
                        s.color = m.color; s.width = 2; s.useOpenGL = true
                        seriesList.push({ series: s, prop: m.prop })
                    }
                    yTraceAxis.max = localMax
                }

                Connections { target: root; function onXAxisModeChanged() { for(var i=0; i<chart.seriesList.length; i++) chart.seriesList[i].series.clear() } }

                Connections {
                    target: backend
                    function onTelemetryUpdated() {
                        var cx = modeTime.checked ? timeTicks : backend.distance
                        for(var i=0; i<chart.seriesList.length; i++) {
                            var item = chart.seriesList[i]
                            item.series.append(cx, backend[item.prop])
                            if (item.series.count > (modeTime.checked ? 150 : 300)) item.series.removePoints(0, 1)
                        }
                    }
                }
            }
        }
    }

    Component {
        id: factoryGauge
        DraggableWindow {
            property var metrics: []
            width: 300; height: Math.max(150, metrics.length * 60 + 40)
            
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 20; spacing: 15
                Repeater {
                    model: metrics
                    delegate: ColumnLayout {
                        property var mDef: root.metricDef[modelData]
                        property real liveVal: 0
                        
                        Connections { target: backend; function onTelemetryUpdated() { liveVal = backend[mDef.prop] } }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: modelData; color: "#a0a0a0"; font.pixelSize: 12; font.family: "Consolas"; font.bold: true; Layout.alignment: Qt.AlignLeft }
                            Text { text: liveVal.toFixed(1) + " " + mDef.unit; color: mDef.color; font.pixelSize: 14; font.family: "Consolas"; font.bold: true; Layout.alignment: Qt.AlignRight }
                        }
                        Rectangle {
                            Layout.fillWidth: true; Layout.preferredHeight: 12; color: "#1a1a1a"; border.color: "#333"; radius: 2
                            Rectangle {
                                height: parent.height; radius: 2; color: mDef.color
                                width: Math.max(0, Math.min(1, liveVal / mDef.max)) * parent.width 
                                Behavior on width { NumberAnimation { duration: 50 } }
                            }
                        }
                    }
                }
                Item { Layout.fillHeight: true } 
            }
        }
    }

    Component {
        id: factoryNumber
        DraggableWindow {
            property var metrics: []
            width: 350; height: 200
            
            GridLayout {
                anchors.fill: parent; anchors.margins: 20; columns: 2; rowSpacing: 20; columnSpacing: 30
                Repeater {
                    model: metrics
                    delegate: ColumnLayout {
                        property var mDef: root.metricDef[modelData]
                        property real liveVal: 0
                        
                        Connections { target: backend; function onTelemetryUpdated() { liveVal = backend[mDef.prop] } }
                        
                        Text { text: modelData.toUpperCase(); color: "#666666"; font.pixelSize: 12; font.family: "Consolas" }
                        RowLayout {
                            Text { text: liveVal.toFixed(1); color: mDef.color; font.pixelSize: 36; font.bold: true; font.family: "Consolas" }
                            Text { text: mDef.unit; color: "#444444"; font.pixelSize: 14; font.family: "Consolas"; Layout.alignment: Qt.AlignBottom | Qt.AlignLeft; Layout.bottomMargin: 6 }
                        }
                    }
                }
            }
        }
    }

    Component {
        id: factoryMap
        DraggableWindow {
            title: "GPS Track & Live Position"
            width: 400; height: 400
            
            // FIX: Map immediately shows the flag if spawned after S/F is already set
            Component.onCompleted: {
                if (root.sfSet) sfMarker.append(root.sfLon, root.sfLat)
            }

            ChartView {
                anchors.fill: parent; backgroundColor: "#000000"; plotAreaColor: "#111"; legend.visible: false; margins { top: 10; bottom: 10; left: 10; right: 10 }
                ValueAxis { id: xMap; min: root.minLon; max: root.maxLon; labelsVisible: false; gridVisible: false }
                ValueAxis { id: yMap; min: root.minLat; max: root.maxLat; labelsVisible: false; gridVisible: false }
                
                SplineSeries { id: gpsTrace; axisX: xMap; axisY: yMap; color: "#FFFFFF"; width: 3; useOpenGL: true }
                ScatterSeries { id: sfMarker; axisX: xMap; axisY: yMap; color: "#00FF00"; markerSize: 15; useOpenGL: true }
                ScatterSeries { id: carMarker; axisX: xMap; axisY: yMap; color: "#FF3333"; markerSize: 12; useOpenGL: true }
                
                // FIX: Listens to the root signal properly so it resets the trace correctly
                Connections {
                    target: root
                    function onSfLineUpdated() {
                        sfMarker.clear()
                        sfMarker.append(root.sfLon, root.sfLat)
                        gpsTrace.clear()
                    }
                }

                Connections {
                    target: backend
                    function onTelemetryUpdated() {
                        if (backend.latitude !== 0 && backend.longitude !== 0) {
                            if (backend.latitude < root.minLat || root.minLat === 999) root.minLat = backend.latitude - 0.0001
                            if (backend.latitude > root.maxLat || root.maxLat === -999) root.maxLat = backend.latitude + 0.0001
                            if (backend.longitude < root.minLon || root.minLon === 999) root.minLon = backend.longitude - 0.0001
                            if (backend.longitude > root.maxLon || root.maxLon === -999) root.maxLon = backend.longitude + 0.0001
                            
                            carMarker.clear()
                            carMarker.append(backend.longitude, backend.latitude)

                            if (root.sfSet && !root.lapClosed) {
                                var dist = root.haversine(root.sfLat, root.sfLon, backend.latitude, backend.longitude)
                                if (dist <= 2.5 && (timeTicks - root.sfSetTime > 150)) root.lapClosed = true
                            }
                            if (!root.lapClosed) gpsTrace.append(backend.longitude, backend.latitude)
                        }
                    }
                }
            }
        }
    }

    Component {
        id: factoryDynamics
        DraggableWindow {
            title: "Vehicle Dynamics"; width: 350; height: 400
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 20; spacing: 20
                
                Item {
                    Layout.fillWidth: true; Layout.preferredHeight: width
                    Rectangle {
                        anchors.centerIn: parent; width: parent.width - 20; height: width; radius: width / 2; color: "transparent"; border.color: "#333"; border.width: 2
                        Rectangle { anchors.centerIn: parent; width: parent.width; height: 1; color: "#333" }
                        Rectangle { anchors.centerIn: parent; width: 1; height: parent.height; color: "#333" }
                        Rectangle {
                            width: 12; height: 12; radius: 6; color: "#FF3333"
                            x: (parent.width / 2) + (backend.accX / 3.0 * (parent.width / 2)) - (width / 2)
                            y: (parent.height / 2) - (backend.accY / 3.0 * (parent.height / 2)) - (height / 2)
                            Behavior on x { NumberAnimation { duration: 33 } }
                            Behavior on y { NumberAnimation { duration: 33 } }
                        }
                    }
                    Text { text: "G-FORCE"; color: "#666"; font.pixelSize: 10; font.family: "Consolas"; anchors.bottom: parent.bottom; anchors.horizontalCenter: parent.horizontalCenter }
                }

                // FIX: ColumnLayout ensures labels sit perfectly above the bars
                RowLayout {
                    Layout.fillWidth: true; Layout.preferredHeight: 80; spacing: 20
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        Text { text: "ROLL: " + backend.roll.toFixed(1) + "°"; color: "#a0a0a0"; font.family: "Consolas"; font.pixelSize: 10; Layout.alignment: Qt.AlignHCenter }
                        Item {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            Rectangle { width: 40; height: 10; color: "#00FFFF"; radius: 2; anchors.centerIn: parent; rotation: backend.roll; Behavior on rotation { NumberAnimation { duration: 33 } } }
                        }
                    }
                    
                    ColumnLayout {
                        Layout.fillWidth: true
                        Text { text: "PITCH: " + backend.pitch.toFixed(1) + "°"; color: "#a0a0a0"; font.family: "Consolas"; font.pixelSize: 10; Layout.alignment: Qt.AlignHCenter }
                        Item {
                            Layout.fillWidth: true; Layout.fillHeight: true
                            Rectangle { width: 60; height: 10; color: "#00FF00"; radius: 2; anchors.centerIn: parent; rotation: -backend.pitch; Behavior on rotation { NumberAnimation { duration: 33 } } }
                        }
                    }
                }
            }
        }
    }

    // =========================================================================
    // WIDGET CREATOR POPUP
    // =========================================================================
    Popup {
        id: widgetCreator
        anchors.centerIn: parent
        width: 600; height: 450
        modal: true
        background: Rectangle { color: "#111"; border.color: "#333"; border.width: 1; radius: 4 }
        
        property string selectedType: "Trace"
        
        ColumnLayout {
            anchors.fill: parent; anchors.margins: 20; spacing: 20
            
            Text { text: "WIDGET CREATOR"; color: "#00FFFF"; font.pixelSize: 20; font.family: "Consolas"; font.bold: true; Layout.alignment: Qt.AlignHCenter }
            
            RowLayout {
                Layout.alignment: Qt.AlignHCenter; spacing: 15
                RadioButton { text: "Trace Graph"; checked: true; onCheckedChanged: if(checked) widgetCreator.selectedType = "Trace"; contentItem: Text { text: parent.text; color: "white"; font.family: "Consolas"; leftPadding: 25; verticalAlignment: Text.AlignVCenter } }
                RadioButton { text: "Bar Gauges"; onCheckedChanged: if(checked) widgetCreator.selectedType = "Gauge"; contentItem: Text { text: parent.text; color: "white"; font.family: "Consolas"; leftPadding: 25; verticalAlignment: Text.AlignVCenter } }
                RadioButton { text: "Numbers"; onCheckedChanged: if(checked) widgetCreator.selectedType = "Number"; contentItem: Text { text: parent.text; color: "white"; font.family: "Consolas"; leftPadding: 25; verticalAlignment: Text.AlignVCenter } }
                RadioButton { text: "GPS Map"; onCheckedChanged: if(checked) widgetCreator.selectedType = "Map"; contentItem: Text { text: parent.text; color: "white"; font.family: "Consolas"; leftPadding: 25; verticalAlignment: Text.AlignVCenter } }
                RadioButton { text: "Dynamics"; onCheckedChanged: if(checked) widgetCreator.selectedType = "Dynamics"; contentItem: Text { text: parent.text; color: "white"; font.family: "Consolas"; leftPadding: 25; verticalAlignment: Text.AlignVCenter } }
            }
            
            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 1; color: "#333" }

            GridLayout {
                id: metricGrid
                visible: widgetCreator.selectedType === "Trace" || widgetCreator.selectedType === "Gauge" || widgetCreator.selectedType === "Number"
                Layout.fillWidth: true; Layout.fillHeight: true
                columns: 3; rowSpacing: 10; columnSpacing: 10
                
                Repeater {
                    id: metricRepeater
                    model: root.availableMetrics
                    delegate: CheckBox {
                        text: modelData
                        contentItem: Text { text: parent.text; color: root.metricDef[modelData].color; font.family: "Consolas"; leftPadding: 30; verticalAlignment: Text.AlignVCenter }
                    }
                }
            }

            Item { Layout.fillHeight: true; visible: !metricGrid.visible } 

            Button {
                Layout.alignment: Qt.AlignHCenter; Layout.preferredWidth: 200; Layout.preferredHeight: 40
                text: "CREATE WIDGET"
                background: Rectangle { color: "#004d00"; border.color: "#00FF00"; radius: 4 }
                contentItem: Text { text: parent.text; color: "#fff"; font.bold: true; font.family: "Consolas"; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                
                onClicked: {
                    var win = null;
                    if (widgetCreator.selectedType === "Map") win = factoryMap.createObject(desktopArea)
                    else if (widgetCreator.selectedType === "Dynamics") win = factoryDynamics.createObject(desktopArea)
                    else {
                        var selected = []
                        for (var i = 0; i < metricRepeater.count; i++) {
                            if (metricRepeater.itemAt(i).checked) selected.push(root.availableMetrics[i])
                        }
                        if (selected.length === 0) return 
                        
                        var titleStr = widgetCreator.selectedType + ": " + selected.join(", ")
                        if (widgetCreator.selectedType === "Trace") win = factoryTrace.createObject(desktopArea, { title: titleStr, metrics: selected })
                        if (widgetCreator.selectedType === "Gauge") win = factoryGauge.createObject(desktopArea, { title: titleStr, metrics: selected })
                        if (widgetCreator.selectedType === "Number") win = factoryNumber.createObject(desktopArea, { title: titleStr, metrics: selected })
                        
                        for (var j = 0; j < metricRepeater.count; j++) metricRepeater.itemAt(j).checked = false
                    }
                    
                    if (win) { win.visible = true; win.z = ++root.topZ }
                    widgetCreator.close()
                }
            }
        }
    }

    // =========================================================================
    // MAIN LAYOUT
    // =========================================================================

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 45
            color: "#111111"
            border.color: "#333333"
            border.width: 1
            
            RowLayout {
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: 10
                spacing: 15
                
                Button { 
                    text: "◀ EXIT"
                    onClicked: { backend.disconnectFromServer(); router.pop() }
                    background: Rectangle { color: "transparent" }
                    contentItem: Text { text: parent.text; color: "#a0a0a0"; font.family: "Consolas"; font.bold: true } 
                }
                
                Rectangle { width: 1; height: 25; color: "#333" }
                
                Button {
                    text: "➕ ADD WIDGET"
                    onClicked: widgetCreator.open()
                    background: Rectangle { color: "#1e1e1e"; border.color: "#00FFFF"; radius: 4 }
                    contentItem: Text { text: parent.text; color: "#00FFFF"; font.family: "Consolas"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                }
                
                Rectangle { width: 1; height: 25; color: "#333" }
                
                RowLayout {
                    spacing: 10
                    Text { text: "X-AXIS:"; color: "#a0a0a0"; font.family: "Consolas"; font.bold: true }
                    
                    RadioButton { 
                        id: modeTime
                        text: "Time"
                        checked: true
                        contentItem: Text { text: parent.text; color: "white"; font.family: "Consolas"; leftPadding: 25; verticalAlignment: Text.AlignVCenter }
                        onCheckedChanged: if(checked) root.resetCharts() 
                    }
                    
                    RadioButton { 
                        id: modeDist
                        text: "Dist"
                        contentItem: Text { text: parent.text; color: "white"; font.family: "Consolas"; leftPadding: 25; verticalAlignment: Text.AlignVCenter }
                        onCheckedChanged: if(checked) root.resetCharts() 
                    }
                }
            }

            Button {
                anchors.centerIn: parent
                text: root.sfSet ? "⚑ UPDATE S/F LINE" : "⚑ SET S/F LINE"
                onClicked: root.sfSet ? sfConfirmDialog.open() : root.setSFLine()
                background: Rectangle { color: "#2d2d2d"; border.color: root.sfSet ? "#00FF00" : "#555"; radius: 4 }
                contentItem: Text { text: parent.text; color: root.sfSet ? "#00FF00" : "#FFFFFF"; font.family: "Consolas"; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
            }

            RowLayout {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.margins: 15
                spacing: 20
                
                Text { 
                    text: "LAP " + backend.lapCount + " | " + (backend.currentLapTime / 1000).toFixed(2) + "s"
                    color: "#FFFFFF"; font.family: "Consolas"; font.bold: true; font.pixelSize: 16 
                }
                
                Text { 
                    text: backend.connectionStatus === "Connected" ? "● LIVE STREAM" : "○ OFFLINE"
                    color: backend.connectionStatus === "Connected" ? "#00FF00" : "#FF3333"
                    font.family: "Consolas"; font.bold: true 
                }
            }
        }

        Item {
            id: desktopArea
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            // FIX: Master scroll logic restored!
            Connections {
                target: backend
                function onTelemetryUpdated() {
                    timeTicks++
                    
                    var currentX = modeTime.checked ? timeTicks : backend.distance
                    var windowSize = modeTime.checked ? 100 : 50
                    
                    if (currentX > root.sharedXMax) {
                        root.sharedXMax = currentX
                        root.sharedXMin = currentX - windowSize
                    }
                }
            }
        }
    }
}
