#!/usr/bin/env python3
"""Apply the Remote 3 Activity/Child Lock overlay to an upstream remote-ui checkout.

The script intentionally patches a pinned upstream source tree instead of copying the
whole upstream repository into this overlay repository. This keeps the fork maintainable
and makes the exact upstream base explicit in the build workflow.
"""
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
        raise RuntimeError(f"Patch anchor not found in {rel}: {old[:100]!r}")
    text = text.replace(old, new, 1)
    write(rel, text)

# ---------------------------------------------------------------------------
# Config: persistent local settings exposed to QML.
# ---------------------------------------------------------------------------
replace_once("src/config/config.h",
'''    Q_PROPERTY(double touchSliderGainSeek READ getTouchSliderGainSeek WRITE setTouchSliderGainSeek NOTIFY touchSliderGainSeekChanged)\n''',
'''    Q_PROPERTY(double touchSliderGainSeek READ getTouchSliderGainSeek WRITE setTouchSliderGainSeek NOTIFY touchSliderGainSeekChanged)\n\n    Q_PROPERTY(bool activityLockEnabled READ getActivityLockEnabled WRITE setActivityLockEnabled NOTIFY activityLockEnabledChanged)\n    Q_PROPERTY(int activityLockInactivityTimeoutSec READ getActivityLockInactivityTimeoutSec WRITE setActivityLockInactivityTimeoutSec NOTIFY activityLockInactivityTimeoutSecChanged)\n    Q_PROPERTY(bool activityLockOnWake READ getActivityLockOnWake WRITE setActivityLockOnWake NOTIFY activityLockOnWakeChanged)\n    Q_PROPERTY(bool activityLockTouchUnlock READ getActivityLockTouchUnlock WRITE setActivityLockTouchUnlock NOTIFY activityLockTouchUnlockChanged)\n    Q_PROPERTY(bool activityLockSliderUnlock READ getActivityLockSliderUnlock WRITE setActivityLockSliderUnlock NOTIFY activityLockSliderUnlockChanged)\n''')

replace_once("src/config/config.h",
'''    double getTouchSliderGainSeek();\n    void   setTouchSliderGainSeek(double value);\n''',
'''    double getTouchSliderGainSeek();\n    void   setTouchSliderGainSeek(double value);\n\n    bool getActivityLockEnabled();\n    void setActivityLockEnabled(bool value);\n    int getActivityLockInactivityTimeoutSec();\n    void setActivityLockInactivityTimeoutSec(int value);\n    bool getActivityLockOnWake();\n    void setActivityLockOnWake(bool value);\n    bool getActivityLockTouchUnlock();\n    void setActivityLockTouchUnlock(bool value);\n    bool getActivityLockSliderUnlock();\n    void setActivityLockSliderUnlock(bool value);\n''')

replace_once("src/config/config.h",
'''    void touchSliderGainSeekChanged();\n''',
'''    void touchSliderGainSeekChanged();\n    void activityLockEnabledChanged();\n    void activityLockInactivityTimeoutSecChanged();\n    void activityLockOnWakeChanged();\n    void activityLockTouchUnlockChanged();\n    void activityLockSliderUnlockChanged();\n''')

replace_once("src/config/config.h",
'''    double m_touchSliderGainSeek;\n''',
'''    double m_touchSliderGainSeek;\n\n    bool m_activityLockEnabled = false;\n    int m_activityLockInactivityTimeoutSec = 0;\n    bool m_activityLockOnWake = false;\n    bool m_activityLockTouchUnlock = true;\n    bool m_activityLockSliderUnlock = true;\n''')

replace_once("src/config/config.cpp",
'''void Config::setTouchSliderGainSeek(double value)\n{\n    m_settings->setValue("touchslider/gainSeek", value);\n    emit touchSliderGainSeekChanged();\n}\n''',
'''void Config::setTouchSliderGainSeek(double value)\n{\n    m_settings->setValue("touchslider/gainSeek", value);\n    emit touchSliderGainSeekChanged();\n}\n\nbool Config::getActivityLockEnabled()\n{\n    return m_settings->value("activitylock/enabled", false).toBool();\n}\n\nvoid Config::setActivityLockEnabled(bool value)\n{\n    m_settings->setValue("activitylock/enabled", value);\n    emit activityLockEnabledChanged();\n}\n\nint Config::getActivityLockInactivityTimeoutSec()\n{\n    return m_settings->value("activitylock/inactivityTimeoutSec", 0).toInt();\n}\n\nvoid Config::setActivityLockInactivityTimeoutSec(int value)\n{\n    value = qBound(0, value, 1800);\n    m_settings->setValue("activitylock/inactivityTimeoutSec", value);\n    emit activityLockInactivityTimeoutSecChanged();\n}\n\nbool Config::getActivityLockOnWake()\n{\n    return m_settings->value("activitylock/onWake", false).toBool();\n}\n\nvoid Config::setActivityLockOnWake(bool value)\n{\n    m_settings->setValue("activitylock/onWake", value);\n    emit activityLockOnWakeChanged();\n}\n\nbool Config::getActivityLockTouchUnlock()\n{\n    return m_settings->value("activitylock/touchUnlock", true).toBool();\n}\n\nvoid Config::setActivityLockTouchUnlock(bool value)\n{\n    m_settings->setValue("activitylock/touchUnlock", value);\n    emit activityLockTouchUnlockChanged();\n}\n\nbool Config::getActivityLockSliderUnlock()\n{\n    return m_settings->value("activitylock/sliderUnlock", true).toBool();\n}\n\nvoid Config::setActivityLockSliderUnlock(bool value)\n{\n    m_settings->setValue("activitylock/sliderUnlock", value);\n    emit activityLockSliderUnlockChanged();\n}\n''')

# ---------------------------------------------------------------------------
# InputController: block navigation keys while still allowing volume/mute/play.
# Also expose a generic userActivity signal used by the inactivity timer.
# ---------------------------------------------------------------------------
replace_once("src/ui/inputController.h",
'''    Q_PROPERTY(int repeatCount READ getRepeatCount CONSTANT)\n''',
'''    Q_PROPERTY(int repeatCount READ getRepeatCount CONSTANT)\n    Q_PROPERTY(bool activityLockActive READ getActivityLockActive WRITE setActivityLockActive NOTIFY activityLockActiveChanged)\n''')
replace_once("src/ui/inputController.h",
'''    int     getRepeatCount() { return m_repeatCount; }\n''',
'''    int     getRepeatCount() { return m_repeatCount; }\n    bool    getActivityLockActive() const { return m_activityLockActive; }\n    void    setActivityLockActive(bool value);\n''')
replace_once("src/ui/inputController.h",
'''    void activeItemChanged();\n''',
'''    void activeItemChanged();\n    void activityLockActiveChanged();\n    void userActivity();\n''')
replace_once("src/ui/inputController.h",
'''    bool m_blockTouchInput = false;\n''',
'''    bool m_blockTouchInput = false;\n    bool m_activityLockActive = false;\n''')

replace_once("src/ui/inputController.cpp",
'''void InputController::blockInput(bool value) {\n''',
'''void InputController::setActivityLockActive(bool value) {\n    if (m_activityLockActive == value) {\n        return;\n    }\n    m_activityLockActive = value;\n    emit activityLockActiveChanged();\n}\n\nvoid InputController::blockInput(bool value) {\n''')

replace_once("src/ui/inputController.cpp",
'''            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            cancelDeferredRelease(key);\n''',
'''            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            emit userActivity();\n\n            if (m_activityLockActive && mappedKey != "VOLUME_UP" && mappedKey != "VOLUME_DOWN" &&\n                mappedKey != "MUTE" && mappedKey != "PLAY" && mappedKey != "POWER") {\n                event->accept();\n                return true;\n            }\n\n            cancelDeferredRelease(key);\n''',)

replace_once("src/ui/inputController.cpp",
'''            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            if (keyEvent->isAutoRepeat()) {\n''',
'''            if (mappedKey.isEmpty()) {\n                break;\n            }\n\n            if (m_activityLockActive && mappedKey != "VOLUME_UP" && mappedKey != "VOLUME_DOWN" &&\n                mappedKey != "MUTE" && mappedKey != "PLAY" && mappedKey != "POWER") {\n                event->accept();\n                return true;\n            }\n\n            if (keyEvent->isAutoRepeat()) {\n''',)

replace_once("src/ui/inputController.cpp",
'''        case QEvent::MouseButtonPress:\n        case QEvent::MouseButtonRelease:\n        case QEvent::TouchBegin:\n        case QEvent::TouchUpdate:\n        case QEvent::TouchEnd:\n        case QEvent::TouchCancel: {\n            if (m_blockTouchInput) {\n''',
'''        case QEvent::MouseButtonPress:\n        case QEvent::MouseButtonRelease:\n        case QEvent::TouchBegin:\n        case QEvent::TouchUpdate:\n        case QEvent::TouchEnd:\n        case QEvent::TouchCancel: {\n            if (event->type() == QEvent::MouseButtonPress || event->type() == QEvent::TouchBegin) {\n                emit userActivity();\n            }\n            if (m_blockTouchInput) {\n''')

# ---------------------------------------------------------------------------
# Touch slider: while the lock is active, existing slider consumers ignore the
# shared hardware gesture; ActivityLock still receives the raw signals.
# ---------------------------------------------------------------------------
replace_once("src/hardware/touchSlider.h",
'''    Q_PROPERTY(int touchXMax READ getTouchXMax CONSTANT)\n''',
'''    Q_PROPERTY(int touchXMax READ getTouchXMax CONSTANT)\n    Q_PROPERTY(bool activityLockActive READ getActivityLockActive WRITE setActivityLockActive NOTIFY activityLockActiveChanged)\n''')
replace_once("src/hardware/touchSlider.h",
'''    int getTouchXMax() { return m_touchXMax; }\n''',
'''    int getTouchXMax() { return m_touchXMax; }\n    bool getActivityLockActive() const { return m_activityLockActive; }\n    void setActivityLockActive(bool value) {\n        if (m_activityLockActive == value) return;\n        m_activityLockActive = value;\n        emit activityLockActiveChanged();\n    }\n''')
replace_once("src/hardware/touchSlider.h",
'''    void touchReleased();\n''',
'''    void touchReleased();\n    void activityLockActiveChanged();\n''')
replace_once("src/hardware/touchSlider.h",
'''    int m_touchXMax = 0;\n''',
'''    int m_touchXMax = 0;\n    bool m_activityLockActive = false;\n''')

# Add a guard to every existing QML consumer of the shared slider.
for rel in [
    "src/qml/components/TouchSliderVolume.qml",
    "src/qml/components/TouchSliderSeek.qml",
    "src/qml/components/TouchSliderBrightness.qml",
    "src/qml/components/TouchSliderPosition.qml",
]:
    text = read(rel)
    needle = '        function onTouchPressed() {\n'
    if needle not in text:
        raise RuntimeError(f"Touch slider handler not found in {rel}")
    text = text.replace(needle, needle + '            if (TouchSliderProcessor.activityLockActive) { return; }\n', 1)
    # Movement/release must also be ignored while locked. This prevents an already-open
    # slider from changing a value during a lock gesture.
    text = text.replace('        function onTouchXChanged(x) {\n', '        function onTouchXChanged(x) {\n            if (TouchSliderProcessor.activityLockActive) { return; }\n', 1)
    text = text.replace('        function onTouchReleased() {\n', '        function onTouchReleased() {\n            if (TouchSliderProcessor.activityLockActive) { return; }\n', 1)
    write(rel, text)

# ---------------------------------------------------------------------------
# New lock UI.
# ---------------------------------------------------------------------------
activity_lock = r'''import QtQuick 2.15
import QtQuick.Controls 2.15

import Config 1.0
import Power 1.0
import Power.Modes 1.0
import TouchSlider 1.0

Item {
    id: lock
    objectName: "activityLock"
    width: ui.width
    height: ui.height
    anchors.centerIn: parent
    visible: Config.activityLockEnabled
    enabled: visible
    z: 10000

    property bool locked: false
    property real touchStartX: 0
    property real sliderStartX: 0
    property bool sliderTracking: false
    readonly property real unlockDistance: width * 0.30

    function validUnlockMethod() {
        return Config.activityLockTouchUnlock || Config.activityLockSliderUnlock;
    }

    function setLocked(value) {
        if (!Config.activityLockEnabled) {
            locked = false;
            TouchSliderProcessor.activityLockActive = false;
            ui.inputController.activityLockActive = false;
            return;
        }
        if (value && !validUnlockMethod()) {
            // Safety: never enter a state without an available unlock method.
            locked = false;
            return;
        }
        locked = value;
        TouchSliderProcessor.activityLockActive = locked;
        ui.inputController.activityLockActive = locked;
        inactivityTimer.stop();
    }

    function resetInactivityTimer() {
        if (!Config.activityLockEnabled || locked || Config.activityLockInactivityTimeoutSec <= 0) {
            return;
        }
        inactivityTimer.restart();
    }

    function lockNow() {
        if (Config.activityLockEnabled && validUnlockMethod()) {
            setLocked(true);
        }
    }

    function unlock() {
        setLocked(false);
        resetInactivityTimer();
    }

    onVisibleChanged: {
        if (!visible) {
            setLocked(false);
        } else {
            resetInactivityTimer();
        }
    }

    Timer {
        id: inactivityTimer
        repeat: false
        interval: Math.max(1000, Config.activityLockInactivityTimeoutSec * 1000)
        onTriggered: lockNow()
    }

    Connections {
        target: Config
        ignoreUnknownSignals: true
        function onActivityLockEnabledChanged() {
            if (!Config.activityLockEnabled) {
                lock.setLocked(false);
            } else {
                lock.resetInactivityTimer();
            }
        }
        function onActivityLockInactivityTimeoutSecChanged() {
            inactivityTimer.interval = Math.max(1000, Config.activityLockInactivityTimeoutSec * 1000);
            lock.resetInactivityTimer();
        }
        function onActivityLockTouchUnlockChanged() {
            if (lock.locked && !lock.validUnlockMethod()) lock.setLocked(false);
        }
        function onActivityLockSliderUnlockChanged() {
            if (lock.locked && !lock.validUnlockMethod()) lock.setLocked(false);
        }
    }

    Connections {
        target: ui.inputController
        ignoreUnknownSignals: true
        function onUserActivity() {
            lock.resetInactivityTimer();
        }
    }

    Connections {
        target: Power
        ignoreUnknownSignals: true
        function onPowerModeChanged(fromPowerMode, toPowerMode) {
            if (!Config.activityLockEnabled || !Config.activityLockOnWake) return;
            if (toPowerMode === PowerModes.Normal &&
                (fromPowerMode === PowerModes.Low_power || fromPowerMode === PowerModes.Idle)) {
                lock.lockNow();
            }
        }
    }

    Connections {
        target: TouchSliderProcessor
        ignoreUnknownSignals: true
        function onTouchPressed() {
            if (!lock.locked || !Config.activityLockSliderUnlock) return;
            lock.sliderTracking = true;
            lock.sliderStartX = TouchSliderProcessor.touchX;
        }
        function onTouchXChanged(x) {
            if (!lock.locked || !lock.sliderTracking || !Config.activityLockSliderUnlock) return;
            if (x - lock.sliderStartX >= (TouchSliderProcessor.touchXMax > TouchSliderProcessor.touchXMin
                                          ? (TouchSliderProcessor.touchXMax - TouchSliderProcessor.touchXMin) * 0.70
                                          : 210)) {
                lock.sliderTracking = false;
                lock.unlock();
            }
        }
        function onTouchReleased() {
            lock.sliderTracking = false;
        }
    }

    MouseArea {
        id: touchGuard
        anchors.fill: parent
        enabled: lock.locked
        preventStealing: true
        propagateComposedEvents: false
        onPressed: {
            lock.touchStartX = mouse.x;
        }
        onReleased: {
            if (!Config.activityLockTouchUnlock) return;
            if (mouse.x - lock.touchStartX >= lock.unlockDistance) {
                lock.unlock();
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        visible: lock.locked
        color: "#000000"
        opacity: 0.88

        Column {
            anchors.centerIn: parent
            spacing: 24
            width: parent.width - 50

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
                text: {
                    if (Config.activityLockTouchUnlock && Config.activityLockSliderUnlock)
                        return qsTr("Swipe right on the screen or slide the touch slider fully to the right to unlock.");
                    if (Config.activityLockTouchUnlock)
                        return qsTr("Swipe right on the screen to unlock.");
                    return qsTr("Slide the touch slider fully to the right to unlock.");
                }
                font.pixelSize: 24
            }

            Rectangle {
                width: parent.width * 0.72
                height: 8
                radius: 4
                color: "#777777"
                anchors.horizontalCenter: parent.horizontalCenter

                Rectangle {
                    width: parent.width * 0.18
                    height: parent.height
                    radius: 4
                    color: "white"
                    anchors.left: parent.left
                }
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
'''
write("src/qml/components/ActivityLock.qml", activity_lock)

settings_page = r'''import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

import Config 1.0
import "qrc:/settings" as Settings
import "qrc:/components" as Components

Settings.Page {
    id: page

    Flickable {
        anchors { top: topNavigation.bottom; bottom: parent.bottom }
        width: parent.width
        contentWidth: width
        contentHeight: content.height + 30
        clip: true

        ColumnLayout {
            id: content
            width: parent.width
            spacing: 20

            function addSeparator() {
                return separatorComponent.createObject(content);
            }

            ColumnLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                spacing: 10
                RowLayout {
                    Text { Layout.fillWidth: true; color: colors.offwhite; text: qsTr("Activity / Child Lock"); font: fonts.primaryFont(30); wrapMode: Text.WordWrap }
                    Components.Switch {
                        id: enabledSwitch
                        checked: Config.activityLockEnabled
                        icon: "uc:check"
                        trigger: function() { Config.activityLockEnabled = !Config.activityLockEnabled; }
                    }
                }
                Text {
                    Layout.fillWidth: true
                    color: colors.light
                    text: qsTr("Protects the current activity and page against accidental touch or navigation input.")
                    font: fonts.secondaryFont(24)
                    wrapMode: Text.WordWrap
                }
            }

            Rectangle { Layout.fillWidth: true; Layout.leftMargin: 10; Layout.rightMargin: 10; height: 2; color: colors.medium }

            ColumnLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                spacing: 10
                RowLayout {
                    Text { Layout.fillWidth: true; color: colors.offwhite; text: qsTr("Lock after inactivity"); font: fonts.primaryFont(30); wrapMode: Text.WordWrap }
                    Text { color: colors.offwhite; text: Config.activityLockInactivityTimeoutSec === 0 ? qsTr("Off") : qsTr("%1 min").arg(Math.round(Config.activityLockInactivityTimeoutSec / 60)); font: fonts.primaryFont(26) }
                }
                Components.Slider {
                    id: timeoutSlider
                    Layout.fillWidth: true
                    from: 0
                    to: 30
                    stepSize: 1
                    value: Math.round(Config.activityLockInactivityTimeoutSec / 60)
                    showLiveValue: false
                    lowValueText: qsTr("Off")
                    highValueText: qsTr("30 min")
                    onMoved: Config.activityLockInactivityTimeoutSec = Math.round(value) * 60
                }
                Text { Layout.fillWidth: true; color: colors.light; text: qsTr("This timer is independent of the remote standby timer."); font: fonts.secondaryFont(24); wrapMode: Text.WordWrap }
            }

            Rectangle { Layout.fillWidth: true; Layout.leftMargin: 10; Layout.rightMargin: 10; height: 2; color: colors.medium }

            ColumnLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                spacing: 10
                RowLayout {
                    Text { Layout.fillWidth: true; color: colors.offwhite; text: qsTr("Lock when waking from standby"); font: fonts.primaryFont(30); wrapMode: Text.WordWrap }
                    Components.Switch {
                        id: wakeSwitch
                        checked: Config.activityLockOnWake
                        icon: "uc:check"
                        trigger: function() { Config.activityLockOnWake = !Config.activityLockOnWake; }
                    }
                }
            }

            Rectangle { Layout.fillWidth: true; Layout.leftMargin: 10; Layout.rightMargin: 10; height: 2; color: colors.medium }

            ColumnLayout {
                Layout.leftMargin: 10
                Layout.rightMargin: 10
                spacing: 10
                Text { color: colors.offwhite; text: qsTr("Unlock methods"); font: fonts.primaryFont(30) }
                RowLayout {
                    Text { Layout.fillWidth: true; color: colors.offwhite; text: qsTr("Touchscreen swipe"); font: fonts.primaryFont(26); wrapMode: Text.WordWrap }
                    Components.Switch { checked: Config.activityLockTouchUnlock; icon: "uc:check"; trigger: function() { Config.activityLockTouchUnlock = !Config.activityLockTouchUnlock; } }
                }
                RowLayout {
                    Text { Layout.fillWidth: true; color: colors.offwhite; text: qsTr("Touch slider"); font: fonts.primaryFont(26); wrapMode: Text.WordWrap }
                    Components.Switch { checked: Config.activityLockSliderUnlock; icon: "uc:check"; trigger: function() { Config.activityLockSliderUnlock = !Config.activityLockSliderUnlock; } }
                }
                Text { Layout.fillWidth: true; color: colors.light; text: qsTr("At least one unlock method is required. The lock will not activate if both are disabled."); font: fonts.secondaryFont(22); wrapMode: Text.WordWrap }
            }
        }
    }

    Component { id: separatorComponent; Rectangle { Layout.fillWidth: true; height: 2; color: colors.medium } }
}
'''
write("src/qml/settings/settings/ActivityLock.qml", settings_page)

# ---------------------------------------------------------------------------
# Main UI: import/instantiate lock overlay.
# ---------------------------------------------------------------------------
main = read("src/qml/main.qml")
if 'Components.ActivityLock' not in main:
    marker = '\n}\n'
    pos = main.rfind(marker)
    if pos < 0:
        raise RuntimeError("Could not locate ApplicationWindow closing brace in main.qml")
    insertion = '''\n    Components.ActivityLock {\n        id: activityLock\n        anchors.centerIn: parent\n    }\n'''
    main = main[:pos] + insertion + main[pos:]
    write("src/qml/main.qml", main)

# ---------------------------------------------------------------------------
# Settings menu and QRC.
# ---------------------------------------------------------------------------
replace_once("src/qml/settings/Settings.qml",
'''                {\n                    itemTitle: QT_TR_NOOP("Touch Slider"),\n                    page: "TouchSlider",\n                    icon: "uc:sliders"\n                },\n''',
'''                {\n                    itemTitle: QT_TR_NOOP("Touch Slider"),\n                    page: "TouchSlider",\n                    icon: "uc:sliders"\n                },\n                {\n                    itemTitle: QT_TR_NOOP("Activity / Child Lock"),\n                    page: "ActivityLock",\n                    icon: "uc:lock"\n                },\n''')

replace_once("resources/qrc/main.qrc",
'''        <file alias="settings/settings/TouchSlider.qml">../../src/qml/settings/settings/TouchSlider.qml</file>\n''',
'''        <file alias="settings/settings/TouchSlider.qml">../../src/qml/settings/settings/TouchSlider.qml</file>\n        <file alias="settings/settings/ActivityLock.qml">../../src/qml/settings/settings/ActivityLock.qml</file>\n''') if 'settings/settings/TouchSlider.qml' in read("resources/qrc/main.qrc") else None
# TouchSlider settings file is not necessarily in main.qrc on every upstream snapshot.
qrc = read("resources/qrc/main.qrc")
if 'settings/settings/ActivityLock.qml' not in qrc:
    anchor = '        <file alias="settings/settings/Ui.qml">../../src/qml/settings/settings/Ui.qml</file>\n'
    if anchor not in qrc:
        raise RuntimeError("QRC settings anchor not found")
    qrc = qrc.replace(anchor, anchor + '        <file alias="settings/settings/ActivityLock.qml">../../src/qml/settings/settings/ActivityLock.qml</file>\n', 1)
if 'components/ActivityLock.qml' not in qrc:
    anchor = '        <file alias="components/LoadingFirst.qml">../../src/qml/components/LoadingFirst.qml</file>\n'
    if anchor not in qrc:
        raise RuntimeError("QRC component anchor not found")
    qrc = qrc.replace(anchor, anchor + '        <file alias="components/ActivityLock.qml">../../src/qml/components/ActivityLock.qml</file>\n', 1)
write("resources/qrc/main.qrc", qrc)

print("Activity Lock patch applied successfully")
''