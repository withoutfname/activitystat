import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects 2.15
import QtQuick.Controls.Material 2.15

Item {
    id: root

    property color primaryColor: "#6c5ce7"
    property color secondaryColor: "#a29bfe"
    property color accentColor: "#fd79a8"
    property color textColor: "#2d3436"
    property color backgroundColor: "#f5f6fa"
    property color cardColor: "#ffffff"
    property color borderColor: "#dfe6e9"

    property color section1Color: "#e0f7fa"
    property color section2Color: "#fce4ec"
    property color section3Color: "#e8f5e9"
    property color section4Color: "#fffde7"
    property color section5Color: "#f3e5f5"
    property color section6Color: "#e1f5fe"
    property color section7Color: "#fff3e0"
    property color section8Color: "#f1f8e9"
    property color section9Color: "#ffebee"

    ScrollView {
        id: scrollView
        anchors.fill: parent
        ScrollBar.vertical.policy: ScrollBar.AsNeeded

        ColumnLayout {
            width: scrollView.width - 80
            anchors.margins: 20
            spacing: 20

            // Current Year with Dropdown
            Rectangle {
                Layout.fillWidth: true
                height: 80
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section2Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section2Color, 1.2) }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "Current Year"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        RowLayout {
                            spacing: 10
                            ComboBox {
                                id: yearComboBox
                                model: dashboardController ? dashboardController.availableYears : []
                                currentIndex: dashboardController && dashboardController.availableYears ? dashboardController.availableYears.indexOf(dashboardController.currentYear) : -1
                                onCurrentTextChanged: {
                                    if (dashboardController && currentText) {
                                        dashboardController.currentYear = parseInt(currentText)
                                    }
                                }
                                enabled: dashboardController && dashboardController.availableYears && dashboardController.availableYears.length > 0
                                background: Rectangle {
                                    color: "white"
                                    border.color: root.accentColor
                                    radius: 5
                                }
                                contentItem: Text {
                                    text: yearComboBox.displayText || "No Year"
                                    color: root.textColor || "#000000"
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: 10
                                }
                            }

                            Label {
                                text: dashboardController && dashboardController.currentYear ? dashboardController.currentYear + " Summary" : "No Data"
                                font.pixelSize: 16
                                color: accentColor
                            }
                        }
                    }
                }
            }

            // General Gaming Metrics
            Rectangle {
                Layout.fillWidth: true
                height: 300
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section3Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section3Color, 1.2) }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "General Gaming Metrics"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        ColumnLayout {
                            spacing: 5
                            RowLayout {
                                Label { text: "Total playtime: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.total_playtime || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Percentage of total playtime: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.percentage_of_total || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Number of gaming sessions: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.session_count || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Average session duration: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.avg_session_duration || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Percentage of active days: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.active_days_percentage || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Most active month: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.most_active_month || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Least active month: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.least_active_month || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Most active day of week: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.most_active_day_of_week || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Most active time of day: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.most_active_time_of_day || "N/A" : "N/A"; color: textColor }
                            }
                            RowLayout {
                                Label { text: "Longest gaming day: "; color: textColor }
                                Label { text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.longest_gaming_day || "N/A" : "N/A"; color: textColor }
                            }
                        }
                    }
                }
            }

            // Game Insights
            Rectangle {
                Layout.fillWidth: true
                height: 220
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section4Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section4Color, 1.2) }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "Game Insights"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        ColumnLayout {
                            spacing: 5
                            Row {
                                spacing: 5
                                Label {
                                    text: dashboardController ? "Игра года " + (dashboardController.currentYear || "") + ":" : "Игра года:"
                                    color: textColor
                                }
                                Label {
                                    text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.game_of_the_year || "N/A" : "N/A"
                                    color: textColor
                                }
                            }
                            Row {
                                spacing: 5
                                Label {
                                    text: "Процент времени в топ-3 играх:"
                                    color: textColor
                                }
                                Label {
                                    text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.top3_games_percentage || "N/A" : "N/A"
                                    color: textColor
                                    wrapMode: Text.WordWrap
                                    Layout.maximumWidth: parent.width - 150
                                }
                            }
                            Row {
                                spacing: 5
                                Label {
                                    text: dashboardController ? "Процент времени в новинках " + (dashboardController.currentYear || "") + " года:" : "Процент времени в новинках года:"
                                    color: textColor
                                }
                                Label {
                                    text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.new_releases_percentage || "N/A" : "N/A"
                                    color: textColor
                                    wrapMode: Text.WordWrap
                                    Layout.maximumWidth: parent.width - 150
                                }
                            }
                            Row {
                                spacing: 5
                                Label {
                                    text: "Количество уникальных игр:"
                                    color: textColor
                                }
                                Label {
                                    text: dashboardController && dashboardController.yearStats ? dashboardController.yearStats.unique_games_count || "N/A" : "N/A"
                                    color: textColor
                                }
                            }
                        }
                    }
                }
            }

            // Genre Insights
            Rectangle {
                Layout.fillWidth: true
                height: 150
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section5Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section5Color, 1.2) }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "Genre Insights"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        ColumnLayout {
                            spacing: 5
                            Label {
                                text: dashboardController && dashboardController.currentYear && dashboardController.yearStats ? "Main genre of " + dashboardController.currentYear + ": " + dashboardController.yearStats.main_genre : "Main genre: N/A"
                                color: textColor
                            }
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Genre distribution: " + dashboardController.yearStats.genre_distribution : "Genre distribution: N/A"
                                color: textColor
                            }
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Single vs Multiplayer: " + dashboardController.yearStats.single_vs_multiplayer : "Single vs Multiplayer: N/A"
                                color: textColor
                            }
                        }
                    }
                }
            }

            // Release Year Insights
            Rectangle {
                Layout.fillWidth: true
                height: 150
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section6Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section6Color, 1.2) }
                    }
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "Release Year Insights"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        ColumnLayout {
                            spacing: 5
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Percentage of playtime by release year: " + dashboardController.yearStats.playtime_by_release_year : "N/A"
                                color: textColor
                            }
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Oldest game played: " + dashboardController.yearStats.oldest_game_played : "N/A"
                                color: textColor
                            }
                        }
                    }
                }
            }

            // Streaks and Sequences
            Rectangle {
                Layout.fillWidth: true
                height: 150
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section7Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section7Color, 1.2) }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "Streaks and Sequences"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        ColumnLayout {
                            spacing: 5
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Longest streak of gaming days: " + dashboardController.yearStats.longest_gaming_streak : "N/A"
                                color: textColor
                            }
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Longest streak for a game: " + dashboardController.yearStats.longest_game_streak : "N/A"
                                color: textColor
                            }
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Longest break between gaming days: " + dashboardController.yearStats.longest_break : "N/A"
                                color: textColor
                            }
                        }
                    }
                }
            }

            // Fun Facts
            Rectangle {
                id: funFactsRect
                Layout.fillWidth: true
                Layout.preferredHeight: contentColumn.implicitHeight + 50 // Dynamic height
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section7Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section7Color, 1.2) }
                    }

                    ColumnLayout {
                        id: contentColumn
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "Fun Facts"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        ColumnLayout {
                            spacing: 5
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Platform Distribution: " + dashboardController.yearStats.platform_distribution : "N/A"
                                color: textColor
                                wrapMode: Text.WordWrap
                            }
                            RowLayout {
                                spacing: 5
                                Label {
                                    id: gamesCountLabel
                                    text: dashboardController && dashboardController.yearStats ? "Games Played One Day: " + (dashboardController.yearStats.games_played_one_day || "N/A").split(" - ")[0] : "N/A"
                                    color: textColor
                                    wrapMode: Text.WordWrap
                                }
                                Label {
                                    id: arrowLabel
                                    text: "▼"
                                    color: textColor
                                    font.pixelSize: 12
                                    MouseArea {
                                        id: expandMouseArea
                                        anchors.fill: parent
                                        enabled: dashboardController && dashboardController.yearStats && gameRepeater.model.length > 0
                                        onClicked: {
                                            gameList.visible = !gameList.visible
                                            if (gameList.visible) {
                                                var gameCount = gameRepeater.model.length || 0
                                                var newHeight = contentColumn.implicitHeight + (gameCount * 30)
                                                heightAnimation.to = newHeight
                                                heightAnimation.start()
                                            } else {
                                                heightAnimation.to = 150
                                                heightAnimation.start()
                                            }
                                        }
                                    }
                                }
                            }
                            ColumnLayout {
                                id: gameList
                                visible: false
                                spacing: 2
                                Repeater {
                                    id: gameRepeater
                                    model: dashboardController && dashboardController.yearStats && (dashboardController.yearStats.games_played_one_day || "N/A").includes("Total") ?
                                           (dashboardController.yearStats.games_played_one_day || "").split(" - ")[1].split(/,\s*/) : []
                                    delegate: Label {
                                        text: modelData || "N/A"
                                        color: textColor
                                        font.pixelSize: 12
                                        wrapMode: Text.WordWrap
                                        padding: 2
                                    }
                                }
                            }
                        }
                    }
                }

                NumberAnimation {
                    id: heightAnimation
                    target: funFactsRect
                    property: "Layout.preferredHeight"
                    duration: 200
                    easing.type: Easing.OutQuad
                    to: 150
                    running: false
                }
            }

            // Experimental Ideas
            Rectangle {
                Layout.fillWidth: true
                height: 100
                color: "transparent"
                radius: 12

                layer.enabled: true

                Rectangle {
                    anchors.fill: parent
                    radius: 12
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: section9Color }
                        GradientStop { position: 1.0; color: Qt.lighter(section9Color, 1.2) }
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 25

                        Label {
                            text: "Experimental Ideas"
                            font.pixelSize: 20
                            font.bold: true
                            color: primaryColor
                        }

                        ColumnLayout {
                            spacing: 5
                            Label {
                                text: dashboardController && dashboardController.yearStats ? "Percentage of overplayed time: " + dashboardController.yearStats.overplayed_time_stats : "N/A"
                                color: textColor
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
        }
    }
}
