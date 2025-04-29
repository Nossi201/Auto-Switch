# app.py

"""Main file"""
import  sys
from PySide6.QtWidgets import QApplication

from src.views.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()