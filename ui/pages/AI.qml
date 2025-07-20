// ui/pages/AI.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 10

        Button {
            text: "Generate Forecast"
            Layout.alignment: Qt.AlignHCenter
            onClicked: {
                aiController.generateForecast(30)
            }
        }

        Text {
            id: statusText
            text: "Ready to generate forecast"
            Layout.alignment: Qt.AlignHCenter
            color: "#333333"
        }

        Canvas {
            id: forecastChart
            Layout.fillWidth: true
            Layout.fillHeight: true

            chartjs: {
                "type": "line",
                "data": {
                    "labels": [],
                    "datasets": [
                        {
                            "label": "Historical Data",
                            "data": [],
                            "borderColor": "#1e88e5",
                            "backgroundColor": "rgba(30, 136, 229, 0.2)",
                            "fill": false,
                            "pointRadius": 3,
                            "borderWidth": 2
                        },
                        {
                            "label": "Forecast",
                            "data": [],
                            "borderColor": "#e53935",
                            "backgroundColor": "rgba(229, 57, 53, 0.2)",
                            "fill": false,
                            "borderDash": [5, 5],
                            "pointRadius": 3,
                            "borderWidth": 2
                        }
                    ]
                },
                "options": {
                    "responsive": true,
                    "maintainAspectRatio": false,
                    "scales": {
                        "x": {
                            "title": {
                                "display": true,
                                "text": "Days Since Start"
                            }
                        },
                        "y": {
                            "title": {
                                "display": true,
                                "text": "Cumulative Hours"
                            },
                            "beginAtZero": false
                        }
                    },
                    "plugins": {
                        "legend": {
                            "display": true
                        },
                        "title": {
                            "display": true,
                            "text": "Cumulative Gaming Time: History and Forecast"
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: aiController
        function onForecastCompleted(historicalData, forecastData, labels, message) {
            forecastChart.chartjs.data.labels = labels
            forecastChart.chartjs.data.datasets[0].data = historicalData
            forecastChart.chartjs.data.datasets[1].data = forecastData
            forecastChart.requestPaint()
            statusText.text = message
            statusText.color = "#333333"
        }

        function onForecastError(message) {
            statusText.text = message
            statusText.color = "red"
        }
    }
}
