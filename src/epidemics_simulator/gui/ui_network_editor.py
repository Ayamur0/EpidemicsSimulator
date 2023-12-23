from src.epidemics_simulator.gui.ui_network_groups import UiNetworkGroups
from src.epidemics_simulator.gui.ui_network_connections import UiNetworkConnections
from src.epidemics_simulator.gui.ui_group_display import UiGroupDisplay
from src.epidemics_simulator.gui.ui_illness_editor import UiIllnessEditor
from src.epidemics_simulator.gui.ui_simulation import UiSimulation
from src.epidemics_simulator.gui.ui_stat_simulation import UiSimulationStats
from PyQt5 import QtWidgets, uic
from storage import Network


class UiNetworkEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        self.groups = UiNetworkGroups(self)
        self.connections = UiNetworkConnections(self)
        self.display = UiGroupDisplay(self)
        self.illness = UiIllnessEditor(self)
        self.simulation = UiSimulation(self)
        self.simulation_stats = UiSimulationStats(self)
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
            
    def get_selected_button(self, button_dict):
        for button in button_dict:
            btn_object = button_dict[button]
            if not btn_object.isChecked():
                continue
            return btn_object
        
