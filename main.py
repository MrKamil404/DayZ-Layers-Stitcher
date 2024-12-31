import sys
from PyQt5 import QtWidgets
from ui import ImageStitcher

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = ImageStitcher()
    ex.show()
    sys.exit(app.exec_())