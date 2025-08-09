import sys
from LoginApp import Authorization
from PyQt6 import QtWidgets

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Authorization()
    window.show()
    sys.exit(app.exec())