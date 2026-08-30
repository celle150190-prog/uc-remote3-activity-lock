#!/usr/bin/env python3
"""Apply the Remote 3 Activity / Child Lock overlay to a pinned remote-ui checkout."""
from pathlib import Path
import sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8")

def write(rel, text):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")

def replace_once(rel, old, new):
    text = read(rel)
    if old not in text:
        raise RuntimeError(f"Patch anchor not found in {rel}: {old[:120]!r}")
    write(rel, text.replace(old, new, 1))

# Config
replace_once("src/config/config.h", "    Q_PROPERTY(double touchSliderGainSeek READ getTouchSliderGainSeek WRITE setTouchSliderGainSeek NOTIFY touchSliderGainSeekChanged)\n", "    Q_PROPERTY(double touchSliderGainSeek READ getTouchSliderGainSeek WRITE setTouchSliderGainSeek NOTIFY touchSliderGainSeekChanged)\n\n    Q_PROPERTY(bool activityLockEnabled READ getActivityLockEnabled WRITE setActivityLockEnabled NOTIFY activityLockEnabledChanged)\n    Q_PROPERTY(int activityLockInactivityTimeoutSec READ getActivityLockInactivityTimeoutSec WRITE setActivityLockInactivityTimeoutSec NOTIFY activityLockInactivityTimeoutSecChanged)\n    Q_PROPERTY(bool activityLockOnWake READ getActivityLockOnWake WRITE setActivityLockOnWake NOTIFY activityLockOnWakeChanged)\n    Q_PROPERTY(bool activityLockTouchUnlock READ getActivityLockTouchUnlock WRITE setActivityLockTouchUnlock NOTIFY activityLockTouchUnlockChanged)\n    Q_PROPERTY(bool activityLockSliderUnlock READ getActivityLockSliderUnlock WRITE setActivityLockSliderUnlock NOTIFY activityLockSliderUnlockChanged)\n")
replace_once("src/config/config.h", "    double getTouchSliderGainSeek();\n    void   setTouchSliderGainSeek(double value);\n", "    double getTouchSliderGainSeek();\n    void   setTouchSliderGainSeek(double value);\n\n    bool getActivityLockEnabled();\n    void setActivityLockEnabled(bool value);\n    int getActivityLockInactivityTimeoutSec();\n    void setActivityLockInactivityTimeoutSec(int value);\n    bool getActivityLockOnWake();\n    void setActivityLockOnWake(bool value);\n    bool getActivityLockTouchUnlock();\n    void setActivityLockTouchUnlock(bool value);\n    bool getActivityLockSliderUnlock();\n    void setActivityLockSliderUnlock(bool value);\n")
replace_once("src/config/config.h", "    void touchSliderGainSeekChanged();\n", "    void touchSliderGainSeekChanged();\n    void activityLockEnabledChanged();\n    void activityLockInactivityTimeoutSecChanged();\n    void activityLockOnWakeChanged();\n    void activityLockTouchUnlockChanged();\n    void activityLockSliderUnlockChanged();\n")
replace_once("src/config/config.cpp", "void Config::setTouchSliderGainSeek(double value)\n{\n    m_settings->setValue(\"touchslider/gainSeek\", value);\n    emit touchSliderGainSeekChanged();\n}\n", "void Config::setTouchSliderGainSeek(double value)\n{\n    m_settings->setValue(\"touchslider/gainSeek\", value);\n    emit touchSliderGainSeekChanged();\n}\n\nbool Config::getActivityLockEnabled() { return m_settings->value(\"activitylock/enabled\", false).toBool(); }\nvoid Config::setActivityLockEnabled(bool value) { m_settings->setValue(\"activitylock/enabled\", value); emit activityLockEnabledChanged(); }\nint Config::getActivityLockInactivityTimeoutSec() { return m_settings->value(\"activitylock/inactivityTimeoutSec\", 0).toInt(); }\nvoid Config::setActivityLockInactivityTimeoutSec(int value) { value = qBound(0, value, 1800); m_settings->setValue(\"activitylock/inactivityTimeoutSec\", value); emit activityLockInactivityTimeoutSecChanged(); }\nbool Config::getActivityLockOnWake() { return m_settings->value(\"activitylock/onWake\", false).toBool(); }\nvoid Config::setActivityLockOnWake(bool value) { m_settings->setValue(\"activitylock/onWake\", value); emit activityLockOnWakeChanged(); }\nbool Config::getActivityLockTouchUnlock() { return m_settings->value(\"activitylock/touchUnlock\", true).toBool(); }\nvoid Config::setActivityLockTouchUnlock(bool value) { m_settings->setValue(\"activitylock/touchUnlock\", value); emit activityLockTouchUnlockChanged(); }\nbool Config::getActivityLockSliderUnlock() { return m_settings->value(\"activitylock/sliderUnlock\", true).toBool(); }\nvoid Config::setActivityLockSliderUnlock(bool value) { m_settings->setValue(\"activitylock/sliderUnlock\", value); emit activityLockSliderUnlockChanged(); }\n")

# Input controller
replace_once("src/ui/inputController.h", "    Q_PROPERTY(int repeatCount READ getRepeatCount CONSTANT)\n", "    Q_PROPERTY(int repeatCount READ getRepeatCount CONSTANT)\n    Q_PROPERTY(bool activityLockActive READ getActivityLockActive WRITE setActivityLockActive NOTIFY activityLockActiveChanged)\n")
replace_once("src/ui/inputController.h", "    int     getRepeatCount() { return m_repeatCount; }\n", "    int     getRepeatCount() { return m_repeatCount; }\n    bool    getActivityLockActive() const { return m_activityLockActive; }\n    void    setActivityLockActive(bool value);\n")
replace_once("src/ui/inputController.h", "    void activeItemChanged();\n", "    void activeItemChanged();\n    void activityLockActiveChanged();\n    void userActivity();\n")
replace_once("src/ui/inputController.h", "    bool m_blockTouchInput = false;\n", "    bool m_blockTouchInput = false;\n    bool m_activityLockActive = false;\n")
replace_once("src/ui/inputController.cpp", "void InputController::blockInput(bool value) {\n", "void InputController::setActivityLockActive(bool value) {\n    if (m_activityLockActive == value) return;\n    m_activityLockActive = value;\n    emit activityLockActiveChanged();\n}\n\nvoid InputController::blockInput(bool value) {\n")
replace_once("src/ui/inputController.cpp", "            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            cancelDeferredRelease(key);\n", "            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            emit userActivity();\n            if (m_activityLockActive && mappedKey != \"VOLUME_UP\" && mappedKey != \"VOLUME_DOWN\" &&\n                mappedKey != \"MUTE\" && mappedKey != \"PLAY\" && mappedKey != \"POWER\") {\n                event->accept();\n                return true;\n            }\n\n            cancelDeferredRelease(key);\n")
replace_once("src/ui/inputController.cpp", "            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            if (keyEvent->isAutoRepeat()) {\n", "            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            if (m_activityLockActive && mappedKey != \"VOLUME_UP\" && mappedKey != \"VOLUME_DOWN\" &&\n                mappedKey != \"MUTE\" && mappedKey != \"PLAY\" && mappedKey != \"POWER\") {\n                event->accept();\n                return true;\n            }\n\n            if (keyEvent->isAutoRepeat()) {\n")
replace_once("src/ui/inputController.cpp", "        case QEvent::TouchCancel: {\n            if (m_blockTouchInput) {\n", "        case QEvent::TouchCancel: {\n            if (event->type() == QEvent::MouseButtonPress || event->type() == QEvent::TouchBegin) {\n                emit userActivity();\n            }\n            if (m_blockTouchInput) {\n")

# Touch slider
replace_once("src/hardware/touchSlider.h", "    Q_PROPERTY(int touchXMax READ getTouchXMax CONSTANT)\n", "    Q_PROPERTY(int touchXMax READ getTouchXMax CONSTANT)\n    Q_PROPERTY(bool activityLockActive READ getActivityLockActive WRITE setActivityLockActive NOTIFY activityLockActiveChanged)\n")
replace_once("src/hardware/touchSlider.h", "    int getTouchXMax() { return m_touchXMax; }\n", "    int getTouchXMax() { return m_touchXMax; }\n    bool getActivityLockActive() const { return m_activityLockActive; }\n    void setActivityLockActive(bool value) {\n        if (m_activityLockActive == value) return;\n        m_activityLockActive = value;\n        emit activityLockActiveChanged();\n    }\n")
replace_once("src/hardware/touchSlider.h", "    void touchReleased();\n", "    void touchReleased();\n    void activityLockActiveChanged();\n")
replace_once("src/hardware/touchSlider.h", "    int m_touchXMax = 0;\n", "    int m_touchXMax = 0;\n    bool m_activityLockActive = false;\n")
for rel in ["src/qml/components/TouchSliderVolume.qml", "src/qml/components/TouchSliderSeek.qml", "src/qml/components/TouchSliderBrightness.qml", "src/qml/components/TouchSliderPosition.qml"]:
    text = read(rel)
    marker = "        function onTouchPressed() {\n"
    if marker not in text:
        raise RuntimeError(f"Touch slider handler not found in {rel}")
    text = text.replace(marker, marker + "            if (TouchSliderProcessor.activityLockActive) { return; }\n", 1)
    text = text.replace("        function onTouchXChanged(x) {\n", "        function onTouchXChanged(x) {\n            if (TouchSliderProcessor.activityLockActive) { return; }\n", 1)
    text = text.replace("        function onTouchReleased() {\n", "        function onTouchReleased() {\n            if (TouchSliderProcessor.activityLockActive) { return; }\n", 1)
    write(rel, text)

# Lock overlay
write("src/qml/components/ActivityLock.qml", r'''import QtQuick 2.15
import QtQuick.Controls 2.15
import Config 1.0
import Power 1.0
import Power.Modes 1.0
import TouchSlider 1.0

Item {
    id: lock
    width: ui.width
    height: ui.height
    z: 10000
    visible: Config.activityLockEnabled && locked
    enabled: visible

    property bool locked: false
    property real touchStartX: 0
    property real sliderStartX: 0
    property bool sliderTracking: false
    readonly property real unlockDistance: width * 0.30

    function validUnlockMethod() {
        return Config.activityLockTouchUnlock || Config.activityLockSliderUnlock;
    }
    function setLocked(value) {
        if (value && !validUnlockMethod()) return;
        locked = value;
        TouchSliderProcessor.activityLockActive = locked;
        ui.inputController.activityLockActive = locked;
        inactivityTimer.stop();
    }
    function lockNow() {
        if (Config.activityLockEnabled && validUnlockMethod()) setLocked(true);
    }
    function resetInactivityTimer() {
        if (!Config.activityLockEnabled || locked || Config.activityLockInactivityTimeoutSec <= 0) return;
        inactivityTimer.restart();
    }
    function unlock() {
        setLocked(false);
        resetInactivityTimer();
    }

    Component.onCompleted: resetInactivityTimer()

    Timer {
        id: inactivityTimer
        interval: Math.max(1000, Config.activityLockInactivityTimeoutSec * 1000)
        repeat: false
        onTriggered: lockNow()
    }

    Connections {
        target: Config
        ignoreUnknownSignals: true
        function onActivityLockEnabledChanged() {
            if (!Config.activityLockEnabled) lock.setLocked(false)
            else lock.resetInactivityTimer()
        }
        function onActivityLockInactivityTimeoutSecChanged() {
            inactivityTimer.interval = Math.max(1000, Config.activityLockInactivityTimeoutSec * 1000)
            lock.resetInactivityTimer()
        }
        function onActivityLockTouchUnlockChanged() {
            if (lock.locked && !lock.validUnlockMethod()) lock.setLocked(false)
        }
        function onActivityLockSliderUnlockChanged() {
            if (lock.locked && !lock.validUnlockMethod()) lock.setLocked(false)
        }
    }

    Connections {
        target: ui.inputController
        ignoreUnknownSignals: true
        function onUserActivity() { lock.resetInactivityTimer() }
    }

    Connections {
        target: Power
        ignoreUnknownSignals: true
        function onPowerModeChanged(fromPowerMode, toPowerMode) {
            if (!Config.activityLockEnabled || !Config.activityLockOnWake) return
            if (toPowerMode === PowerModes.Normal && (fromPowerMode === PowerModes.Low_power || fromPowerMode === PowerModes.Idle)) lock.lockNow()
        }
    }

    Connections {
        target: TouchSliderProcessor
        ignoreUnknownSignals: true
        function onTouchPressed() {
            if (!lock.locked || !Config.activityLockSliderUnlock) return
            lock.sliderTracking = true
            lock.sliderStartX = TouchSliderProcessor.touchX
        }
        function onTouchXChanged(x) {
            if (!lock.locked || !lock.sliderTracking || !Config.activityLockSliderUnlock) return
            var range = TouchSliderProcessor.touchXMax - TouchSliderProcessor.touchXMin
            if (range <= 0) range = 300
            if (x - lock.sliderStartX >= range * 0.70) {
                lock.sliderTracking = false
                lock.unlock()
            }
        }
        function onTouchReleased() { lock.sliderTracking = false }
    }

    MouseArea {
        anchors.fill: parent
        preventStealing: true
        onPressed: lock.touchStartX = mouse.x
        onReleased: {
            if (Config.activityLockTouchUnlock && mouse.x - lock.touchStartX >= lock.unlockDistance) lock.unlock()
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.88
        Column {
            anchors.centerIn: parent
            width: parent.width - 50
            spacing: 24
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                color: "white"
                text: "🔒"
                font.pixelSize: 70
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                color: "white"
                text: qsTr("Remote locked")
                font.pixelSize: 34
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                color: "#dddddd"
                text: Config.activityLockTouchUnlock && Config.activityLockSliderUnlock ? qsTr("Swipe right on the screen or slide the touch slider fully to the right to unlock.") : (Config.activityLockTouchUnlock ? qsTr("Swipe right on the screen to unlock.") : qsTr("Slide the touch slider fully to the right to unlock."))
                font.pixelSize: 24
            }
            Text {
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
                color: "#aaaaaa"
                text: qsTr("The current activity and page remain selected.")
                font.pixelSize: 18
            }
        }
    }
}
''')

# Settings page. Keep every child object on its own line; this avoids the QML parser error caused by semicolon-separated object declarations.
write("src/qml/settings/settings/ActivityLock.qml", r'''import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Config 1.0
import "qrc:/settings" as Settings
import "qrc:/components" as Components

Settings.Page {
    id: page

    Flickable {
        anchors {
            top: topNavigation.bottom
            bottom: parent.bottom
        }
        width: parent.width
        contentWidth: width
        contentHeight: content.height + 30
        clip: true

        ColumnLayout {
            id: content
            width: parent.width
            spacing: 20

            ColumnLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                spacing: 10

                RowLayout {
                    Text {
                        Layout.fillWidth: true
                        color: colors.offwhite
                        text: qsTr("Activity / Child Lock")
                        font: fonts.primaryFont(30)
                        wrapMode: Text.WordWrap
                    }
                    Components.Switch {
                        checked: Config.activityLockEnabled
                        icon: "uc:check"
                        trigger: function() { Config.activityLockEnabled = !Config.activityLockEnabled }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    color: colors.light
                    text: qsTr("Locks the current activity and page against accidental navigation input.")
                    font: fonts.secondaryFont(24)
                    wrapMode: Text.WordWrap
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                height: 2
                color: colors.medium
            }

            ColumnLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                spacing: 10

                RowLayout {
                    Text {
                        Layout.fillWidth: true
                        color: colors.offwhite
                        text: qsTr("Lock after inactivity")
                        font: fonts.primaryFont(30)
                        wrapMode: Text.WordWrap
                    }
                    Text {
                        color: colors.offwhite
                        text: Config.activityLockInactivityTimeoutSec === 0 ? qsTr("Off") : qsTr("%1 min").arg(Math.round(Config.activityLockInactivityTimeoutSec / 60))
                        font: fonts.primaryFont(26)
                    }
                }

                Components.Slider {
                    Layout.fillWidth: true
                    from: 0
                    to: 30
                    stepSize: 1
                    showLiveValue: false
                    value: Math.round(Config.activityLockInactivityTimeoutSec / 60)
                    lowValueText: qsTr("Off")
                    highValueText: qsTr("30 min")
                    onMoved: Config.activityLockInactivityTimeoutSec = Math.round(value) * 60
                }

                Text {
                    Layout.fillWidth: true
                    color: colors.light
                    text: qsTr("Independent of the remote standby timer.")
                    font: fonts.secondaryFont(24)
                    wrapMode: Text.WordWrap
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                height: 2
                color: colors.medium
            }

            RowLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10

                Text {
                    Layout.fillWidth: true
                    color: colors.offwhite
                    text: qsTr("Lock when waking from standby")
                    font: fonts.primaryFont(30)
                    wrapMode: Text.WordWrap
                }
                Components.Switch {
                    checked: Config.activityLockOnWake
                    icon: "uc:check"
                    trigger: function() { Config.activityLockOnWake = !Config.activityLockOnWake }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                height: 2
                color: colors.medium
            }

            ColumnLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                spacing: 10

                Text {
                    color: colors.offwhite
                    text: qsTr("Unlock methods")
                    font: fonts.primaryFont(30)
                }

                RowLayout {
                    Text {
                        Layout.fillWidth: true
                        color: colors.offwhite
                        text: qsTr("Touchscreen swipe")
                        font: fonts.primaryFont(26)
                    }
                    Components.Switch {
                        checked: Config.activityLockTouchUnlock
                        icon: "uc:check"
                        trigger: function() {
                            if (Config.activityLockSliderUnlock) Config.activityLockTouchUnlock = !Config.activityLockTouchUnlock
                        }
                    }
                }

                RowLayout {
                    Text {
                        Layout.fillWidth: true
                        color: colors.offwhite
                        text: qsTr("Touch slider")
                        font: fonts.primaryFont(26)
                    }
                    Components.Switch {
                        checked: Config.activityLockSliderUnlock
                        icon: "uc:check"
                        trigger: function() {
                            if (Config.activityLockTouchUnlock) Config.activityLockSliderUnlock = !Config.activityLockSliderUnlock
                        }
                    }
                }

                Text {
                    Layout.fillWidth: true
                    color: colors.light
                    text: qsTr("At least one unlock method is always required.")
                    font: fonts.secondaryFont(22)
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
''')

# Settings menu entry
replace_once("src/qml/settings/Settings.qml", "                {\n                    itemTitle: QT_TR_NOOP(\"Touch Slider\"),\n                    page: \"TouchSlider\",\n                    icon: \"uc:sliders\"\n                },\n", "                {\n                    itemTitle: QT_TR_NOOP(\"Touch Slider\"),\n                    page: \"TouchSlider\",\n                    icon: \"uc:sliders\"\n                },\n                {\n                    itemTitle: QT_TR_NOOP(\"Activity / Child Lock\"),\n                    page: \"ActivityLock\",\n                    icon: \"uc:lock\"\n                },\n")

# Main UI and resources
main = read("src/qml/main.qml")
if 'Components.ActivityLock {' not in main:
    marker = "\n}\n"
    pos = main.rfind(marker)
    if pos < 0:
        raise RuntimeError("main.qml closing brace not found")
    main = main[:pos] + "\n    Components.ActivityLock {\n        id: activityLock\n        anchors.centerIn: parent\n    }\n" + main[pos:]
    write("src/qml/main.qml", main)

qrc = read("resources/qrc/main.qrc")
if 'components/ActivityLock.qml' not in qrc:
    anchor = '        <file alias="components/LoadingFirst.qml">../../src/qml/components/LoadingFirst.qml</file>\n'
    if anchor not in qrc:
        raise RuntimeError("main.qrc component anchor not found")
    qrc = qrc.replace(anchor, anchor + '        <file alias="components/ActivityLock.qml">../../src/qml/components/ActivityLock.qml</file>\n', 1)
if 'settings/settings/ActivityLock.qml' not in qrc:
    anchor = '        <file alias="settings/settings/Ui.qml">../../src/qml/settings/settings/Ui.qml</file>\n'
    if anchor not in qrc:
        raise RuntimeError("main.qrc settings anchor not found")
    qrc = qrc.replace(anchor, anchor + '        <file alias="settings/settings/ActivityLock.qml">../../src/qml/settings/settings/ActivityLock.qml</file>\n', 1)
write("resources/qrc/main.qrc", qrc)

print("Activity Lock patch applied successfully")
