from PyQt6.QtGui import QFont, QPixmap, QKeyEvent
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget, QVBoxLayout)
from PyQt6.QtCore import QSize, Qt, pyqtSignal

import sys
sys.path.append('../sgp4')

import sgp4_basic as sgpb
from observer import Observer
from satellite import Satellite
import pytz, datetime

import subprocess

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Information gathering
        # self.tle_file_path = "../bluetooth/tle.data"
        # self.gps_file_path = "../bluetooth/gps.data"
        # self.tle_data = sgpb.read_tle_file(self.tle_file_path)

        file_path = "../sgp4/tle.txt"
        tle_data = sgpb.read_tle_file(file_path)
        
        self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]
        
        # observer = Observer(file_path=self.gps_file_path)
        observer = Observer(40.444, -79.953, 300)

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

        # Create the combo box
        self.combo_box = QComboBox()
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
        # self.combo_box.addItems([satellite.name for satellite in satellites])
        options = [sat.name for sat in self.satellites]
        self.combo_box.addItems(options)
        self.combo_box.setFixedWidth(390)
        self.combo_box.setFixedHeight(40)

        # Call method for selected satellite
        self.combo_box.currentIndexChanged.connect(lambda: self.sat_data(self.satellites, self.combo_box.currentIndex(), observer, local_time))

        # Create entry widgets
        self.e1 = QLineEdit()
        self.e2 = QLineEdit()
        self.e3 = QLineEdit()
        self.e4 = QLineEdit()
        self.e5 = QLineEdit()
        self.e6 = QLineEdit()

        # Create interactable icons
        label_image = QLabel(central_widget)
        label_image.setGeometry(10, 400, 64,64)
        pixmap = QPixmap('Assets/auto.png')
        pixmap = pixmap.scaled(64,64)
        label_image.setPixmap(pixmap)

        label_image_2 = QLabel(central_widget)
        label_image_2.setGeometry(100, 400, 64, 64)
        pixmap2 = QPixmap('Assets/manual.png')
        pixmap2 = pixmap2.scaled(64,64)
        label_image_2.setPixmap(pixmap2)

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

    # def keyPressEvent(self, event: QKeyEvent):
    #     if event.key() == Qt.Key.Key_F10:
    #         self.startBtServer()

    def sat_data(self, satellites, selected, observer, local_time):
        # Get data from the satellite object
        e1_data = satellites[selected].getAngleFrom(observer, local_time)
        
        e2_data = satellites[selected].nextOverhead(observer, local_time)
        e3_data = satellites[selected].overheadDuration(observer, local_time, next_overhead=e2_data)
        # e4_data = satellites[selected].getAngleFrom(observer, local_time)
        e4_data = satellites[selected].name

        e5_data = str(observer.lat) + " , " + str(observer.lon) + " , " + str(observer.alt)
        
        # String formatting for displaying results
        e1_data = "AZ: " + str(e1_data[0][0]) + " , " + "EL: " + str(e1_data[1][0])
        e2_data = e2_data.strftime("%Y-%m-%d %H:%M:%S")
        e3_data = str(e3_data)
        e4_data = str(e4_data)
        # e5_data = str(e5_data)
        
        # Pass satellite data into text boxes
        self.e1.setText(e1_data)
        self.e2.setText(e2_data)
        self.e3.setText(e3_data)
        self.e4.setText(e4_data)
        self.e5.setText(e5_data)

    # def startBtServer(self):
    #     process = subprocess.Popen(['python3', '../bluetooth/btserver.py'],
    #                               stdin=None,
    #                               stdout=None,
    #                               stderr=subprocess.PIPE)

    #     output, errors = process.communicate(input="")
    #     if output != None:
    #         print(f"{output.decode()}")
    
    #     if errors != None:
    #         print(f"{errors.decode()}")

    #     print("Bluetooth server returned to main loop")

            
    #     self.tle_data = sgpb.read_tle_file(self.tle_file_path)
    #     self.satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in self.tle_data]
    #     self.observer = Observer(file_path=self.gps_file_path)


def main():
    # satellites = Satellite("Sat1", "32", "40")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



if __name__ == '__main__':

    main()
