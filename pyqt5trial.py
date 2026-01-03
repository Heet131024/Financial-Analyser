import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow , QLabel,
QWidget , QVBoxLayout , QHBoxLayout , QGridLayout , QPushButton , QCheckBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My cool first GUI")
        self.setGeometry(700, 300, 500, 500)
        self.setWindowIcon(QIcon("HEET.jpeg"))
        self.button = QPushButton("Click Me", self)
        self.label = QLabel("Hello", self)
        self.checkbox = QCheckBox("Do you like food? " , self)
        self.initUI()
        
    
    def on_click(self):
        print("Button clicked!")
        self.button.setText("Clicked")
        self.button.setDisabled(True)
        self.label.setText("Goodbye!")

    def initUI(self):
            self.button.setGeometry(150 , 200 , 200 , 100)
            self.button.setStyleSheet("font-size: 30px;")
            self.button.clicked.connect(self.on_click)
            
            self.label.setGeometry(150 , 300 , 200 , 100)
            self.label.setStyleSheet("font-size: 30px; color: green;")

            self.checkbox.setGeometry(0 , 0, 500 , 100)
            self.checkbox.setStyleSheet("font-size: 30px; color: blue; font-family: Arial;")
            self.checkbox.setChecked(False)
            self.checkbox.stateChanged.connect(self.checkbox_changed)


    def checkbox_changed(self , state):
        if state == Qt.Unchecked:
            print("You don't like food!")
        else:
            print("You Like food!")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
    

