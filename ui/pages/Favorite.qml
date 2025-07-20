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
                            sourceSize.width: 180
                            sourceSize.height: 120
                            cache: false

                            source: {
                                //console.log("=== Favorite image source calculation start ===");
                                //console.log("Game name:", modelData.name || "Unnamed");
                                //console.log("is_external:", modelData.is_external);
                                //console.log("Original icon_path:", modelData.icon_path);

                                if (modelData.icon_path && modelData.icon_path !== "") {
                                    if (modelData.is_external) {
                                        var resolvedPath = Qt.resolvedUrl(modelData.icon_path);
                                        //console.log("[External] Resolved path:", resolvedPath);

                                        // Проверка существования файла
                                        var cleanPath = resolvedPath.toString().replace("file:///", "");
                                        var fileExists = libraryController.checkFileExists(cleanPath);
                                        //console.log("File exists:", fileExists, "at path:", cleanPath);

                                        if (!fileExists) {
                                            //console.error("External image file not found, using fallback");
                                            return Qt.resolvedUrl("../../resources/app_icons/images.jpg");
                                        }

                                        return resolvedPath;
                                    } else {
                                        var internalUrl = libraryController.getIconUrl(modelData.icon_path);
                                        //console.log("[Internal] getIconUrl result:", internalUrl);

                                        if (!internalUrl) {
                                            //console.error("Internal image URL is empty, using fallback");
                                            return Qt.resolvedUrl("../../resources/app_icons/images.jpg");
                                        }

                                        // Проверка существования файла
                                        var cleanInternalPath = internalUrl.toString().replace("file:///", "");
                                        var fileExistsInternal = libraryController.checkFileExists(cleanInternalPath);
                                        //console.log("Internal file exists:", fileExistsInternal, "at path:", cleanInternalPath);

                                        if (!fileExistsInternal) {
                                            //console.error("Internal image file not found, using fallback");
                                            return Qt.resolvedUrl("../../resources/app_icons/images.jpg");
                                        }

                                        return internalUrl;
                                    }
                                } else {
                                    //console.log("No icon_path provided, using fallback image");
                                    return Qt.resolvedUrl("../../resources/app_icons/images.jpg");
                                }
                            }

                            onStatusChanged: {
                                if (status === Image.Error) {
                                    //console.error("Image load error for", modelData.name, "path:", source);
                                    source = Qt.resolvedUrl("../../resources/app_icons/images.jpg");
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
