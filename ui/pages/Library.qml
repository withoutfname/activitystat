import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt.labs.platform 1.1 as Platform

Item {
    Component.onCompleted: {
        libraryController.fetchGames()
    }

    Connections {
        target: libraryController
        function onRawgMetadataFetched(app_id, icon_path, genres, year) {
            if (editDialog.currentGame && editDialog.currentGame.app_id === app_id) {
                editDialog.tempIconPath = icon_path
                editDialog.tempGenres = genres ? genres.split(", ") : []
                editDialog.tempYear = year > 0 ? year : ""
                editDialog.isNewIcon = (icon_path !== "" && icon_path !== editDialog.currentGame.icon_path)
                editDialog.open()
            }
        }
    }

    ScrollView {
        id: scrollView
        anchors.fill: parent
        clip: true
        ScrollBar.vertical.policy: ScrollBar.AsNeeded
        ScrollBar.horizontal.policy: ScrollBar.AsNeeded

        ColumnLayout {
            width: scrollView.width
            spacing: 30

            Label {
                text: "Game Library"
                font.pixelSize: 28
                font.bold: true
                Layout.alignment: Qt.AlignHCenter
                Layout.topMargin: 10
            }

            Loader {
                id: noDataLoader
                active: libraryController.gamesList.length === 0
                sourceComponent: Component {
                    Label {
                        text: "No games found in the library."
                        font.pixelSize: 20
                        color: "gray"
                        Layout.alignment: Qt.AlignHCenter
                    }
                }
            }

            GridView {
                id: gameGrid
                Layout.fillWidth: true
                Layout.preferredHeight: contentHeight
                Layout.leftMargin: 30
                Layout.rightMargin: 30
                cellWidth: (parent.width - Layout.leftMargin - Layout.rightMargin) / 5 - 20
                cellHeight: 360
                model: libraryController.gamesList
                visible: libraryController.gamesList.length > 0

                property int itemSpacing: 20

                delegate: Item {
                    id: cellItem
                    width: gameGrid.cellWidth - gameGrid.itemSpacing
                    height: gameGrid.cellHeight

                    Rectangle {
                        id: card
                        width: parent.width
                        height: 340
                        color: "white"
                        border.color: "gray"
                        border.width: 1
                        radius: 5
                        clip: true

                        Column {
                            id: contentColumn
                            anchors.top: parent.top
                            anchors.topMargin: 10
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: 5
                            width: parent.width - 20

                            Image {
                                id: gameImage
                                width: 140
                                height: 140
                                fillMode: Image.PreserveAspectFit
                                sourceSize.width: 140
                                sourceSize.height: 140
                                anchors.horizontalCenter: parent.horizontalCenter
                                cache: false

                                source: {
                                    console.log("=== Image source calculation start ===");
                                    console.log("Game name:", modelData.name || "Unnamed");
                                    console.log("is_external:", modelData.is_external);
                                    console.log("Original icon_path:", modelData.icon_path);

                                    if (modelData.icon_path && modelData.icon_path !== "") {
                                        if (modelData.is_external) {
                                            var resolvedPath = Qt.resolvedUrl(modelData.icon_path);
                                            console.log("[External] Resolved path:", resolvedPath);

                                            // Проверка существования файла
                                            var cleanPath = resolvedPath.toString().replace("file:///", "");
                                            var fileExists = libraryController.checkFileExists(cleanPath);
                                            console.log("File exists:", fileExists, "at path:", cleanPath);

                                            if (!fileExists) {
                                                console.error("External image file not found, using fallback");
                                                return Qt.resolvedUrl("../../resources/images/no_image.jpg");
                                            }

                                            return resolvedPath;
                                        } else {
                                            var internalUrl = libraryController.getIconUrl(modelData.icon_path);
                                            console.log("[Internal] getIconUrl result:", internalUrl);

                                            if (!internalUrl) {
                                                console.error("Internal image URL is empty, using fallback");
                                                return Qt.resolvedUrl("../../resources/images/no_image.jpg");
                                            }

                                            // Проверка существования файла
                                            var cleanInternalPath = internalUrl.toString().replace("file:///", "");
                                            var fileExistsInternal = libraryController.checkFileExists(cleanInternalPath);
                                            console.log("Internal file exists:", fileExistsInternal, "at path:", cleanInternalPath);

                                            if (!fileExistsInternal) {
                                                console.error("Internal image file not found, using fallback");
                                                return Qt.resolvedUrl("../../resources/images/no_image.jpg");
                                            }

                                            return internalUrl;
                                        }
                                    } else {
                                        console.log("No icon_path provided, using fallback image");
                                        return Qt.resolvedUrl("../../resources/images/no_image.jpg");
                                    }
                                }
                            }

                            Text {
                                text: modelData.name || "Unnamed Game"
                                font.pixelSize: 14
                                horizontalAlignment: Text.AlignHCenter
                                width: parent.width
                                wrapMode: Text.WordWrap
                            }

                            Text {
                                text: "Hours: " + (modelData.total_hours || 0).toFixed(1)
                                font.pixelSize: 12
                                color: "gray"
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }

                        Column {
                            id: hoverInfo
                            anchors.top: contentColumn.bottom
                            anchors.topMargin: 10
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: 5
                            width: parent.width - 20
                            visible: false

                            Text {
                                text: "Sessions: " + (modelData.session_count || 0)
                                font.pixelSize: 12
                                color: "black"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Text {
                                text: "First Played: " + (modelData.first_played ? Qt.formatDate(new Date(modelData.first_played), "dd-MM-yyyy") : "N/A")
                                font.pixelSize: 12
                                color: "black"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Text {
                                text: "Last Played: " + (modelData.last_played ? Qt.formatDate(new Date(modelData.last_played), "dd-MM-yyyy") : "N/A")
                                font.pixelSize: 12
                                color: "black"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Text {
                                text: "Genre: " + (modelData.genre || "Unknown")
                                font.pixelSize: 12
                                color: "black"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Text {
                                text: "Year: " + (modelData.year || "N/A")
                                font.pixelSize: 12
                                color: "black"
                                horizontalAlignment: Text.AlignHCenter
                            }

                            Text {
                                visible: !modelData.is_external && modelData.rating
                                text: {
                                    if (modelData.rating === "like") return "Rating: 👍 Liked"
                                    else if (modelData.rating === "dislike") return "Rating: 👎 Disliked"
                                    else if (modelData.rating === "mixed") return "Rating: ~ Mixed"
                                    else return ""
                                }
                                font.pixelSize: 12
                                color: {
                                    if (modelData.rating === "like") return "#51cf66"
                                    else if (modelData.rating === "dislike") return "#ff6b6b"
                                    else if (modelData.rating === "mixed") return "#ADFF2F"
                                    else return "black"
                                }
                                horizontalAlignment: Text.AlignHCenter
                            }
                        }

                        RowLayout {
                            id: buttonRow
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.rightMargin: 10
                            anchors.bottomMargin: 10
                            spacing: 5
                            visible: !modelData.is_external && hoverInfo.visible

                            Button {
                                id: autoButton
                                implicitWidth: 40
                                implicitHeight: 40
                                Image {
                                    source: Qt.resolvedUrl("../../resources/images/auto_parse_icon.png").toString()
                                    anchors.centerIn: parent
                                    width: 24
                                    height: 24
                                    fillMode: Image.PreserveAspectFit
                                }
                                onClicked: {
                                    editDialog.currentGame = modelData
                                    libraryController.fetchRawgMetadata(modelData.app_id, modelData.name)
                                }
                            }

                            Button {
                                id: manualButton
                                implicitWidth: 40
                                implicitHeight: 40
                                Image {
                                    source: Qt.resolvedUrl("../../resources/images/manual_icon.png").toString()
                                    anchors.centerIn: parent
                                    width: 24
                                    height: 24
                                    fillMode: Image.PreserveAspectFit
                                }
                                onClicked: {
                                    editDialog.currentGame = modelData
                                    editDialog.tempIconPath = modelData.icon_path || ""
                                    editDialog.tempGenres = modelData.genre ? modelData.genre.split(", ") : []
                                    editDialog.tempYear = modelData.year > 0 ? modelData.year : ""
                                    editDialog.isNewIcon = false
                                    editDialog.open()
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            onEntered: {
                                card.color = "#f0f0f0"
                                hoverInfo.visible = true
                                buttonRow.visible = !modelData.is_external
                            }
                            onExited: {
                                card.color = "white"
                                hoverInfo.visible = false
                                buttonRow.visible = false
                            }
                            propagateComposedEvents: true
                            acceptedButtons: Qt.NoButton
                        }
                    }
                }
            }
        }
    }

    Dialog {
        id: editDialog
        title: "Edit Game Metadata"
        standardButtons: Dialog.Close
        width: 800
        height: 650
        anchors.centerIn: parent

        property var currentGame: ({})
        property string tempIconPath: ""
        property var tempGenres: []
        property string tempYear: ""
        property bool isNewIcon: false
        property string selectedIconPath: ""

        onOpened: {
            if (currentGame && currentGame.app_id) {
                console.log("Opening editDialog for game:", currentGame.name, "rating:", currentGame.rating)
                var updatedGame = libraryController.gamesList.find(game => game.app_id === currentGame.app_id)
                if (updatedGame) {
                    editDialog.currentGame = updatedGame
                }
                gameNameLabel.text = currentGame.name || "Unnamed Game"
                genreRepeater.updateSelectedGenres(tempGenres.length > 0 ? tempGenres : (currentGame.genre ? currentGame.genre.split(", ") : []))
                yearField.text = tempYear !== "" ? tempYear : (currentGame.year > 0 ? currentGame.year : "")
                ratingRow.currentRating = currentGame.rating !== undefined ? currentGame.rating : ""
                console.log("Set currentRating to:", ratingRow.currentRating)

                // Сбрасываем флаг новой иконки
                selectedIconPath = ""
                isNewIcon = false

                // Устанавливаем изображение
                if (tempIconPath && tempIconPath.startsWith("temp_")) {
                    previewImage.source = libraryController.getIconUrl(tempIconPath)
                } else if (currentGame.is_external) {
                    previewImage.source = currentGame.icon_path
                        ? Qt.resolvedUrl(currentGame.icon_path)
                        : Qt.resolvedUrl("../../resources/images/no_image.jpg")
                } else {
                    previewImage.source = currentGame.icon_path
                        ? libraryController.getIconUrl(currentGame.icon_path)
                        : Qt.resolvedUrl("../../resources/images/no_image.jpg")
                }
            }
        }

        onClosed: {
            // Удаляем временную иконку, если она не была сохранена
            if (tempIconPath && tempIconPath.startsWith("temp_") && !isNewIcon) {
                console.log("Deleting temp icon on dialog close:", tempIconPath)
                libraryController.deleteTempIcon(tempIconPath)
            }
            tempIconPath = ""
            tempGenres = []
            tempYear = ""
            isNewIcon = false
            selectedIconPath = ""
        }

        Platform.FileDialog {
            id: fileDialog
            title: "Select Game Image"
            nameFilters: ["Image files (*.png *.jpg *.jpeg)"]
            folder: Platform.StandardPaths.writableLocation(Platform.StandardPaths.PicturesLocation)

            onAccepted: {
                if (editDialog.currentGame && editDialog.currentGame.app_id) {
                    var sourcePath = fileDialog.file.toString()
                    // Убираем file:/// для проверки существования
                    var cleanPath = sourcePath.replace("file:///", "")

                    if (libraryController.checkFileExists(cleanPath)) {
                        editDialog.selectedIconPath = cleanPath
                        editDialog.isNewIcon = true
                        previewImage.source = "file:///" + cleanPath
                    } else {
                        console.error("Файл не существует:", cleanPath)
                    }
                }
            }
        }

        ScrollView {
            id: dialogScrollView
            anchors.fill: parent
            clip: true
            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            ScrollBar.horizontal.policy: ScrollBar.AsNeeded

            ColumnLayout {
                width: dialogScrollView.width
                spacing: 15
                anchors.margins: 20

                Label {
                    id: gameNameLabel
                    text: "Game Name"
                    font.pixelSize: 18
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: "Icon Preview:"
                        font.pixelSize: 14
                    }

                    Image {
                        id: previewImage
                        width: 140
                        height: 140
                        fillMode: Image.PreserveAspectFit
                        sourceSize.width: 140
                        sourceSize.height: 140
                        clip: true
                        Layout.alignment: Qt.AlignVCenter
                        cache: false
                    }

                    Button {
                        text: "Change Icon"
                        onClicked: {
                            fileDialog.open()
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: "Genre:"
                        font.pixelSize: 14
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 220
                        clip: true

                        GridLayout {
                            columns: 6
                            columnSpacing: 5
                            rowSpacing: 5

                            Repeater {
                                id: genreRepeater
                                model: [
                                    "Action", "Adventure", "RPG", "Strategy", "Simulation",
                                    "Shooter", "Racing", "Sports", "Horror", "Sandbox",
                                    "Open World", "Survival", "Stealth", "Fighting",
                                    "Battle Royale", "Souls-like", "Roguelike", "Tactical",
                                    "Fantasy", "Cyberpunk", "Post-Apocalyptic",
                                    "Interactive Movie", "Narrative", "Single", "Multiplayer",
                                    "Co-op", "MMO"
                                ]

                                property var selectedGenres: []

                                function updateSelectedGenres(genres) {
                                    selectedGenres = genres || []
                                    selectedGenres = selectedGenres.filter(function(genre) {
                                        return genre !== "Unknown" && model.indexOf(genre) !== -1
                                    })
                                    for (var i = 0; i < count; i++) {
                                        var button = itemAt(i)
                                        button.checked = selectedGenres.includes(button.text)
                                    }
                                }

                                Button {
                                    text: modelData
                                    checkable: true
                                    checked: genreRepeater.selectedGenres.includes(modelData)

                                    Layout.minimumWidth: 100
                                    Layout.preferredHeight: 40

                                    palette.button: checked ? "#d0e0ff" : "white"
                                    palette.buttonText: "black"
                                    flat: false
                                    padding: 10

                                    onClicked: {
                                        if (checked) {
                                            if (!genreRepeater.selectedGenres.includes(modelData)) {
                                                genreRepeater.selectedGenres.push(modelData)
                                            }
                                        } else {
                                            var index = genreRepeater.selectedGenres.indexOf(modelData)
                                            if (index !== -1) {
                                                genreRepeater.selectedGenres.splice(index, 1)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: "Rating:"
                        font.pixelSize: 14
                    }

                    Row {
                        id: ratingRow
                        spacing: 5

                        property string currentRating: editDialog.currentGame && editDialog.currentGame.rating !== undefined ? editDialog.currentGame.rating : ""

                        function updateRating(newRating) {
                            currentRating = newRating || ""
                        }

                        Button {
                            text: "Like"
                            checkable: true
                            checked: ratingRow.currentRating === "like"
                            palette.button: checked ? "#ffcccc" : "white"
                            onClicked: {
                                ratingRow.updateRating(checked ? "like" : "")
                            }
                        }

                        Button {
                            text: "Dislike"
                            checkable: true
                            checked: ratingRow.currentRating === "dislike"
                            palette.button: checked ? "#cce5ff" : "white"
                            onClicked: {
                                ratingRow.updateRating(checked ? "dislike" : "")
                            }
                        }

                        Button {
                            text: "Mixed"
                            checkable: true
                            checked: ratingRow.currentRating === "mixed"
                            palette.button: checked ? "#e6ffe6" : "white"
                            onClicked: {
                                ratingRow.updateRating(checked ? "mixed" : "")
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Label {
                        text: "Year:"
                        font.pixelSize: 14
                    }

                    TextField {
                        id: yearField
                        Layout.preferredWidth: 100
                        validator: IntValidator { bottom: 1990 }
                        placeholderText: "Enter year (1990+)"
                    }
                }

                Button {
                    text: "Save"
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        if (editDialog.currentGame && editDialog.currentGame.app_id) {
                            var newYear = parseInt(yearField.text) || 0
                            var genresString = genreRepeater.selectedGenres.join(", ")

                            // Определяем путь для сохранения
                            var iconToSave = ""
                            if (editDialog.selectedIconPath !== "") {
                                // Пытаемся сохранить выбранную картинку (из fileDialog)
                                iconToSave = libraryController.saveIconToAppData(
                                    editDialog.selectedIconPath,
                                    editDialog.currentGame.app_id
                                )
                            } else if (editDialog.tempIconPath && editDialog.tempIconPath.startsWith("temp_")) {
                                // Используем временную иконку из автопарсинга
                                iconToSave = libraryController.saveIconToAppData(
                                    libraryController.get_full_icon_path(editDialog.tempIconPath),
                                    editDialog.currentGame.app_id
                                )
                            } else {
                                // Используем текущую иконку
                                iconToSave = editDialog.currentGame.icon_path || ""
                            }

                            if (iconToSave === "") {
                                console.error("Не удалось сохранить иконку")
                                return
                            }

                            // Сохраняем метаданные
                            libraryController.saveManualMetadata(
                                editDialog.currentGame.app_id,
                                iconToSave,
                                genresString,
                                newYear,
                                ratingRow.currentRating
                            )

                            // Устанавливаем isNewIcon, чтобы предотвратить удаление в onClosed
                            editDialog.isNewIcon = true

                            console.log("Forcing Library.qml refresh by calling fetchGames")
                            libraryController.fetchGames()

                            editDialog.close()
                        }
                    }
                }
            }
        }
    }
}
