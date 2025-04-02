from PyQt6.QtGui import QFont, QPixmap, QKeyEvent, QColor, QPainter
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget, QVBoxLayout, QStyledItemDelegate)
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QEvent

import sys
import os
import serial

ser = serial.Serial("/dev/ttyACM0", 115200)


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
    

class ColorDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, sats=None, observer=None):
        self.satellites = sats
        self.observer = observer
        super().__init__(parent)

    def paint(self, painter: QPainter, option, index):

        satellite = next((sat for sat in self.satellites if sat.name == index.data), None)
        if satellite is not None:
            el_angle = satellite.getAngleFrom(self.observer, datetime.datetime.now(pytz.timezone("US/Eastern")))[1]
            color_index = 0
            print(f"name = {self.satellites[satellite_index].name}")
            print(f"angle = {el_angle}")
            if el_angle > 30:
                color_index = 2
            elif el_angle > 0:
                color_index = 1
            else:
                color_index = 0

            colors = {
                0: QColor(255, 200, 200),
                1: QColor(80, 252, 234),
                2: QColor(173, 153, 162),
                }

            painter.fillRect(option.rect, colors[color_index])
            super().paint(painter, option, index)


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
        
        self.showFullScreen()

        self.fake_datetime = datetime.datetime(year=2025, month=4, day=2, hour=12, minute=10, second=0)

        # Information gathering
        # self.tle_file_path = "../bluetooth/tle.data"
        # self.gps_file_path = "../bluetooth/gps.data"
        # self.tle_data = sgpb.read_tle_file(self.tle_file_path)

        #file_path = "../sgp4/tle.txt"
        if os.path.exists("../bluetooth/tle.data"):

            self.tle_data = sgpb.read_tle_file("../bluetooth/tle.data")
        
            self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in self.tle_data]
        
        # observer = Observer(file_path=self.gps_file_path)
        self.observer = Observer(lat=40.4442, lon=-79.9557, alt=300)

        self.process = None
        self.process_running = False

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
        self.satellites = sorted(self.satellites, key=lambda sat: sat.getAngleFrom(observer, local_time)[2])
        
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
                self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, datetime.datetime.now(pytz.timezone("US/Eastern")))
            elif event.key() == Qt.Key.Key_F7:
                index = self.combo_box.currentIndex()
                angle = self.satellites[index].getAngleFrom(self.observer, self.fake_datetime)
                self.fake_datetime += datetime.timedelta(seconds=60)
                print(f"{angle=}")
                if angle[1] > 0:
                    print("Sending motor command to esp32")
                    string = f"{angle[0]} {angle[1]}"
                    ser.write(string.encode())
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
        # Get data from the satellite object
        e1_data = satellites[selected].getAngleFrom(observer, local_time)
        
        e2_data = satellites[selected].nextOverhead(observer, local_time)
        e3_data = satellites[selected].overheadDuration(observer, local_time, next_overhead=e2_data)
        
        # e4_data = satellites[selected].getAngleFrom(observer, local_time)

        e5_data = str(observer.lat) + " , " + str(observer.lon) + " , " + str(observer.alt)
        
        # String formatting for displaying results
        e1_data = "AZ: " + str(e1_data[0]) + " , " + "EL: " + str(e1_data[1])
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

            self.tle_data = sgpb.read_tle_file("../bluetooth/tle.data")
            self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in self.tle_data]
            self.observer = Observer(file_path="../bluetooth/gps.data")
            print("Bluetooth server updated TLE data and GPS data")

            self.sat_data(self.satellites, self.combo_box.currentIndex(), self.observer, datetime.datetime.now(pytz.timezone("US/Eastern")))

            options = [sat.name for sat in self.satellites]
            self.combo_box.clear()
            self.combo_box.addItems(options)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
