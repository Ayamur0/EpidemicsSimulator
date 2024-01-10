from PyQt5 import QtWidgets
from src.epidemics_simulator.gui.network_edit.ui_groups_edit import UiGroupEdit
from src.epidemics_simulator.gui.network_edit.ui_connections_edit import UiConnectionEdit
from src.epidemics_simulator.gui.network_edit.ui_display_groups import UiDisplayGroup
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Project
class UiNetworkEditTab:
    def __init__(self, main_window: QtWidgets.QMainWindow):
        self.main_window = main_window
        self.connection_edit = UiConnectionEdit(self.main_window)
        self.group_edit = UiGroupEdit(self.main_window, self.connection_edit)
        self.group_display = UiDisplayGroup(self.main_window)
        self.tab_widget = self.main_window.network_edit
        
        
    def init_ui(self, network: Network):
        self.unload()
        
        self.group_edit.init_ui(network)
        self.connection_edit.init_ui(network)
        self.group_display.init_ui(network)
    
    def unload(self):
        self.connection_edit.unload()
        self.group_edit.unload()
        self.group_display.unload()