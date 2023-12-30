from functools import partial
import json
from src.epidemics_simulator.gui.ui_network_groups import UiNetworkGroups
from src.epidemics_simulator.gui.ui_network_connections import UiNetworkConnections
from src.epidemics_simulator.gui.ui_group_display import UiGroupDisplay
from src.epidemics_simulator.gui.ui_illness_editor import UiIllnessEditor
from src.epidemics_simulator.gui.ui_simulation import UiSimulation
from src.epidemics_simulator.gui.ui_stat_simulation import UiSimulationStats
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from PyQt5 import QtWidgets, uic
from storage import Network


class UiNetworkEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        with open('qt/NetworkEdit/themes.json', 'r') as fp:
            self.themes = json.load(fp)
        with open("qt\\NetworkEdit\\style_sheet.qss", mode="r", encoding="utf-8") as fp:
            self.stylesheet = fp.read()
        self.change_theme('Dark')
        self.fill_theme(self.themes)
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
        
    def fill_theme(self, theme: dict):
        menu = self.menuThemes
        for key in theme.keys():
            action = UiWidgetCreator.create_qaction(key, 'theme_action', self)
            action.triggered.connect(partial(self.change_theme, key))
            menu.addAction(action)
            
    def change_theme(self, new_Theme):
        new_style = self.stylesheet
        for key, value in self.themes[new_Theme].items():
            new_style = new_style.replace(key, value)
        self.setStyleSheet(new_style)