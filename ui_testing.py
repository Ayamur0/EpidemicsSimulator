import os
import sys
from src.epidemics_simulator.gui import UiNetworkEditor
from PyQt5 import QtWidgets

# import atexit
current_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_directory)


app = QtWidgets.QApplication(sys.argv)
window = UiNetworkEditor()
app.exec_()
# atexit.register(window.website_handler.kill.emit)
