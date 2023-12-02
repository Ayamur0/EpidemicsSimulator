from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
import sys
from gui import UiNetworkEditor
from storage import Network, NodeGroup


test_data = Network()
g1 = NodeGroup(test_data, "Group1", 53, 58, 0.54, 14, 2)
g2 = NodeGroup(test_data, "Group2", 87, 12, 0.62, 12, 7)
g1.add_external_connection(g2.id, 5, 7)


test_data.add_group(g1)
test_data.add_group(g2)

app = QtWidgets.QApplication(sys.argv)
window = UiNetworkEditor()
window.load_groups(test_data)
app.exec_()
