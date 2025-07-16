import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1 as Platform

Item {
    id: root
    anchors.fill: parent

    // Диалог для сохранения файла
    Platform.FileDialog {
        id: saveDialog
        title: "Save Database Backup"
        fileMode: Platform.FileDialog.SaveFile
        nameFilters: ["SQL files (*.sql)", "All files (*)"]
        defaultSuffix: "sql"
        onAccepted: {
            var filePath = saveDialog.file.toString().replace(/^(file:\/{3})|(qrc:\/{2})|(http:\/{2})/, "")
            backupController.backupDatabase(filePath)
        }
    }

    // Диалог для загрузки файла
    Platform.FileDialog {
        id: loadDialog
        title: "Load Database Backup"
        fileMode: Platform.FileDialog.OpenFile
        nameFilters: ["SQL files (*.sql)", "All files (*)"]
        onAccepted: {
            var filePath = loadDialog.file.toString().replace(/^(file:\/{3})|(qrc:\/{2})|(http:\/{2})/, "")
            backupController.restoreDatabase(filePath)
        }
    }

    // Диалог сообщения
    Dialog {
        id: messageDialog
        title: "Information"
        standardButtons: Dialog.Ok
        width: 300
        height: 150
        anchors.centerIn: parent

        property alias message: messageText.text

        ColumnLayout {
            anchors.fill: parent
            spacing: 10

            Label {
                id: messageText
                Layout.fillWidth: true
                wrapMode: Text.Wrap
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    Connections {
        target: backupController
        function onBackupStatus(success, message) {
            messageDialog.message = message
            messageDialog.open()
        }
        function onRestoreStatus(success, message) {
            messageDialog.message = message
            messageDialog.open()
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#f5f6fa"

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 30

            // Заголовок
            Label {
                Layout.alignment: Qt.AlignHCenter
                text: "ActivityStats"
                color: "#2d3436"
                font.pixelSize: 36
                font.bold: true
            }

            // Подзаголовок
            Label {
                Layout.alignment: Qt.AlignHCenter
                text: "Track your gaming activity"
                color: "#636e72"
                font.pixelSize: 18
            }

            // Кнопка перехода на Time.qml
            Button {
                Layout.alignment: Qt.AlignHCenter
                text: "View Time Statistics"
                font.pixelSize: 16
                padding: 15

                background: Rectangle {
                    color: "#6c5ce7"
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
                    tabBar.currentIndex = 1
                }
            }

            // Кнопка сохранения БД
            Button {
                Layout.alignment: Qt.AlignHCenter
                text: "Backup Database"
                font.pixelSize: 16
                padding: 15

                background: Rectangle {
                    color: "#00b894"
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
                    saveDialog.open()
                }
            }

            // Кнопка восстановления БД
            Button {
                Layout.alignment: Qt.AlignHCenter
                text: "Restore Database"
                font.pixelSize: 16
                padding: 15

                background: Rectangle {
                    color: "#e17055"
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
                    loadDialog.open()
                }
            }
        }
    }
}
