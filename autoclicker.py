import sys
import time
import random
from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from pynput.mouse import Button
from pynput.mouse import Controller as mController, Listener as mListener
from pynput.keyboard import Controller as kController, Listener as kListener


class KeyboardClicker(qtc.QObject):

    def __init__(self, key, delay, variation):
        super().__init__()
        self.keyboard = kController()
        self.key = key
        self.delay = delay
        self.variation = variation / 1000
        self.flag = False

    def tap(self):
        while self.flag:
            if self.variation < self.delay:
                delay = random.uniform(self.delay - self.variation, self.delay + self.variation)
            else:
                delay = random.uniform(0, 2 * self.delay)
            time.sleep(delay)
            self.keyboard.tap(eval(self.key))

    def run(self):
        self.flag = True
        self.tap()

    def stop(self):
        self.flag = False


class MouseClicker(qtc.QObject):

    def __init__(self, key, delay, variation):
        super().__init__()
        self.mouse = mController()
        self.key = key
        self.delay = delay
        self.variation = variation / 1000
        self.flag = False

    def click(self):
        while self.flag:
            if self.variation < self.delay:
                delay = random.uniform(self.delay - self.variation, self.delay + self.variation)
            else:
                delay = random.uniform(0, 2 * self.delay)
            time.sleep(delay)
            self.mouse.click(self.key)

    def run(self):
        self.flag = True
        self.click()

    def stop(self):
        self.flag = False


class Listeners(qtc.QThread):

    pressed = qtc.Signal(bool, str)

    def __init__(self):
        super().__init__()
        self.klistener = kListener(on_release=self.on_release,
                                   on_press=self.on_press)

    def on_release(self, key):
        self.pressed.emit(False, str(key))

    def on_press(self, key):
        self.pressed.emit(True, str(key))

    def run(self):
        self.klistener.start()


class GetPressedKey(qtc.QThread):
    # used in get_trigger_key and get_other_button

    key_pressed_signal = qtc.Signal(str)

    def __init__(self):
        super().__init__()
        self.klistener = kListener(on_release=self.on_release)
        self.mlistener = mListener(on_click=self.on_click)

    def on_release(self, key):
        self.key_pressed_signal.emit(str(key))
        self.klistener.stop()
        self.mlistener.stop()

    def on_click(self, x, y, key, pressed):
        self.key_pressed_signal.emit(str(key))
        self.klistener.stop()
        self.mlistener.stop()

    def run(self):
        self.klistener.start()
        self.mlistener.start()


class MainWindow(qtw.QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Main UI code goes here
        self.setWindowTitle("Clicker")
        self.status = qtw.QLabel("Status: Idle", font=qtg.QFont("Calibri", 24))

        self.cps_label = qtw.QLabel("Clicks/s")
        self.cps_input = qtw.QLineEdit("10")
        self.cps_input_validator = qtg.QIntValidator()
        self.cps_input_validator.setRange(0, 100)
        self.cps_input.setValidator(self.cps_input_validator)
        self.trigger_label = qtw.QLabel("Trigger")
        self.trigger_input = qtw.QPushButton("key")

        self.stop_button = qtw.QPushButton("Stop Everything")

        self.time_variation = qtw.QSpinBox(maximum=1000)
        self.time_variation_label = qtw.QLabel("ms")

        self.press_button = qtw.QRadioButton("Press")
        self.toggle_button = qtw.QRadioButton("Toggle")
        self.press_button.setChecked(True)

        self.left_click_button = qtw.QRadioButton("Left")
        self.middle_click_button = qtw.QRadioButton("Middle")
        self.right_click_button = qtw.QRadioButton("Right")
        self.other_key_button = qtw.QRadioButton("Other")
        self.other_key_input = qtw.QPushButton("None")
        self.left_click_button.setChecked(True)

        # Layouts
        # Shows status
        main_layout = qtw.QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.status)

        # Shows CPS and trigger button
        first_settings = qtw.QFormLayout()
        first_settings.addRow(self.cps_label, self.cps_input)
        first_settings.addRow(self.trigger_label, self.trigger_input)
        first_settings.addRow(self.stop_button)
        main_layout.addLayout(first_settings)

        # Shows click time variation widget
        click_variation_group = qtw.QGroupBox("Click Time Variation")
        click_variation_group.setLayout(qtw.QHBoxLayout())
        click_variation_group.layout().addWidget(self.time_variation)
        click_variation_group.layout().addWidget(self.time_variation_label)
        main_layout.addWidget(click_variation_group)

        # Shows press/toggle widget
        press_toggle_group = qtw.QGroupBox("Press/Toggle")
        press_toggle_group.setLayout(qtw.QVBoxLayout())
        press_toggle_group.layout().addWidget(self.press_button)
        press_toggle_group.layout().addWidget(self.toggle_button)
        self.press_toggle_bgroup = qtw.QButtonGroup()
        self.press_toggle_bgroup.addButton(self.press_button, 0)
        self.press_toggle_bgroup.addButton(self.toggle_button, 1)
        main_layout.addWidget(press_toggle_group)

        # Shows the button being clicked
        button_to_click_group = qtw.QGroupBox("Button to Click")
        button_to_click_group.setLayout(qtw.QVBoxLayout())
        button_to_click_group.layout().addWidget(self.left_click_button)
        button_to_click_group.layout().addWidget(self.middle_click_button)
        button_to_click_group.layout().addWidget(self.right_click_button)
        other_key_layout = qtw.QHBoxLayout()
        other_key_layout.addWidget(self.other_key_button)
        other_key_layout.addWidget(self.other_key_input)
        button_to_click_group.layout().addLayout(other_key_layout)
        self.button_to_click_bgroup = qtw.QButtonGroup()
        self.button_to_click_bgroup.addButton(self.left_click_button, 0)
        self.button_to_click_bgroup.addButton(self.middle_click_button, 1)
        self.button_to_click_bgroup.addButton(self.right_click_button, 2)
        self.button_to_click_bgroup.addButton(self.other_key_button, 3)
        main_layout.addWidget(button_to_click_group)

        # End main UI code

        # Initialize variables
        self.cps = 10
        self.delay = 0.1
        self.click_variation_time = 0
        self.ready_to_get_other = False
        self.no_listeners = True
        self.click_mode = "Press"
        self.clicking = False
        self.button_to_click = Button.left
        self.pressed_held = False

        # Signal/Slot Connections Stuff
        self.cps_input.textChanged.connect(self.change_cps)
        self.stop_button.clicked.connect(self.stop)
        self.trigger_input.clicked.connect(self.get_trigger_key)
        self.time_variation.valueChanged.connect(self.change_click_variation)
        self.press_toggle_bgroup.buttonClicked.connect(self.set_click_mode)
        self.button_to_click_bgroup.buttonClicked.connect(self.set_button_to_click)
        self.other_key_input.clicked.connect(self.get_other_button)

        self.show()

    def change_cps(self, cps):
        self.cps = cps
        if self.cps == "0":
            self.delay = 10
        elif self.cps:
            self.delay = 1 / float(self.cps)

    def get_trigger_key(self):
        self.trigger_input.setText("press a trigger key")
        self.gpk = GetPressedKey()
        self.gpk.start()
        # connect the signal from gpk to change_trigger_key_text
        self.gpk.key_pressed_signal.connect(self.change_trigger_key_text)

    @qtc.Slot(str)
    def change_trigger_key_text(self, key):
        self.gpk.deleteLater()
        if key:
            self.trigger_key = key
            self.trigger_input.setText(key)
            self.start_listeners()
        else:
            self.trigger_input.setText("click again")

    def change_click_variation(self, value):
        self.click_variation_time = value

    def set_click_mode(self, button):
        if button.text() == "Press":
            self.click_mode = "Press"
            self.ls.pressed.disconnect()
            self.ls.pressed.connect(self.start_clicking)
        elif button.text() == "Toggle":
            self.click_mode = "Toggle"
            self.ls.pressed.disconnect()
            self.ls.pressed.connect(self.start_toggle_click)

    def set_button_to_click(self, button):
        self.other_key_input.setText("key2")
        if button.text() == "Left":
            self.button_to_click = Button.left
            self.ready_to_get_other = False
        elif button.text() == "Middle":
            self.button_to_click = Button.middle
            self.ready_to_get_other = False
        elif button.text() == "Right":
            self.button_to_click = Button.right
            self.ready_to_get_other = False
        elif button.text() == "Other":
            # for retrieving the 'other' button
            self.ready_to_get_other = True
            self.button_to_click = None

    def get_other_button(self):
        if self.ready_to_get_other:
            self.other_key_input.setText("press key to click")
            self.gpk = GetPressedKey()
            self.gpk.start()
            self.gpk.key_pressed_signal.connect(self.change_other_button_text)

    @qtc.Slot(str)
    def change_other_button_text(self, key):
        self.gpk.deleteLater()
        self.button_to_click = key
        self.other_key_input.setText(key)

    def start_listeners(self):
        if self.no_listeners:
            self.no_listeners = False
            self.ls = Listeners()
            self.ls.start()
            self.ls.pressed.connect(self.start_clicking if self.click_mode == "Press" else self.start_toggle_click)

    def stop(self):
        self.clicker.stop()
        self.status.setText("Status: Idle")

    @qtc.Slot(bool, str)
    def start_clicking(self, pressed, button):
        if self.cps and self.click_mode and self.button_to_click and button == self.trigger_key:
            if button and pressed:
                if not self.pressed_held:
                    self.pressed_held = True
                    try:
                        if self.click_thread.isFinished():
                            self.click_thread = qtc.QThread()
                        else:
                            return -1
                    except AttributeError:
                        self.click_thread = qtc.QThread()
                    if str(self.button_to_click).count("Button"):
                        self.clicker = MouseClicker(self.button_to_click, self.delay, self.click_variation_time)
                    else:
                        self.clicker = KeyboardClicker(self.button_to_click, self.delay, self.click_variation_time)
                    self.clicker.moveToThread(self.click_thread)
                    self.click_thread.started.connect(self.clicker.run)
                    self.click_thread.start()
                    self.status.setText("Status: Clicking")
            else:
                self.clicker.stop()
                self.click_thread.exit()
                self.pressed_held = False
                self.status.setText("Status: Idle")

    @qtc.Slot(bool, str)
    def start_toggle_click(self, pressed, button):
        if self.cps and self.click_mode and self.button_to_click and button == self.trigger_key:
            if button and not(pressed):
                if not(self.clicking):
                    try:
                        if self.click_thread.isFinished():
                            self.click_thread = qtc.QThread()
                        else:
                            return -1
                    except AttributeError:
                        self.click_thread = qtc.QThread()
                    if str(self.button_to_click).count("Button"):
                        self.clicker = MouseClicker(self.button_to_click, self.delay, self.click_variation_time)
                    else:
                        self.clicker = KeyboardClicker(self.button_to_click, self.delay, self.click_variation_time)
                    self.clicker.moveToThread(self.click_thread)
                    self.click_thread.started.connect(self.clicker.run)
                    self.click_thread.start()
                    self.clicking = True
                    self.status.setText("Status: Clicking")
                else:
                    self.clicker.stop()
                    self.click_thread.exit()
                    self.clicking = False
                    self.status.setText("Status: Idle")


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec())
