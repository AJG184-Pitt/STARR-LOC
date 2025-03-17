from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget)
from PyQt6.QtCore import QSize

import sys
sys.path.append('../sgp4')

import sgp4_basic as sgpb
from observer import Observer
from satellite import Satellite
import pytz, datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Information gathering
        file_path = "../sgp4/tle.txt"
        tle_data = sgpb.read_tle_file(file_path)
        satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]
        
        observer = Observer(40.44, -79.95, 300)

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
                background-position: center;
                background-size: contain;
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
        selected = self.combo_box.currentIndex()
        # local_time = datetime.datetime.now()
        self.combo_box.activated.connect(lambda: self.sat_data(satellites, selected, observer, local_time))

        # Create entry widgets
        self.e1 = QLineEdit()
        self.e2 = QLineEdit()
        self.e3 = QLineEdit()

        edit_lines = [self.e1, self.e2, self.e3]

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

        # Line edits and combo box
        grid.addWidget(self.combo_box, 2, 0)
        grid.addWidget(self.e1, 1, 1)
        grid.addWidget(self.e2, 2, 1)
        grid.addWidget(self.e3, 3, 1)

        # self.e1.setText("Temp")
        # self.e2.setText("Temp")
        # self.e3.setText("Temp")


        # self.combo_box.currentIndexChanged.connect(self.update_tle_data(satellites))

    def update_tle_data(self, satellites):
        tle1, tle2 = satellites.tle1, satellites.tle2
        self.e1.setText(tle1)
        self.e2.setText(tle2)

    def sat_data(self, satellites, selected, observer, local_time):
        e1_data = satellites[selected].name
        e2_data = satellites[selected].getAngleFrom(observer, local_time)[1][0]
        e2_data = str(e2_data)
        e3_data = satellites[selected].tle2

        self.e1.setText(e1_data)
        self.e2.setText(e2_data)
        self.e3.setText(e3_data)

def main():
    # satellites = Satellite("Sat1", "32", "40")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
