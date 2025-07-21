import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        Button {
            text: "Сгенерировать прогноз"
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                chartView.visible = false
                errorText.text = ""
                busyIndicator.visible = true
                aiController.generateForecast()
            }
        }

        BusyIndicator {
            id: busyIndicator
            Layout.alignment: Qt.AlignHCenter
            running: visible
            visible: false
        }

        Text {
            id: errorText
            Layout.alignment: Qt.AlignHCenter
            color: "red"
            visible: text !== ""
        }

        ChartView {
            id: chartView
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: false
            antialiasing: true
            legend.visible: true

            ValueAxis {
                id: axisX
                titleText: "Дни с начала отслеживания"
                min: 0
                max: 1
            }

            ValueAxis {
                id: axisY
                titleText: "Накопленное время (часы)"
                min: 0
                max: 1
            }

            LineSeries {
                id: historicalSeries
                name: "Исторические данные"
                axisX: axisX
                axisY: axisY
                style: Qt.SolidLine
                color: "blue"
                width: 2
                pointsVisible: true
            }

            LineSeries {
                id: forecastSeries
                name: "Прогноз"
                axisX: axisX
                axisY: axisY
                style: Qt.DashLine
                color: "red"
                width: 2
                pointsVisible: true
            }
        }
    }

    Connections {
        target: aiController
        function onForecastReady(historicalData, forecastData, error) {
            busyIndicator.visible = false

            if (error !== "") {
                errorText.text = error
                chartView.visible = false
                return
            }

            // Очистка серий
            historicalSeries.clear()
            forecastSeries.clear()

            // Заполнение исторических данных
            var minX = Number.MAX_VALUE
            var maxX = Number.MIN_VALUE
            var minY = Number.MAX_VALUE
            var maxY = Number.MIN_VALUE

            for (var i = 0; i < historicalData.length; i++) {
                var point = historicalData[i]
                historicalSeries.append(point[0], point[1])
                minX = Math.min(minX, point[0])
                maxX = Math.max(maxX, point[0])
                minY = Math.min(minY, point[1])
                maxY = Math.max(maxY, point[1])
            }

            // Заполнение прогнозируемых данных
            for (i = 0; i < forecastData.length; i++) {
                point = forecastData[i]
                forecastSeries.append(point[0], point[1])
                minX = Math.min(minX, point[0])
                maxX = Math.max(maxX, point[0])
                minY = Math.min(minY, point[1])
                maxY = Math.max(maxY, point[1])
            }

            // Обновление осей
            axisX.min = minX
            axisX.max = maxX + 1
            axisY.min = Math.max(0, minY - 10)
            axisY.max = maxY + 10

            chartView.visible = true
        }
    }
}
