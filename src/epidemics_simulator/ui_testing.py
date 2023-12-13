from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
import sys
from gui import UiNetworkEditor
from storage import Network, NodeGroup


test_data = Network()
g1 = NodeGroup(test_data, "Group1", 53, 58, 0.54, 0.3, 14, 2, '#ff3411')
g2 = NodeGroup(test_data, "Group2", 87, 12, 0.62, 0.4, 12, 7,'#115577')
g3 = NodeGroup(test_data, "Group3", 69, 7, 0.78, 0.7, 15, 3,'#acde75')
g4 = NodeGroup(test_data, "Group4", 27, 3, 0.34, 1, 11, 5, '#ffffff')
g5 = NodeGroup(test_data, "Group5", 71, 24, 0.55, 0.4, 13, 4, '#f74532')



test_data.add_group(g1)
test_data.add_group(g2)
test_data.add_group(g3)
test_data.add_group(g4)
test_data.add_group(g5)

g1.add_external_connection(g2.id, 5, 3)

app = QtWidgets.QApplication(sys.argv)
window = UiNetworkEditor()
with open("qt\\NetworkEdit\\style_sheet.qss", mode="r", encoding="utf-8") as fp:
    stylesheet = fp.read()
app.setStyleSheet(stylesheet)
window.load_groups(test_data)
app.exec_()
