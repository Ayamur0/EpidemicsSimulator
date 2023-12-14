#from gui import UiNetworkGroups, UiNetworkConnections
from .ui_network_groups import UiNetworkGroups
from .ui_network_connections import UiNetworkConnections
from .ui_group_display import UiGroupDisplay

import random
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QRegExp, QTimer, Qt
from PyQt5.QtGui import QRegExpValidator, QColor
import sys
from storage import Network, NodeGroup
from functools import partial


class UiNetworkEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        self.groups = UiNetworkGroups(self)
        self.connections = UiNetworkConnections(self)
        self.display = UiGroupDisplay(self)
        self.show()
        
    def load_groups(self, network: Network):
        self.current_network = network
        all_groups = network.groups
        for group in all_groups:
            self.groups.add_group(group, network)
        self.groups.new_group_button_input(network)
        
    def unload_all_segments(self):
        self.connections.unload()
        self.display.unload()
        self.groups.unload()
        
        
    def unload_items_from_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def deselect_other_buttons(self, sender_id, button_dict):
        for button in button_dict:
            btn_object = button_dict[button]
            if button == sender_id: # So it is not possible to deleselct the same button
                btn_object.setChecked(True)
                continue
            if not btn_object.isChecked():
                continue
            btn_object.setChecked(False)
        
