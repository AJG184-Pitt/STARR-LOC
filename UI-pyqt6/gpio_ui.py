from PyQt6.QtGui import QFont, QPixmap, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget, QVBoxLayout)
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QEvent, QTimer

import sys
import os
from serial import Serial

# Add the relative path (this might work in some cases)
sys.path.append('../sgp4')

# Add the absolute path (this will work more reliably)
sgp4_path = 'C:/Users/Aidan/Desktop/STARR-LOC/sgp4'
sys.path.append(sgp4_path)

import sgp4_basic as sgpb
from observer import Observer
from satellite import Satellite
import pytz, datetime

import subprocess

import RPi.GPIO as GPIO
import time

class GpioSetup():
    def __init__(self):
        # Pin numbers on Raspberry Pi
        # First encoder
        self.CLK_PIN = 25   # GPIO7 connected to the rotary encoder's CLK pin
        self.DT_PIN = 8     # GPIO8 connected to the rotary encoder's DT pin
        self.SW_PIN = 7     # GPIO25 connected to the rotary encoder's SW pin

        # Second encoder
        self.CLK_PIN_2 = 14
        self.DT_PIN_2 = 15
        self.SW_PIN_2 = 18

        self.DIRECTION_CW = 0
        self.DIRECTION_CCW = 1

        # First encoder state
        self.counter = 0
        self.direction = self.DIRECTION_CW
        self.CLK_state = 0
        self.prev_CLK_state = 0
        self.button_pressed = False
        self.prev_button_state = GPIO.HIGH

        # Second encoder state
        self.counter_2 = 0
        self.direction_2 = self.DIRECTION_CW
        self.CLK_state_2 = 0
        self.prev_CLK_state_2 = 0
        self.button_pressed_2 = False
        self.prev_button_state_2 = GPIO.HIGH

        # Configure GPIO pins
        GPIO.setmode(GPIO.BCM)
        
        # First encoder setup
        GPIO.setup(self.CLK_PIN, GPIO.IN)
        GPIO.setup(self.DT_PIN, GPIO.IN)
        GPIO.setup(self.SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Second encoder setup
        GPIO.setup(self.CLK_PIN_2, GPIO.IN)
        GPIO.setup(self.DT_PIN_2, GPIO.IN)
        GPIO.setup(self.SW_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Read the initial state of both rotary encoders' CLK pins
        self.prev_CLK_state = GPIO.input(self.CLK_PIN)
        self.prev_CLK_state_2 = GPIO.input(self.CLK_PIN_2)

    def read_encoder(self):
        # Read the current state of the first rotary encoder's CLK pin
        CLK_state = GPIO.input(self.CLK_PIN)

        pulse_difference = 0

        # If the state of CLK is changed, then pulse occurred
        # React to only the rising edge (from LOW to HIGH) to avoid double count
        if CLK_state != self.prev_CLK_state and CLK_state == GPIO.LOW:
            # If the DT state is HIGH, the encoder is rotating in counter-clockwise direction
            if GPIO.input(self.DT_PIN) == GPIO.HIGH:
                pulse_difference = -1
                self.direction = self.DIRECTION_CCW
            else:
                # The encoder is rotating in clockwise direction
                pulse_difference = 1
                self.direction = self.DIRECTION_CW

        # Save last CLK state
        self.prev_CLK_state = CLK_state
        return pulse_difference
    
    def read_encoder_2(self):
        # Read the current state of the second rotary encoder's CLK pin
        CLK_state_2 = GPIO.input(self.CLK_PIN_2)

        pulse_difference = 0

        # If the state of CLK is changed, then pulse occurred
        # React to only the rising edge (from LOW to HIGH) to avoid double count
        if CLK_state_2 != self.prev_CLK_state_2 and CLK_state_2 == GPIO.LOW:
            # If the DT state is HIGH, the encoder is rotating in counter-clockwise direction
            if GPIO.input(self.DT_PIN_2) == GPIO.HIGH:
                pulse_difference = -1
                self.direction_2 = self.DIRECTION_CCW
            else:
                # The encoder is rotating in clockwise direction
                pulse_difference = 1
                self.direction_2 = self.DIRECTION_CW

        # Save last CLK state
        self.prev_CLK_state_2 = CLK_state_2
        return pulse_difference
        
    def read_button(self):
        # State change detection for the first button
        button_state = GPIO.input(self.SW_PIN)
        if button_state != self.prev_button_state:
            time.sleep(0.1)  # Add a small delay to debounce
            if button_state == GPIO.LOW:
                self.button_pressed = True
            else:
                self.button_pressed = False

        self.prev_button_state = button_state
        return self.button_pressed
    
    def read_button_2(self):
        # State change detection for the second button
        button_state_2 = GPIO.input(self.SW_PIN_2)
        if button_state_2 != self.prev_button_state_2:
            time.sleep(0.1)  # Add a small delay to debounce
            if button_state_2 == GPIO.LOW:
                self.button_pressed_2 = True
            else:
                self.button_pressed_2 = False

        self.prev_button_state_2 = button_state_2
        return self.button_pressed_2

class CustomComboBox(QComboBox):
    """
    A combobox that ignores certain keys for user operation on other labels
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #27a7d8;
                border-radius: 5px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                color: white;
                font-family: JetBrains Mono;
                font-size: 14px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px; /* Adjust as needed */
                border-left-width: 1px;
                border-left-color: darkgrey;
                border-left-style: solid; 
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-image: none; /* Remove default arrow */
            }
            
            QComboBox::down-arrow {
                border-image: url('Assets/drop-arrow');
            }
            
            QComboBox QAbstractItemView {
                background-color: grey; /* Dark grey for dropdown items */
                color: white; /* Font color inside the dropdown */
                border: 1px solid #27a7d8;
                border-radius: 3px;
            }
        """)

    def keyPressEvent(self, event):
        # Ignore keys when no modifiers are pressed, but propagate to parent
        if event.key() in (Qt.Key.Key_M, Qt.Key.Key_N, Qt.Key.Key_B, Qt.Key.Key_J, Qt.Key.Key_K, Qt.Key.Key_L) and not event.modifiers():
            event.ignore()
            return
        return super().keyPressEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Information gathering
        # self.tle_file_path = "../bluetooth/tle.data"
        # self.gps_file_path = "../bluetooth/gps.data"
        # self.tle_data = sgpb.read_tle_file(self.tle_file_path)

        file_path = "../sgp4/tle.txt"
        self.tle_data = sgpb.read_tle_file(file_path)
        
        self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in self.tle_data]
        
        # observer = Observer(file_path=self.gps_file_path)
        observer = Observer(lat=40.4442, lon=-79.9557, alt=300)

        et = pytz.timezone("US/Eastern")
        local_time = datetime.datetime.now(et)
        # utc_time = local_time.astimezone(pytz.utc)
                
        # Set window title and size constraints
        self.setWindowTitle("PyQt6 Application for On-Device UI")
        self.setFixedSize(800, 480)

        # Create central widget and layout
        central_widget = QWidget()
        background_image = "Assets/star_background"
        central_widget.setStyleSheet(f"""
            QWidget {{
                background-image: url({background_image});            
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)

        # Sort list based on distance
        self.satellites = sorted(self.satellites, key=lambda sat: sat.getAngleFrom(observer, local_time)[2])
        
        # Create custom combo box and populate it
        self.combo_box = CustomComboBox()
        options = [f"{sat.name} ({sat.getAngleFrom(observer, local_time)[2][0]:.2f} kilometers | Overhead: {sat.overhead})" for sat in self.satellites]
        self.combo_box.addItems(options)
        self.combo_box.setFixedWidth(390)
        self.combo_box.setFixedHeight(40)
        
        # Call method for selected satellite
        self.combo_box.currentIndexChanged.connect(
            lambda: self.sat_data(self.satellites, self.combo_box.currentIndex(), observer, local_time)
        )

        # Create entry widgets
        self.e1 = QLineEdit()
        self.e2 = QLineEdit()
        self.e3 = QLineEdit()
        self.e4 = QLineEdit()
        self.e5 = QLineEdit()
        self.e6 = QLineEdit()

        # Create interactable icons
        self.auto_image = QLabel(central_widget)
        self.auto_image.setGeometry(10, 400, 64, 64)
        pixmap1 = QPixmap('Assets/auto.png')
        pixmap1 = pixmap1.scaled(64, 64)
        self.auto_image.setPixmap(pixmap1)

        self.manual_image = QLabel(central_widget)
        self.manual_image.setGeometry(100, 400, 64, 64)
        pixmap2 = QPixmap('Assets/manual.png')
        pixmap2 = pixmap2.scaled(64, 64)
        self.manual_image.setPixmap(pixmap2)

        self.bluetooth_image = QLabel(central_widget)
        self.bluetooth_image.setGeometry(190, 400, 48, 64)
        pixmap3 = QPixmap('Assets/bluetooth.png')
        pixmap3 = pixmap3.scaled(48, 64)
        self.bluetooth_image.setPixmap(pixmap3)

        # Labels for satellite information
        self.label1 = QLabel("Current Angle:")
        self.label2 = QLabel("Next Satellite Overhead Period:")
        self.label3 = QLabel("Current Overhead Duration:")
        self.label4 = QLabel("Max Angle:")
        self.label5 = QLabel("GPS Location:")

        edit_lines = [self.e1, self.e2, self.e3, self.e4, self.e5, self.e6]

        for line in edit_lines:
            line.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ff9a00;
                    border-radius: 5px;
                    padding: 1px 18px 1px 3px;
                    min-width: 6em;
                    color: white;
                    font-family: JetBrains Mono;
                    font-size: 14px
                }
            """)

        self.e1.setFixedWidth(390)
        self.e1.setFixedHeight(40)

        self.e2.setFixedWidth(390)
        self.e2.setFixedHeight(40)

        self.e3.setFixedWidth(390)
        self.e3.setFixedHeight(40)

        self.e4.setFixedWidth(390)
        self.e4.setFixedHeight(40)

        self.e5.setFixedWidth(390)
        self.e5.setFixedHeight(40)

        self.e6.setFixedWidth(390)
        self.e6.setFixedHeight(40)

        # Line edits and combo box
        grid.addWidget(self.combo_box, 5, 0)

        grid.addWidget(self.label1, 0, 1, alignment=Qt.AlignmentFlag.AlignBottom)
        grid.addWidget(self.e1, 1, 1)

        grid.addWidget(self.label2, 2, 1, alignment=Qt.AlignmentFlag.AlignBottom)
        grid.addWidget(self.e2, 3, 1)

        grid.addWidget(self.label3, 4, 1, alignment=Qt.AlignmentFlag.AlignBottom)
        grid.addWidget(self.e3, 5, 1)

        grid.addWidget(self.label4, 6, 1, alignment=Qt.AlignmentFlag.AlignBottom)
        grid.addWidget(self.e4, 7, 1)

        grid.addWidget(self.label5, 8, 1, alignment=Qt.AlignmentFlag.AlignBottom)
        grid.addWidget(self.e5, 9, 1)

        # Install event filter on the window itself
        self.installEventFilter(self)

        # Initialize flags for selection
        self.auto_flag = False
        self.manual_flag = False
        self.combo_selected = False
        self.bluetooth_selected = False
        
        # Initialize gpio class object
        self.gpio = GpioSetup()
        self.selected_labels = [0, 1, 2, 3]
        self.current_index = 0
        
        # Encoder checks
        self.encoder_timer = QTimer(self)
        self.encoder_timer.timeout.connect(self.update_current_index)
        self.encoder_timer.start(50)  # Check every 50ms

        # Encoder 2 checks
        self.encoder_2_timer = QTimer(self)
        self.encoder_2_timer.timeout.connect(self.update_second_encoder)
        self.encoder_2_timer.start(50)

        # Encoder button checks
        self.button_action_pending = False  # Add this as a class variable
        self.button2_action_pending = False  # Add this as a class variable
        self.encoder_timer = QTimer(self)
        self.encoder_timer.timeout.connect(self.update_button_1)  # Connect to new method
        self.encoder_timer.start(50)  # Check every 50ms
        
        # Temp code for testing
        self.step_amount = 0

        # Automatic mode flag
        self.auto_toggle_active = False

    def update_current_index(self):
        previous_index = self.current_index
        # Update current index based on encoder value
        self.encode = self.gpio.read_encoder()
        if self.encode == 1:
            self.current_index = (self.current_index + 1) % len(self.selected_labels)
        elif self.encode == -1:
            self.current_index = (self.current_index - 1) % len(self.selected_labels)
        
        # Update UI if index changed
        if previous_index != self.current_index:
            self.update_selection()

    def update_second_encoder(self):
        if self.combo_selected:
            encoder2_value = self.gpio.read_encoder_2()
            if encoder2_value == 1:
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(self.combo_box, key_event)
            elif encoder2_value == -1:
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(self.combo_box, key_event)

            if self.gpio.read_button_2() and not self.button2_action_pending:
                key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_F4, Qt.KeyboardModifier.NoModifier)
                QApplication.sendEvent(self.combo_box, key_event)
                self.button2_action_pending = True
            elif not self.gpio.read_button_2():
                self.button2_action_pending = False

    def update_selection(self):
        # Update UI based on current_index
        if self.current_index == 0:
            self.auto_flag = True
            self.combo_selected = False
            self.manual_flag = False
            self.bluetooth_selected = False
            self.setAutoIconSelected()
        elif self.current_index == 1:
            self.auto_flag = False
            self.combo_selected = True
            self.manual_flag = False
            self.bluetooth_selected = False
            self.setDropdownSelected()
        elif self.current_index == 2:
            self.auto_flag = False
            self.combo_selected = False
            self.manual_flag = True
            self.bluetooth_selected = False
            self.setManualIconSelected()
        elif self.current_index == 3:
            self.auto_flag = False
            self.combo_box = False
            self.manual_flag = False
        self.bluetooth_selected = True
        self.setBluetoothIconSelected()
        
    def update_button_1(self):
        # First update encoder position
        self.update_current_index()
        
        # Then check button state
        if self.gpio.read_button():
            # Button is pressed, handle based on current mode
            if self.auto_flag:
                if not self.button_action_pending:
                    self.auto_toggle_active = not self.auto_toggle_active
                    print(f"Auto toggle Mode: {'Active' if self.auto_toggle_active else 'Inactive'}")
            elif self.manual_flag:
                if self.button_action_pending == False:  # Prevent repeated actions
                    print("Manual mode pending integration")
                    self.manual_encoder_control()
                    self.button_action_pending = True
        else:
            # Button is released
            self.button_action_pending = False

    def manual_encoder_control(self):
        """
        Toggle-able serial control method that sends encoder values over serial.
        This method will run until the button is pressed again to exit.
        
        Designed to be called directly when the button is pressed.
        """
        # Flags to track state
        self.serial_active = not getattr(self, 'serial_active', False)
        
        # If we're turning off the connection, just exit
        if not self.serial_active:
            print("Stopping serial control")
            return
        
        print("Starting serial control")
        try:
            # Open serial connection
            ser = Serial('/dev/ttyUSB0', 115200, timeout=1)
            time.sleep(0.5)  # Give serial connection time to initialize
            
            print("Serial connection established")

            counter1 = 0
            counter2 = 0
            prev_1 = 0
            prev_2 = 0
            
            # Run until button is pressed again
            while self.serial_active:
                # Read encoder 1
                encoder1_change = self.gpio.read_encoder()
                encoder2_change = self.gpio.read_encoder_2()
                
                if encoder1_change != 0:
                    # Send encoder 1 data when it changes
                    if encoder1_change == 1:
                        counter1 += 1
                    elif encoder1_change == -1:
                        counter1 -= 1
                    
                    print(f"Encoder 1 w/ counter: {encoder1_change} {counter1}\n")
                
                elif encoder2_change != 0:
                    if encoder2_change == 1:
                        counter2 += 1
                    elif encoder2_change == -1:
                        counter2 -= 1
                    
                    if counter2 <= 0:
                        counter2 = 0
                    
                    print(f"Encoder 2 w/ counter: {encoder2_change} {counter2}")
                
                print(f"{counter1} {counter2}\n")
                if prev_1 != counter1 or prev_2 != counter2:
                    send_data = f"{counter1} {counter2}\n"
                    ser.write(send_data.encode())

                    prev_1 = counter1
                    prev_2 = counter2
                
                # if encoder2_change != 0:
                #     # Send encoder 2 data when it changes
                #     print(f"Sending encoder 2: {encoder2_change}")
                #     ser.write(f"E2:{encoder2_change}\n".encode())
                
                # Check if button is pressed to exit the loop
                if self.gpio.read_button() == True:
                    time.sleep(0.1)  # Debounce
                    print("Button pressed, exiting serial control")
                    self.serial_active = False
                    break
                
                time.sleep(0.01)  # Small delay to prevent CPU hogging
                
        except Exception as e:
            print(f"Serial communication error: {e}")
        finally:
            try:
                ser.close()
                print("Serial connection closed")
            except:
                pass
            self.serial_active = False
        
    def eventFilter(self, obj, event):
        # Check if the event is a key press event
        if event.type() == QEvent.Type.KeyPress:
            # Check for Z key specifically
            if event.key() == Qt.Key.Key_B:
                # Only process if in auto mode
                if self.auto_flag:
                    print("Automatic Mode: On")
                    # Return True to indicate the event has been handled
                    return True

            # Check for N key and manual flag to print
            if event.key() == Qt.Key.Key_N:
                if self.manual_flag:
                    print(f"Example Step: {self.step_amount}")
                    self.step_amount -= 1
                    return True
            # Check for M key and manual flag to print
            elif event.key() == Qt.Key.Key_M:
                if self.manual_flag:
                    print(f"Example Step: {self.step_amount}")
                    self.step_amount += 1
                    return True
        
        # Pass the event to the default event filter
        return super().eventFilter(obj, event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_J:
           self.auto_flag = True
           self.combo_selected = False
           self.manual_flag = False
           self.setAutoIconSelected()
        elif event.key() == Qt.Key.Key_K:
            self.auto_flag = False
            self.combo_selected = True
            self.manual_flag = False
            self.setDropdownSelected()
        elif event.key() == Qt.Key.Key_L:
            self.auto_flag = False
            self.combo_selected = False
            self.manual_flag = True
            self.setManualIconSelected()

        super().keyPressEvent(event)

    def setDropdownSelected(self):
        index = self.combo_box.currentIndex()
        self.combo_box.setCurrentIndex(index)
        self.combo_box.setStyleSheet("""
            QComboBox {
                border: 2px solid yellow;
                border-radius: 5px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                color: white;
                font-family: JetBrains Mono;
                font-size: 14px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px; /* Adjust as needed */
                border-left-width: 1px;
                border-left-color: darkgrey;
                border-left-style: solid; 
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-image: none; /* Remove default arrow */
            }
            
            QComboBox::down-arrow {
                border-image: url('Assets/drop-arrow');
            }
            
            QComboBox QAbstractItemView {
                background-color: grey; /* Dark grey for dropdown items */
                color: white; /* Font color inside the dropdown */
                border: 1px solid #27a7d8;
                border-radius: 3px;
            }
        """)
        self.manual_image.setStyleSheet("")
        self.auto_image.setStyleSheet("")
        
    def setManualIconSelected(self):
        self.manual_image.setStyleSheet("border: 2px solid yellow")
        self.auto_image.setStyleSheet("")
        self.combo_box.setStyleSheet("""
            QComboBox {
                border: 1px solid #27a7d8;
                border-radius: 5px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                color: white;
                font-family: JetBrains Mono;
                font-size: 14px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px; /* Adjust as needed */
                border-left-width: 1px;
                border-left-color: darkgrey;
                border-left-style: solid; 
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-image: none; /* Remove default arrow */
            }
            
            QComboBox::down-arrow {
                border-image: url('Assets/drop-arrow');
            }
            
            QComboBox QAbstractItemView {
                background-color: grey; /* Dark grey for dropdown items */
                color: white; /* Font color inside the dropdown */
                border: 1px solid #27a7d8;
                border-radius: 3px;
            }
        """)

    def setAutoIconSelected(self):
        self.auto_image.setStyleSheet("border: 2px solid yellow")
        self.manual_image.setStyleSheet("")
        self.combo_box.setStyleSheet("""
            QComboBox {
                border: 1px solid #27a7d8;
                border-radius: 5px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                color: white;
                font-family: JetBrains Mono;
                font-size: 14px;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px; /* Adjust as needed */
                border-left-width: 1px;
                border-left-color: darkgrey;
                border-left-style: solid; 
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-image: none; /* Remove default arrow */
            }
            
            QComboBox::down-arrow {
                border-image: url('Assets/drop-arrow');
            }
            
            QComboBox QAbstractItemView {
                background-color: grey; /* Dark grey for dropdown items */
                color: white; /* Font color inside the dropdown */
                border: 1px solid #27a7d8;
                border-radius: 3px;
            }
        """)

    def setBluetoothIconSelected(self):
        return 0

    def sat_data(self, satellites, selected, observer, local_time):
        # Get data from the satellite object
        e1_data = satellites[selected].getAngleFrom(observer, local_time)
        
        e2_data = satellites[selected].nextOverhead(observer, local_time)
        e3_data = satellites[selected].overheadDuration(observer, local_time, next_overhead=e2_data)
        
        # e4_data = satellites[selected].getAngleFrom(observer, local_time)

        e5_data = str(observer.lat) + " , " + str(observer.lon) + " , " + str(observer.alt)
        
        # String formatting for displaying results
        e1_data = "AZ: " + str(e1_data[0][0]) + " , " + "EL: " + str(e1_data[1][0])
        e2_data = e2_data.strftime("%Y-%m-%d %H:%M:%S")
        e3_data = str(e3_data)
        e4_data = str("-1")
        # e5_data = str(e5_data)
        
        # Pass satellite data into text boxes
        self.e1.setText(e1_data)
        self.e2.setText(e2_data)
        self.e3.setText(e3_data)
        self.e4.setText(e4_data)
        self.e5.setText(e5_data)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
