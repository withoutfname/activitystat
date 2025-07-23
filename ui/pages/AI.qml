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

        Text {
            id: errorText
            Layout.alignment: Qt.AlignHCenter
            color: "red"
            visible: text !== ""
            width: parent.width
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }

        Text {
            id: summaryText
            Layout.alignment: Qt.AlignHCenter
            color: "black"
            visible: text !== ""
            width: parent.width
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }

        ChartView {
            id: chartView
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: true  // Всегда видим
            antialiasing: true
            legend.visible: true
            backgroundColor: "transparent"

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
                width: 2
                color: "blue"
            }

            LineSeries {
                id: forecastSeries
                name: "Прогноз"
                axisX: axisX
                axisY: axisY
                width: 2
                color: "orange"
            }
        }
    }

    Component.onCompleted: {
        errorText.text = ""
        summaryText.text = ""
        // Инициируем загрузку данных
        aiController.generateForecast()
    }

    Connections {
        target: aiController
        function onForecastReady(historicalData, forecastData, error) {
            if (error !== "") {
                errorText.text = error
                summaryText.text = ""
                return
            }

            // Очистка серий
            historicalSeries.clear()
            forecastSeries.clear()

            if (historicalData.length === 0) {
                errorText.text = "Нет исторических данных для отображения"
                return
            }

            // Заполнение исторических данных
            var minX = Number.MAX_VALUE
            var maxX = Number.MIN_VALUE
            var minY = Number.MAX_VALUE
            var maxY = Number.MIN_VALUE
            var currentHours = 0

            for (var i = 0; i < historicalData.length; i++) {
                var point = historicalData[i]
                historicalSeries.append(point[0], point[1])
                minX = Math.min(minX, point[0])
                maxX = Math.max(maxX, point[0])
                minY = Math.min(minY, point[1])
                maxY = Math.max(maxY, point[1])
                if (i === historicalData.length - 1) {
                    currentHours = point[1]
                }
            }

            // Заполнение прогнозируемых данных (если есть)
            var forecastHours = currentHours
            if (forecastData.length > 0) {
                for (i = 0; i < forecastData.length; i++) {
                    point = forecastData[i]
                    forecastSeries.append(point[0], point[1])
                    minX = Math.min(minX, point[0])
                    maxX = Math.max(maxX, point[0])
                    minY = Math.min(minY, point[1])
                    maxY = Math.max(maxY, point[1])
                    if (i === forecastData.length - 1) {
                        forecastHours = point[1]
                    }
                }
                summaryText.text = "На данный момент: " + currentHours.toFixed(2) + " часов\n" +
                                  "Через 30 дней прогнозируется: " + forecastHours.toFixed(2) + " часов"
            } else {
                summaryText.text = "На данный момент: " + currentHours.toFixed(2) + " часов\n" +
                                  "Недостаточно данных для прогноза"
            }

            // Обновление осей
            axisX.min = minX
            axisX.max = maxX + 1
            axisY.min = Math.max(0, minY - 10)
            axisY.max = maxY + 10
        }
    }
}
