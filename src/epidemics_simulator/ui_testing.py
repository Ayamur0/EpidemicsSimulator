import os
from PyQt5 import QtWidgets
import sys
from gui import UiNetworkEditor
# import atexit
current_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_directory)
os.chdir('../..')
app = QtWidgets.QApplication(sys.argv)
window = UiNetworkEditor()
app.exec_()
# atexit.register(window.website_handler.kill.emit)
