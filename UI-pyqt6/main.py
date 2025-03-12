import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QComboBox,
                            QLineEdit, QLabel, QGridLayout, QWidget)
from PyQt6.QtCore import QSize


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and size constraints
        self.setWindowTitle("PyQt6 Application for On-Device UI")
        # self.resize(800, 480)
        self.setFixedSize(800, 480)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)

        # Create the combo box
        options = ['Option 1', 'Option 2', 'Option 3']
        combo_box = QComboBox()
        combo_box.addItems(options)
        combo_box.setFixedWidth(390)  # Approximate equivalent to width=50 in tkinter
        combo_box.setFixedHeight(40)
        combo_box.setStyleSheet("background-color: white")

        # Create entry widgets (QLineEdit in PyQt)
        e1 = QLineEdit("Dummy Text 1")
        e1.setStyleSheet("background-color: lightgray;")
        e1.setFixedWidth(390)
        e1.setFixedHeight(40)

        e2 = QLineEdit("Dummy Text 2")
        e2.setStyleSheet("background-color: lightgray;")
        e2.setFixedWidth(390)
        e2.setFixedHeight(40)

        e3 = QLineEdit("Dummy Text 3")
        e3.setStyleSheet("background-color: lightgray;")
        e3.setFixedWidth(390)
        e3.setFixedHeight(40)

        # Line edits and combo box
        grid.addWidget(combo_box, 2, 0)
        grid.addWidget(e1, 1, 1)
        grid.addWidget(e2, 2, 1)
        grid.addWidget(e3, 3, 1)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
