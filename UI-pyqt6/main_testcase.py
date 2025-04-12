from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer

import sys
import os
from serial import Serial
from time import sleep
import time
from cProfile import Profile
from pstats import SortKey, Stats
import pstats

# Add the relative path (this might work in some cases)
sys.path.append('../sgp4')

# Add the absolute path (this will work more reliably)
sgp4_path = 'C:/Users/Aidan/Desktop/STARR-LOC/sgp4'
sys.path.append(sgp4_path)

import sgp4_basic as sgpb
from observer import Observer
from satellite import Satellite
import pytz, datetime

import subprocess, multiprocessing

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
        if event.key() in (Qt.Key.Key_M, Qt.Key.Key_N, Qt.Key.Key_B, Qt.Key.Key_W, Qt.Key.Key_A, Qt.Key.Key_S, Qt.Key.Key_D, Qt.Key.Key_F) and not event.modifiers():
            event.ignore()
            return
        return super().keyPressEvent(event)

class MainWindow(QMainWindow):
    
    auto_track = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        # self.ser = Serial('/dev/ttyUSB0', 115200, timeout=1)
        # self.ser.rts = False
        # self.ser.dtr = False

        # Information gathering
        self.tle_file_path = "../bluetooth/tle.data"
        self.gps_file_path = "../bluetooth/gps.data"
        
        if os.path.exists(self.tle_file_path):
        
            self.tle_data = sgpb.read_tle_file(self.tle_file_path)

            self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in self.tle_data]

        if os.path.exists(self.gps_file_path):
            self.observer = Observer(file_path=self.gps_file_path)

        self.process = None
        self.process_running = False
        self.auto_track_process = multiprocessing.Process
        self.tracking_active = False
        self.tracked_satellite = None
                
        et = pytz.timezone("US/Eastern")
        local_time = datetime.datetime.now(et)
        # utc_time = local_time.astimezone(pytz.utc)
                
        # Set window title and size constraints
        self.setWindowTitle("PyQt6 Application for On-Device UI")
        self.setFixedSize(800, 480)

        # Create central widget and layout
        self.central_widget = QWidget()
        background_image = "Assets/star_background"
        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-image: url({background_image});            
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)
        self.setCentralWidget(self.central_widget)
        grid = QGridLayout(self.central_widget)

        # Sort list based on distance
        self.satellites = sorted(self.satellites, key=lambda sat: sat.getAngleFrom(self.observer, local_time)[2])
        
        # Create custom combo box and populate it
        self.combo_box = CustomComboBox()
        # options = [f"{sat.name} ({sat.getAngleFrom(self.observer, local_time)[2]:.2f} kilometers | Overhead: {sat.overhead})" for sat in self.satellites]
        # self.combo_box.addItems(options)
        self.combo_box.setFixedWidth(390)
        self.combo_box.setFixedHeight(40)
        
        # Call method for selected satellite
        self.combo_box.currentIndexChanged.connect(
            lambda: self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, local_time)
        )

        # Create entry widgets
        self.e1 = QLineEdit()
        self.e2 = QLineEdit()
        self.e3 = QLineEdit()
        self.e4 = QLineEdit()
        self.e5 = QLineEdit()
        self.e6 = QLineEdit()

        # Create interactable icons
        self.auto_image = QLabel(self.central_widget)
        self.auto_image.setGeometry(10, 400, 64, 64)
        pixmap1 = QPixmap('Assets/auto.png')
        pixmap1 = pixmap1.scaled(64, 64)
        self.auto_image.setPixmap(pixmap1)

        self.manual_image = QLabel(self.central_widget)
        self.manual_image.setGeometry(100, 400, 64, 64)
        pixmap2 = QPixmap('Assets/manual.png')
        pixmap2 = pixmap2.scaled(64, 64)
        self.manual_image.setPixmap(pixmap2)

        self.bluetooth_image = QLabel(self.central_widget)
        self.bluetooth_image.setGeometry(190, 400, 48, 64)
        pixmap3 = QPixmap('Assets/bluetooth.png')
        pixmap3 = pixmap3.scaled(48, 64)
        self.bluetooth_image.setPixmap(pixmap3)

        self.radio_image = QLabel(self.central_widget)
        self.radio_image.setGeometry(280, 400, 32, 64)
        pixmap4 = QPixmap('Assets/radio.png')
        pixmap4 = pixmap4.scaled(32, 64)
        self.radio_image.setPixmap(pixmap4)

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

        # Initialize flags
        self.auto_flag = False
        self.manual_flag = False
        self.combo_selected = False
        self.bluetooth_flag = False
        self.radio_flag = False

        # Temp code for testing
        self.step_amount = 0

        # Automatic mode flag
        self.auto_toggle_active = False

        # Refresh data timer
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.quick_data)
        self.data_timer.start(5000)

        self.reread_data()

        options = [f"{sat.name:20} | " if not sat.overhead else f"{sat.name:20} |     Overhead " for sat in self.satellites]
        self.combo_box.clear()
        self.combo_box.addItems(options)

    def eventFilter(self, obj, event):
        start_time = time.perf_counter()
        
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
            elif event.key() == Qt.Key.Key_F5:
                self.startBluetoothServer()
            elif event.key() == Qt.Key.Key_F6:
                self.tracked_satellite = None
                self.auto_track_process.terminate()
                self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, datetime.datetime.now(pytz.timezone("US/Eastern")))
            elif event.key() == Qt.Key.Key_F7:
                #print("Starting Process")
                self.tracked_satellite = self.satellites[self.combo_box.currentIndex()]
                self.auto_track_process = multiprocessing.Process(target=self.auto_tracking)
                self.auto_track_process.start()
                #self.auto_track.emit()
                pass
            elif event.key() == Qt.Key.Key_F8:
                self.showFullScreen()
            elif event.key() == Qt.Key.Key_F9:
                self.showMaximized()
    
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("eventFilter", duration_ms)

        # Pass the event to the default event filter
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_A:
            self.auto_flag = True
            self.combo_selected = False
            self.manual_flag = False
            self.bluetooth_flag = False
            self.radio_flag = False
            self.setAutoIconSelected()
        elif event.key() == Qt.Key.Key_W:
            self.auto_flag = False
            self.combo_selected = True
            self.manual_flag = False
            self.bluetooth_flag = False
            self.radio_flag = False
            self.setDropdownSelected()
        elif event.key() == Qt.Key.Key_S:
            self.auto_flag = False
            self.combo_selected = False
            self.manual_flag = True
            self.bluetooth_flag = False
            self.radio_flag = False
            self.setManualIconSelected()
        elif event.key() == Qt.Key.Key_D:
            self.auto_flag = False
            self.combo_selected = False
            self.manual_flag = False
            self.bluetooth_flag = True
            self.radio_flag = False
            self.setBluetoothIcon()
        elif event.key() == Qt.Key.Key_F:
            self.auto_flag = False
            self.combo_selected = False
            self.manual_flag = False
            self.bluetooth_flag = False
            self.radio_flag = True
            self.setRadioSelected()
        
        super().keyPressEvent(event)

    def setDropdownSelected(self):
        start_time = time.perf_counter()

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
        self.bluetooth_image.setStyleSheet("")
        self.radio_image.setStyleSheet("")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("drop down selected", duration_ms)
        
    def setManualIconSelected(self):
        start_time = time.perf_counter()
        
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
        self.bluetooth_image.setStyleSheet("")
        self.radio_image.setStyleSheet("")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("manual icon", duration_ms)

    def setAutoIconSelected(self):
        start_time = time.perf_counter()
        
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
        self.bluetooth_image.setStyleSheet("")
        self.radio_image.setStyleSheet("")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("auto icon", duration_ms)

    def setBluetoothIcon(self):
        start_time = time.perf_counter()
        
        self.auto_image.setStyleSheet("")
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
        self.bluetooth_image.setStyleSheet("border: 2px solid yellow")
        self.radio_image.setStyleSheet("")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("bluetooth icon", duration_ms)

    def setRadioSelected(self):
        start_time = time.perf_counter()
        
        self.auto_image.setStyleSheet("")
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
        self.bluetooth_image.setStyleSheet("")
        self.radio_image.setStyleSheet("border: 2px solid yellow")

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("radio icon", duration_ms)

    def sat_data(self, satellites, selected, observer, local_time):
        start_time = time.perf_counter()
        
        # Get data from the satellite object
        e2_data = satellites[selected].getAngleFrom(observer, local_time)
        
        e3_data = satellites[selected].nextOverhead(observer, local_time)
        e4_data = satellites[selected].overheadDuration(observer, local_time, next_overhead=e3_data)
        
        # e4_data = satellites[selected].getAngleFrom(observer, local_time)

        e5_data = f"Lat: {observer.lat:.2f}, Lon: {observer.lon:.2f}, Alt: {observer.alt:.2f}"
        
        # String formatting for displaying results
        e2_data = f"Azimuth: {e2_data[0][0]:.2f}, Elevation: {e2_data[1][0]:.2f}"
        e3_data = e3_data.astimezone(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")
        e4_data = f"Minutes: {e4_data[0]}, Seconds: {e4_data[1]}"
        # e4_data = str("-1")
        # e5_data = str(e5_data)
        
        # Pass satellite data into text boxes
        self.e1.setText("Satellite")
        self.e2.setText(e2_data)
        self.e3.setText(e3_data)
        self.e4.setText(e4_data)
        self.e5.setText(e5_data)

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("sat_data", duration_ms)

    def startBluetoothServer(self):
        start_time = time.perf_counter()

        if not self.process_running:
            self.process_running = True
            self.process = subprocess.Popen(['python3', '../bluetooth/btserver.py'],
                                   stdin=None,
                                   stdout=None,
                                   stderr=None)
            
            self.process.wait()
            print("Bluetooth server returned to main loop")
            self.process_running = False

            self.reread_data()

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("bluetooth server", duration_ms)

    def quick_data(self):
        start_time = time.perf_counter()
        
        current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))
        utc_time = current_time.astimezone(pytz.utc)
        #self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, utc_time)

        if self.tracked_satellite is not None:
            index = self.satellites.index(self.tracked_satellite)
            print(self.tracked_satellite)
        else:
            index = self.combo_box.currentIndex()
            print("No tracked satellite")

        e2_data = self.satellites[index].getAngleFrom(self.observer, utc_time)
        e2_data = f"Azimuth: {e2_data[0][0]:.2f}, Elevation: {e2_data[1][0]:.2f}"
        self.e2.setText(e2_data)

        for satellite in self.satellites:
            satellite.isOverhead(self.observer, utc_time)

        #sat_labels = [f"{sat.name:20} | {overhead:10} " for sat in self.satellites]
        sat_labels = [f"{sat.name:20} | " if not sat.overhead else f"{sat.name:20} |     Overhead " for sat in self.satellites]
        for i, text in enumerate(sat_labels):
            self.combo_box.setItemText(i, text)

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("quick_data", duration_ms)

    def reread_data(self, signum=None, frame=None):
            start_time = time.perf_counter()
            
            print("rereading data")
            self.tle_data = sgpb.read_tle_file("../bluetooth/tle.data")
            self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in self.tle_data]
            self.observer = Observer(file_path="../bluetooth/gps.data")
            
            self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, datetime.datetime.now(pytz.timezone("US/Eastern")))

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            self.log_timing("reread data", duration_ms)

    def auto_tracking(self):
        """
        Auto tracking loop
        """
        start_time = time.perf_counter()

        satellite = self.satellites[self.combo_box.currentIndex()]

        with open("auto_tracking_doc.txt", "a") as file:

            while (1):
                # Get the current time
                current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))
                current_time = current_time.astimezone(pytz.utc)

                # Get the satellite position and angle
                angle = satellite.getAngleFrom(self.observer, current_time)
                # Check if the satellite is overhead
                if angle[1] > 0: 
                    print(f"Satellite {satellite.name} is overhead at {current_time}", file=file)
                    print(f"{angle[0]=} & {angle[1]=}", file=file)
                    # Send motor command to ESP32
                    string = f"{angle[0]:.4f} {angle[1]:.4f} 0"
                    self.ser.write(string.encode())
                else:
                    print(f"Satellite {satellite.name} is not overhead at {current_time}", file=file)
                    self.tracked_satellite = None
                    self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, datetime.datetime.now(pytz.timezone("US/Eastern")))
                    break

                sleep(5)

        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        self.log_timing("auto tracking", duration_ms)

    def log_timing(self, method_name, duration_ms):
        """Log timing information to a file"""
        with open("main_ui_timing_log.txt", "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            f.write(f"{timestamp} - {method_name}: {duration_ms:.2f}ms\n")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.auto_track.connect(window.auto_tracking)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
