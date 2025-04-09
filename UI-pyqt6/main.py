from PyQt6.QtGui import QFont, QPixmap, QKeyEvent, QColor, QPainter
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget, QVBoxLayout, QStyledItemDelegate)
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QEvent, QTimer, pyqtSignal

import sys
import os
import serial
import signal
from time import sleep
import functools

ser = serial.Serial("/dev/ttyUSB0", 115200, rtscts=False, dsrdtr=False)
ser.rts = False
ser.dtr = False

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
import multiprocessing
    

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

    auto_track = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.showFullScreen()

        self.fake_datetime = datetime.datetime(year=2025, month=4, day=2, hour=12, minute=10, second=0)

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
        
        # Initialize flags
        self.auto_flag = False
        self.manual_flag = False
        self.combo_selected = False
        
        # Sort list based on distance
        self.satellites = sorted(self.satellites, key=lambda sat: sat.getAngleFrom(self.observer, local_time)[2])
        
        # Create custom combo box and populate it
        self.combo_box = CustomComboBox()
        #options = [f"{sat.name} ({sat.getAngleFrom(observer, local_time)[2][0]:.2f} kilometers | Overhead: {sat.overhead})" for sat in self.satellites]
        #self.combo_box.addItems(options)
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

        # Example step counter for manual operation
        self.step_amount = 0
        
        # Install event filter on the window itself
        self.installEventFilter(self)

        #self.serial = QtSerialPort.QtSerialPort('/dev/ttyUSB0', baudRate=115200)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.quick_data)
        self.timer.start(5000)


        #signal.signal(signal.SIGALRM, self.quick_data)
        #signal.setitimer(signal.ITIMER_REAL, 5, 5)

        self.reread_data()


        options = [f"{sat.name:20} | {sat.overhead:10} " for sat in self.satellites]
        self.combo_box.clear()
        self.combo_box.addItems(options)


    def eventFilter(self, obj, event):
        # Check if the event is a key press event
        if event.type() == QEvent.Type.KeyPress:
            # Check for Z key specifically
            if event.key() == Qt.Key.Key_B:
                # Only process if in auto mode
                if self.auto_flag:
                    print("sending data: 1")
                    print("sending data: 2")
                    print("sending data: 3")
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
                self.auto_track_process.terminate()
                pass
            elif event.key() == Qt.Key.Key_F7:
                #self.fake_datetime += datetime.timedelta(seconds=60)
                print("Starting Process")
                self.auto_track_process = multiprocessing.Process(target=self.auto_tracking)
                self.auto_track_process.start()
                #self.auto_track.emit()

                #if angle[1] > 0:
                    #print("Sending motor command to esp32")
                    #string = f"{angle[0]} {angle[1]}"
                    #ser.write(string.encode())
            elif event.key() == Qt.Key.Key_F8:
                self.showFullScreen()
            elif event.key() == Qt.Key.Key_F9:
                self.showMaximized()
        
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

    def sat_data(self, satellites, selected, observer, local_time):
        print("sat data")
        # Get data from the satellite object
        
        e1_data = satellites[selected].getAngleFrom(observer, local_time)
        
        e2_data = satellites[selected].nextOverhead(observer, local_time)
        e3_data = satellites[selected].overheadDuration(observer, local_time, next_overhead=e2_data)
        
        # e4_data = satellites[selected].getAngleFrom(observer, local_time)

        #e5_data = str(observer.lat) + " , " + str(observer.lon) + " , " + str(observer.alt)
        e5_data = f"Lat: {observer.lat:.2f}, Lon: {observer.lon:.2f}, Alt: {observer.alt:.2f}"
        
        # String formatting for displaying results
        #e1_data = "AZ: " + str(e1_data[0]) + " , " + "EL: " + str(e1_data[1])
        e1_data = f"Azimuth: {e1_data[0]:.2f}, Elevation: {e1_data[1]:.2f}"
        e2_data = e2_data.astimezone(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")
        #e3_data = str(e3_data)
        e3_data = f"Minutes : {e3_data[0]}, Seconds: {e3_data[1]}"
        e4_data = str("-1")
        # e5_data = str(e5_data)
        
        # Pass satellite data into text boxes
        self.e1.setText(e1_data)
        self.e2.setText(e2_data)
        self.e3.setText(e3_data)
        self.e4.setText(e4_data)
        self.e5.setText(e5_data)

    def startBluetoothServer(self):
        
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

    def quick_data(self):
        print("quick data")
        time = datetime.datetime.now(pytz.timezone("US/Eastern"))
        #time = datetime.datetime.now()
        utc_time = time.astimezone(pytz.utc)
        self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, utc_time)

        for satellite in self.satellites:
            satellite.isOverhead(self.observer, utc_time)

        #sat_labels = [f"{sat.name:20} | {overhead:10} " for sat in self.satellites]
        sat_labels = [f"{sat.name:20} | " if not sat.overhead else f"{sat.name:20} |     Overhead " for sat in self.satellites]
        for i, text in enumerate(sat_labels):
            self.combo_box.setItemText(i, text)



    def reread_data(self, signum=None, frame=None):

            print("rereading data")
            self.tle_data = sgpb.read_tle_file("../bluetooth/tle.data")
            self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in self.tle_data]
            self.observer = Observer(file_path="../bluetooth/gps.data")
            
            self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, datetime.datetime.now(pytz.timezone("US/Eastern")))




    def auto_tracking(self):
        """
        Auto tracking loop
        """
        satellite = self.satellites[self.combo_box.currentIndex()]

        with open("auto_tracking_doc.txt", "a") as file:

            while (1):
                # Get the current time
                current_time = datetime.datetime.now(pytz.timezone("US/Eastern"))
                current_time = current_time.astimezone(pytz.utc)
                #current_time += datetime.timedelta(seconds=5)

                # Get the satellite position and angle
                angle = satellite.getAngleFrom(self.observer, current_time)
                # Check if the satellite is overhead
                #if satellite.isOverhead(self.observer, current_time):
                if angle[1] > 0: 
                    print(f"Satellite {satellite.name} is overhead at {current_time}", file=file)
                    print(f"{angle[0]=} & {angle[1]=}", file=file)
                    # Send motor command to ESP32
                    string = f"{angle[0]:.4f} {angle[1]:.4f} 0"
                    ser.write(string.encode())
                    #self.serial.write(string.encode())
                else:
                    print(f"Satellite {satellite.name} is not overhead at {current_time}", file=file)
                    break

                sleep(5)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.auto_track.connect(window.auto_tracking)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
