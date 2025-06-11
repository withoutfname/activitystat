import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property string filterRating: "like"

    Component.onCompleted: {
        if (!libraryController) {
            console.error("[Favorite] libraryController is not available!")
        } else {
            libraryController.fetchGames()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        // Фильтры по рейтингу
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: 10

            ButtonGroup {
                id: ratingGroup
                onCheckedButtonChanged: {
                    if (likeButton.checked) root.filterRating = "like"
                    else if (dislikeButton.checked) root.filterRating = "dislike"
                    else if (mixedButton.checked) root.filterRating = "mixed"
                }
            }

            Button {
                id: likeButton
                text: "Like"
                checkable: true
                checked: true
                ButtonGroup.group: ratingGroup
            }

            Button {
                id: dislikeButton
                text: "Dislike"
                checkable: true
                ButtonGroup.group: ratingGroup
            }

            Button {
                id: mixedButton
                text: "Mixed"
                checkable: true
                ButtonGroup.group: ratingGroup
            }
        }

        // Основной контент
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            GridView {
                id: favoriteGrid
                anchors.fill: parent
                anchors.leftMargin: 20
                anchors.rightMargin: 20
                clip: true

                readonly property int columns: Math.max(1, Math.floor(width / 200))
                cellWidth: width / columns
                cellHeight: 220

                model: libraryController ? libraryController.gamesList.filter(game => game.rating === root.filterRating) : []

                delegate: Rectangle {
                    width: favoriteGrid.cellWidth - 10
                    height: favoriteGrid.cellHeight - 10
                    color: "white"
                    radius: 5
                    border.color: "#e0e0e0"
                    border.width: 1

                    Column {
                        anchors.fill: parent
                        anchors.margins: 10
                        spacing: 5

                        Image {
                            id: gameImage
                            width: parent.width - 20
                            height: 120
                            anchors.horizontalCenter: parent.horizontalCenter
                            fillMode: Image.PreserveAspectFit
                            source: modelData.icon_path ? Qt.resolvedUrl(modelData.icon_path) : Qt.resolvedUrl("../../resources/app_icons/images.jpg")
                            onStatusChanged: {
                                if (status === Image.Error) {
                                    source = Qt.resolvedUrl("../../resources/app_icons/images.jpg")
                                }
                            }
                        }

                        Text {
                            text: modelData.name || "Unnamed Game"
                            width: parent.width - 10
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                            elide: Text.ElideRight
                            maximumLineCount: 2
                        }
                    }
                }

                Label {
                    anchors.centerIn: parent
                    text: "No games with this rating"
                    visible: favoriteGrid.count === 0
                    font.pixelSize: 16
                    color: "#999"
                }
            }
        }
    }
}
