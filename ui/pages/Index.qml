import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent

    Rectangle {
        anchors.fill: parent
        color: "#f5f6fa"  // Светлый фон

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 30

            // Заголовок
            Label {
                Layout.alignment: Qt.AlignHCenter
                text: "ActivityStats"
                color: "#2d3436"  // Темно-серый текст
                font.pixelSize: 36
                font.bold: true
            }

            // Подзаголовок
            Label {
                Layout.alignment: Qt.AlignHCenter
                text: "Track your gaming activity"
                color: "#636e72"  // Серый текст
                font.pixelSize: 18
            }

            // Кнопка перехода на Time.qml
            Button {
                Layout.alignment: Qt.AlignHCenter
                text: "View Time Statistics"
                font.pixelSize: 16
                padding: 15

                background: Rectangle {
                    color: "#6c5ce7"  // Фиолетовый
                    radius: 8
                }
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                onClicked: {
                    tabBar.currentIndex = 1  // Переключаем на вкладку Time
                }
            }

            // Первая кнопка-заглушка
            Button {
                Layout.alignment: Qt.AlignHCenter
                text: "Coming Soon"
                font.pixelSize: 16
                padding: 15
                enabled: false

                background: Rectangle {
                    color: "#b2bec3"  // Серый для неактивной кнопки
                    radius: 8
                }
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

            // Вторая кнопка-заглушка
            Button {
                Layout.alignment: Qt.AlignHCenter
                text: "Feature in Development"
                font.pixelSize: 16
                padding: 15
                enabled: false

                background: Rectangle {
                    color: "#b2bec3"  // Серый для неактивной кнопки
                    radius: 8
                }
                contentItem: Text {
                    text: parent.text
                    font: parent.font
                    color: "white"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }

        }
    }
}
