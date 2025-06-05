import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtCharts 2.15

Item {
    id: root

    property bool controllerReady: false
    property color primaryColor: "#6c5ce7" // Основной цвет (синий) для акцентов
    property color accentColor: "#fd79a8" // Розовый акцент
    property color textColor: "#2d3436" // Тёмный текст
    property color backgroundColor: "#f5f6fa" // Фоновый цвет
    property color cardColor: "#ffffff" // Цвет карточек
    property color borderColor: "#dfe6e9" // Цвет границ

    // Новые цвета для секций
    property color section1Color: "#f0f2f5"  // Очень светлый голубовато-серый
    property color section2Color: "#f5f0f2"  // Очень светлый розовато-серый
    property color section3Color: "#f2f5f0"  // Очень светлый зеленовато-серый

    Timer {
        id: initTimer
        interval: 100
        repeat: false
        running: true
        onTriggered: {
            if (timeController) {
                console.log("timeController is ready, initializing...")
                rangeSlider.first.value = 0
                rangeSlider.second.value = timeController.maxIntervalDays
                timeController.setIntervalRange(0, timeController.maxIntervalDays)
                controllerReady = true
            } else {
                console.log("timeController is still not available, retrying...")
                initTimer.restart()
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10
        anchors.margins: 20

        Rectangle {
            id: dateRangeCard
            Layout.fillWidth: true
            height: 80
            radius: 12
            color: cardColor
            border.color: Qt.darker(cardColor, 1.1)
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5

                Label {
                    text: "Date Range"
                    font.pixelSize: 16
                    font.bold: true
                    color: textColor
                    Layout.alignment: Qt.AlignHCenter
                }

                RangeSlider {
                    id: rangeSlider
                    Layout.fillWidth: true
                    from: 0
                    to: timeController ? timeController.maxIntervalDays : 30
                    first.value: 0
                    second.value: timeController ? timeController.maxIntervalDays : 25
                    stepSize: 1
                    snapMode: RangeSlider.SnapAlways

                    first.onMoved: if (timeController) timeController.setIntervalRange(Math.floor(first.value), Math.floor(second.value))
                    second.onMoved: if (timeController) timeController.setIntervalRange(Math.floor(first.value), Math.floor(second.value))

                    background: Rectangle {
                        x: rangeSlider.leftPadding
                        y: rangeSlider.topPadding + rangeSlider.availableHeight / 2 - height / 2
                        implicitWidth: 200
                        implicitHeight: 4
                        width: rangeSlider.availableWidth
                        height: implicitHeight
                        radius: 2
                        color: "#e0e0e0"

                        Rectangle {
                            x: rangeSlider.first.visualPosition * parent.width
                            width: rangeSlider.second.visualPosition * parent.width - x
                            height: parent.height
                            radius: 2
                            color: primaryColor
                        }
                    }

                    first.handle: Rectangle {
                        x: rangeSlider.leftPadding + rangeSlider.first.visualPosition * (rangeSlider.availableWidth - width)
                        y: rangeSlider.topPadding + rangeSlider.availableHeight / 2 - height / 2
                        implicitWidth: 20
                        implicitHeight: 20
                        radius: 10
                        color: rangeSlider.first.pressed ? Qt.darker(primaryColor, 1.2) : primaryColor
                        border.color: Qt.darker(primaryColor, 1.3)

                        Label {
                            anchors.centerIn: parent
                            text: Math.floor(rangeSlider.first.value)
                            font.pixelSize: 10
                            color: "white"
                        }
                    }

                    second.handle: Rectangle {
                        x: rangeSlider.leftPadding + rangeSlider.second.visualPosition * (rangeSlider.availableWidth - width)
                        y: rangeSlider.topPadding + rangeSlider.availableHeight / 2 - height / 2
                        implicitWidth: 20
                        implicitHeight: 20
                        radius: 10
                        color: rangeSlider.second.pressed ? Qt.darker(primaryColor, 1.2) : primaryColor
                        border.color: Qt.darker(primaryColor, 1.3)

                        Label {
                            anchors.centerIn: parent
                            text: Math.floor(rangeSlider.second.value)
                            font.pixelSize: 10
                            color: "white"
                        }
                    }
                }

                Label {
                    text: timeController ?
                          Qt.formatDate(new Date(timeController.startDate), "dd MMM yyyy") + " — " +
                          Qt.formatDate(new Date(timeController.endDate), "dd MMM yyyy") : "Loading..."
                    font.pixelSize: 14
                    Layout.alignment: Qt.AlignHCenter
                    color: Qt.darker(textColor, 1.2)
                }
            }
        }

        ScrollView {
            id: scrollView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded

            ColumnLayout {
                width: scrollView.width - 40
                spacing: 0

                // Секция 1: Основная статистика и рекорды
                Rectangle {
                    Layout.fillWidth: true
                    Layout.topMargin: 10
                    implicitHeight: mainStatsLayout.implicitHeight + 40
                    color: section1Color
                    radius: 12
                    clip: true

                    ColumnLayout {
                        id: mainStatsLayout
                        width: parent.width
                        spacing: 10
                        anchors.centerIn: parent

                        RowLayout {
                            spacing: 20

                            // Main Statistics (левая колонка)
                            ColumnLayout {
                                Layout.preferredWidth: 30
                                spacing: 10

                                Label {
                                    text: "Main Statistics"
                                    font.pixelSize: 20
                                    font.bold: true
                                    color: textColor
                                    Layout.alignment: Qt.AlignLeft
                                }

                                Repeater {
                                    model: [
                                        { text: timeController ? "Total Playtime: " + timeController.totalFullPlaytime.toFixed(1) + " hours" : "Total Playtime: N/A", size: 16, icon: "⏱️" },
                                        { text: timeController ? "Average Session Time: " + timeController.avgSessionTime + " hours" : "Average Session Time: N/A", size: 16, icon: "⏳" },
                                        { text: timeController ? "Average Day Playtime: " + timeController.avgDayPlaytime.toFixed(1) + " hours" : "Average Day Playtime: N/A", size: 16, icon: "📅" },
                                        { text: timeController ? "Total Sessions: " + timeController.fullSessionCount : "Total Sessions: N/A", size: 16, icon: "🔄" }
                                    ]

                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 70
                                        radius: 8
                                        color: cardColor
                                        border.color: borderColor
                                        border.width: 1
                                        gradient: Gradient {
                                            GradientStop { position: 0.0; color: "#f5f7fa" }
                                            GradientStop { position: 1.0; color: "#dfe4ea" }
                                        }

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 10

                                            Rectangle {
                                                width: 40
                                                height: 40
                                                radius: 20
                                                color: Qt.rgba(0, 0, 0, 0.1)

                                                Label {
                                                    anchors.centerIn: parent
                                                    text: modelData.icon
                                                    font.pixelSize: 18
                                                }
                                            }

                                            ColumnLayout {
                                                spacing: 2
                                                Layout.fillWidth: true

                                                Label {
                                                    text: modelData.text.split(":")[0] + ":"
                                                    font.pixelSize: modelData.size - 2
                                                    color: Qt.darker(textColor, 1.3)
                                                    elide: Text.ElideRight
                                                }

                                                Label {
                                                    text: modelData.text.split(":")[1] || "N/A"
                                                    font.pixelSize: modelData.size
                                                    font.bold: true
                                                    color: textColor
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            // Records (правая колонка)
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 10

                                Label {
                                    text: "Records 🏆"
                                    font.pixelSize: 20
                                    font.bold: true
                                    color: accentColor
                                    Layout.alignment: Qt.AlignLeft
                                }

                                Repeater {
                                    model: [
                                        { text: timeController && timeController.maxSessionDuration ?
                                                "Max Session Duration: " + timeController.maxSessionDuration[0].toFixed(1) +
                                                " hours (Date: " + timeController.maxSessionDuration[2] +
                                                ", Game: " + timeController.maxSessionDuration[1] + ")" : "Max Session Duration: N/A", icon: "🏆" },
                                        { text: timeController && timeController.maxDailyGameSession ?
                                                "Max Daily Game Session: " + timeController.maxDailyGameSession[0].toFixed(1) +
                                                " hours (Date: " + timeController.maxDailyGameSession[1] +
                                                ", Game: " + timeController.maxDailyGameSession[2] +
                                                ", Sessions: " + timeController.maxDailyGameSession[3] + ")" : "Max Daily Game Session: N/A", icon: "📅" },
                                        { text: timeController && timeController.maxDailyTotalDuration ?
                                                "Max Daily Total Duration: " + timeController.maxDailyTotalDuration[0].toFixed(1) +
                                                " hours (Date: " + timeController.maxDailyTotalDuration[1] +
                                                ", Games: " + timeController.maxDailyTotalDuration[2] + ")" : "Max Daily Total Duration: N/A", icon: "⏰" },
                                        { text: !timeController || !timeController.maxConsecutiveDays ? "Max Consecutive Gaming Days: N/A" :
                                                (function() {
                                                    var streak = timeController.maxConsecutiveDays[0];
                                                    var start = timeController.maxConsecutiveDays[1];
                                                    var end = timeController.maxConsecutiveDays[2];
                                                    return streak > 0 ? "Max Consecutive Gaming Days: " + streak + " (From " + end + " to " + start + ")" :
                                                                       "Max Consecutive Gaming Days: 0 (No consecutive days found)";
                                                })(), icon: "🔥" }
                                    ]

                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 70
                                        radius: 8
                                        color: cardColor
                                        border.color: borderColor
                                        border.width: 1
                                        gradient: Gradient {
                                            GradientStop { position: 0.0; color: "#f5f7fa" }
                                            GradientStop { position: 1.0; color: "#dfe4ea" }
                                        }

                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: 10
                                            spacing: 10

                                            Rectangle {
                                                width: 40
                                                height: 40
                                                radius: 20
                                                color: Qt.rgba(0, 0, 0, 0.1)

                                                Label {
                                                    anchors.centerIn: parent
                                                    text: modelData.icon
                                                    font.pixelSize: 18
                                                }
                                            }

                                            Label {
                                                text: modelData.text
                                                font.pixelSize: 14
                                                color: textColor
                                                wrapMode: Text.WordWrap
                                                Layout.fillWidth: true
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // Секция 2: Графики и топ игр
                Rectangle {
                    Layout.fillWidth: true
                    Layout.topMargin: 10
                    implicitHeight: chartsLayout.implicitHeight + 40
                    color: section2Color
                    radius: 12
                    clip: true

                    ColumnLayout {
                        id: chartsLayout
                        width: parent.width
                        spacing: 10
                        anchors.centerIn: parent

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 20

                            // Топ игр (левая часть)
                            Rectangle {
                                Layout.fillWidth : true
                                height: 386
                                color: section2Color
                                radius: 8


                                ColumnLayout {
                                    anchors.fill: parent
                                    anchors.margins: 15
                                    spacing: 10

                                    Label {
                                        text: "Top Games"
                                        font.pixelSize: 20
                                        font.bold: true
                                        Layout.alignment: Qt.AlignHCenter
                                    }

                                    Repeater {
                                        model: timeController ? timeController.topGames : []

                                        Rectangle {
                                            Layout.fillWidth: true
                                            height: 40
                                            radius: 5
                                            color: index % 2 === 0 ? Qt.lighter(cardColor, 1.05) : cardColor
                                            border.color: borderColor
                                            border.width: 1

                                            RowLayout {
                                                anchors.fill: parent
                                                anchors.margins: 5
                                                spacing: 10

                                                Label {
                                                    text: modelData ? (index + 1) + "." : ""
                                                    font.pixelSize: 14
                                                    color: textColor
                                                }

                                                Label {
                                                    text: modelData ? modelData[0] : "N/A"
                                                    font.pixelSize: 14
                                                    color: textColor
                                                    Layout.fillWidth: true
                                                    elide: Text.ElideRight
                                                }

                                                Label {
                                                    text: modelData ? modelData[1].toFixed(1) + "h" : ""
                                                    font.pixelSize: 14
                                                    font.bold: true
                                                    color: primaryColor
                                                }
                                            }
                                        }
                                    }

                                    Item {
                                        Layout.fillHeight: true
                                    }
                                }
                            }

                            // Круговая диаграмма (левая часть)
                            ChartView {
                                Layout.preferredWidth: 900
                                height: 400
                                antialiasing: true
                                backgroundColor: section2Color
                                legend.visible: false
                                legend.alignment: Qt.AlignRight
                                legend.font.pixelSize: 14
                                margins.right: 30

                                PieSeries {
                                    id: pieSeries
                                    visible: controllerReady && timeController && timeController.pieChartData && timeController.pieChartData.length > 0 && timeController.pieChartData[0][0] !== "No Data"
                                    function updateSlices() {
                                        if (!timeController || !timeController.pieChartData) {
                                            console.log("Cannot update PieSeries: timeController or pieChartData is null")
                                            return
                                        }
                                        pieSeries.clear()
                                        var data = timeController.pieChartData
                                        for (var i = 0; i < data.length; i++) {
                                            var name = data[i][0]
                                            var hours = data[i][1]
                                            var percent = timeController.totalFullPlaytime > 0 ? (hours / timeController.totalFullPlaytime * 100).toFixed(1) : 0
                                            var label = name + ": " + hours.toFixed(1) + "h (" + percent + "%)"
                                            var value = hours > 0 ? hours : 0.001
                                            pieSeries.append(label, value)
                                            pieSeries.at(i).color = name === "No Data" ? "#cccccc" : Qt.hsla(i / data.length, 0.7, 0.5, 1.0)
                                            pieSeries.at(i).labelPosition = PieSlice.LabelOutside
                                            pieSeries.at(i).labelFont.pixelSize = 10
                                            pieSeries.at(i).labelArmLengthFactor = 0.3
                                            pieSeries.at(i).labelVisible = true
                                            pieSeries.at(i).borderWidth = 1
                                            pieSeries.at(i).borderColor = "black"
                                        }
                                    }

                                    Component.onCompleted: {
                                        if (controllerReady) {
                                            updateSlices()
                                        }
                                    }

                                    Connections {
                                        target: timeController
                                        function onIntervalChanged() {
                                            pieSeries.updateSlices()
                                        }
                                    }
                                }

                                Rectangle {
                                    visible: !controllerReady || !timeController || !timeController.pieChartData || timeController.pieChartData.length === 0 || timeController.pieChartData[0][0] === "No Data"
                                    width: parent.width
                                    height: parent.height
                                    color: "white"

                                    Text {
                                        anchors.centerIn: parent
                                        text: "🎮 No gaming today! Time to play? 😄"
                                        font.pixelSize: 16
                                        color: "black"
                                    }
                                }
                            }
                        }
                    }
                }

                // Секция 3: Гистограммы
                Rectangle {
                    Layout.fillWidth: true
                    Layout.topMargin: 10
                    Layout.bottomMargin: 10
                    implicitHeight: histogramsLayout.implicitHeight + 40
                    color: section3Color
                    radius: 12
                    clip: true

                    ColumnLayout {
                        id: histogramsLayout
                        width: parent.width
                        spacing: 10
                        anchors.centerIn: parent

                        // Заголовки для гистограмм
                        RowLayout {
                            spacing: 150
                            Layout.alignment: Qt.AlignHCenter

                            Label {
                                text: "Playtime by Day of Week:"
                                font.pixelSize: 20
                                font.bold: true
                                Layout.alignment: Qt.AlignHCenter
                            }

                            Label {
                                text: "Playtime by Time of Day:"
                                font.pixelSize: 20
                                font.bold: true
                                Layout.alignment: Qt.AlignHCenter
                            }
                        }

                        // Гистограммы в одном ряду
                        RowLayout {
                            spacing: 50
                            Layout.alignment: Qt.AlignHCenter

                            // Первая гистограмма: Playtime by Day of Week
                            ColumnLayout {
                                spacing: 10

                                RowLayout {
                                    spacing: 20

                                    Canvas {
                                        id: histogramCanvas
                                        width: 500
                                        height: 300
                                        Layout.alignment: Qt.AlignLeft

                                        property var playtime: controllerReady && timeController ? timeController.playtimeByDayOfWeek : [0, 0, 0, 0, 0, 0, 0]
                                        property var dayNames: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

                                        onPlaytimeChanged: {
                                            if (controllerReady) {
                                                requestPaint()
                                            }
                                        }

                                        onPaint: {
                                            var ctx = getContext("2d");
                                            ctx.reset();

                                            var maxValue = Math.max(...playtime);
                                            if (maxValue === 0) maxValue = 1;

                                            var barWidth = width / 8;
                                            var margin = barWidth;
                                            var heightScale = (height - 30) / maxValue;

                                            ctx.beginPath();
                                            ctx.moveTo(margin, height - 20);
                                            ctx.lineTo(width - margin / 2, height - 20);
                                            ctx.strokeStyle = "#000000";
                                            ctx.stroke();

                                            ctx.font = "14px sans-serif";
                                            ctx.fillStyle = "#000";
                                            ctx.textAlign = "center";
                                            for (var i = 0; i < 7; i++) {
                                                var x = margin + (i + 0.5) * barWidth;
                                                ctx.fillText(dayNames[i], x, height - 5);
                                            }

                                            ctx.beginPath();
                                            ctx.moveTo(margin, 10);
                                            ctx.lineTo(margin, height - 20);
                                            ctx.stroke();

                                            ctx.font = "12px sans-serif";
                                            ctx.textAlign = "right";
                                            ctx.fillText(maxValue.toFixed(1) + "h", margin - 10, 15);
                                            ctx.fillText("0h", margin - 10, height - 20);

                                            for (var j = 0; j < 7; j++) {
                                                var playtimeIndex = (j + 1) % 7;
                                                var barHeight = playtime[playtimeIndex] * heightScale;
                                                var xPos = margin + j * barWidth;
                                                ctx.fillStyle = "#4CAF50";
                                                ctx.fillRect(xPos, height - 20 - barHeight, barWidth - 5, barHeight);
                                            }
                                        }
                                    }

                                    ColumnLayout {
                                        spacing: 5
                                        Layout.alignment: Qt.AlignTop

                                        Repeater {
                                            model: ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
                                            Label {
                                                text: controllerReady && timeController ? modelData + ": " + timeController.playtimeByDayOfWeek[(index + 1) % 7].toFixed(1) + " hours" : modelData + ": N/A"
                                                font.pixelSize: 18
                                                Layout.alignment: Qt.AlignLeft
                                            }
                                        }
                                    }
                                }
                            }

                            // Вторая гистограмма: Playtime by Time of Day
                            ColumnLayout {
                                spacing: 10

                                RowLayout {
                                    spacing: 20

                                    Canvas {
                                        id: timeOfDayHistogramCanvas
                                        width: 400
                                        height: 200
                                        Layout.alignment: Qt.AlignLeft

                                        property var playtime: controllerReady && timeController ? timeController.playtimeByTimeOfDay : [0, 0, 0, 0]
                                        property var timeNames: ["Morning", "Afternoon", "Evening", "Night"]

                                        onPlaytimeChanged: {
                                            if (controllerReady) {
                                                requestPaint()
                                            }
                                        }

                                        onPaint: {
                                            var ctx = getContext("2d");
                                            ctx.reset();

                                            var maxValue = Math.max(...playtime);
                                            if (maxValue === 0) maxValue = 1;

                                            var barWidth = width / 5;
                                            var margin = barWidth;
                                            var heightScale = (height - 30) / maxValue;

                                            ctx.beginPath();
                                            ctx.moveTo(margin, height - 20);
                                            ctx.lineTo(width - margin / 2, height - 20);
                                            ctx.strokeStyle = "#000000";
                                            ctx.stroke();

                                            ctx.font = "14px sans-serif";
                                            ctx.fillStyle = "#000000";
                                            ctx.textAlign = "center";
                                            for (var i = 0; i < 4; i++) {
                                                var x = margin + (i + 0.5) * barWidth;
                                                ctx.fillText(timeNames[i], x, height - 5);
                                            }

                                            ctx.beginPath();
                                            ctx.moveTo(margin, 10);
                                            ctx.lineTo(margin, height - 20);
                                            ctx.stroke();

                                            ctx.font = "12px sans-serif";
                                            ctx.textAlign = "right";
                                            ctx.fillText(maxValue.toFixed(1) + "h", margin - 10, 15);
                                            ctx.fillText("0h", margin - 10, height - 20);

                                            for (var j = 0; j < 4; j++) {
                                                var barHeight = playtime[j] * heightScale;
                                                var xPos = margin + j * barWidth;
                                                ctx.fillStyle = "#2196F3";
                                                ctx.fillRect(xPos, height - 20 - barHeight, barWidth - 5, barHeight);
                                            }
                                        }
                                    }

                                    ColumnLayout {
                                        spacing: 5
                                        Layout.alignment: Qt.AlignTop

                                        Repeater {
                                            model: ["Morning", "Afternoon", "Evening", "Night"]
                                            Label {
                                                text: controllerReady && timeController && timeController.playtimeByTimeOfDay ? modelData + ": " + timeController.playtimeByTimeOfDay[index].toFixed(1) + " hours" : modelData + ": N/A"
                                                font.pixelSize: 18
                                                Layout.alignment: Qt.AlignLeft
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: timeController
        function onIntervalChanged() {
        }
    }
}
