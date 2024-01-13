from PyQt5 import QtWidgets
import sys
from gui import UiNetworkEditor
        

app = QtWidgets.QApplication(sys.argv)
window = UiNetworkEditor()
app.exec_()
