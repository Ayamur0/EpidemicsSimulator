import os
import sys
from src.epidemics_simulator.gui import UiNetworkEditor
from PyQt5 import QtWidgets

executable_directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(executable_directory)
app = QtWidgets.QApplication(sys.argv)
window = UiNetworkEditor()
app.exec_()
