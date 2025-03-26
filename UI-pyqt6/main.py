from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget)
from PyQt6.QtCore import QSize, Qt

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
        file_path = "../bluetooth/tle.data"
        tle_data = sgpb.read_tle_file(file_path)
        satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]
        
        observer = Observer(file_path="../bluetooth/gps.data")
        #observer = Observer(40.44, -79.95, 300)

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
        options = [sat.name for sat in satellites]
        self.combo_box.addItems(options)
        self.combo_box.setFixedWidth(390)
        self.combo_box.setFixedHeight(40)

        # Call method for selected satellite
        self.combo_box.currentIndexChanged.connect(lambda: self.sat_data(satellites, self.combo_box.currentIndex(), observer, local_time))

        # Create entry widgets
        self.e1 = QLineEdit()
        self.e2 = QLineEdit()
        self.e3 = QLineEdit()
        self.e4 = QLineEdit()
        self.e5 = QLineEdit()

        self.label1 = QLabel("Names:")
        self.label2 = QLabel("Values:")
        self.label3 = QLabel("Items")
        self.label4 = QLabel("Widhts")
        self.label5 = QLabel("Overhead")

        edit_lines = [self.e1, self.e2, self.e3, self.e4, self.e5]

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

    def sat_data(self, satellites, selected, observer, local_time):
        # Get data from the satellite object
        e1_data = satellites[selected].name
        e2_data = satellites[selected].getAngleFrom(observer, local_time)[1][0]
        e2_data = str(e2_data)
        e3_data = satellites[selected].tle2
        e4_data = satellites[selected].nextOverhead(observer, local_time)
        e5_data = satellites[selected].isOverhead(observer, local_time)
        e5_data = str(e5_data)

        e4_data = e4_data.strftime("%Y-%m-%d %H:%M:%S")

        # Pass satellite data into text boxes
        self.e1.setText(e1_data)
        self.e2.setText(e2_data)
        self.e3.setText(e3_data)
        self.e4.setText(e4_data)
        self.e5.setText(e5_data)


    def startBtServer():
        process = subprocess.Popen(['python3', '../bluetooth/btserver.py'],
                                  stdin=None,
                                  stdout=None,
                                  stderr=subprocess.PIPE)

        output, errors = process.communicate(input="")
        if output != None:
            print(f"{output.decode()}")
    
        if errors != None:
            print(f"{errors.decode()}")

            
        tle_data = sgpb.read_tle_file(file_path)
        satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]
        observer = Observer(file_path="../bluetooth/gps.data")


def main():
    # satellites = Satellite("Sat1", "32", "40")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



if __name__ == '__main__':

    main()
