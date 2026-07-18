import os
import sys
from PySide6.QtWidgets import QApplication

from gui.window import MainWindow

if __name__ == "__main__":

    os.environ["LC_NUMERIC"] = "C"
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())