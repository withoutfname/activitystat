import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

ApplicationWindow {
    id: window
    visible: true
    title: "ActivityStats"
    visibility: Window.Maximized

    // Устанавливаем минимальные размеры окна
    minimumWidth: 1500
    minimumHeight: 750

    property var tabSources: [
        Qt.resolvedUrl("../ui/pages/Index.qml").toString(),
        Qt.resolvedUrl("../ui/pages/Time.qml").toString(),
        Qt.resolvedUrl("../ui/pages/Library.qml").toString(),
        Qt.resolvedUrl("../ui/pages/Favorite.qml").toString(),
        //Qt.resolvedUrl("../ui/pages/AI.qml").toString(),
        Qt.resolvedUrl("../ui/pages/Dashboard.qml").toString()
    ]

    header: TabBar {
        id: tabBar
        width: parent.width
        TabButton { text: "Main" }
        TabButton { text: "Time" }
        TabButton { text: "Library" }
        TabButton { text: "Favorite games"}
        //TabButton { text: "AI" }
        TabButton { text: "Dashboard" }        
    }

    Loader {
        id: pageLoader
        anchors.fill: parent
        source: tabSources[tabBar.currentIndex]
    }

    Label {
        anchors.centerIn: parent
        text: "Page Not Implemented"
        font.pixelSize: 20
        visible: pageLoader.status !== Loader.Ready
    }

    Shortcut {
        sequence: "Esc"
        onActivated: Qt.quit()
    }
}
