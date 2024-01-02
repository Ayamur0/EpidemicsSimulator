from functools import partial
import json
import os
from src.epidemics_simulator.visualization.dash_server import DashServer
from src.epidemics_simulator.gui.ui_network_groups import UiNetworkGroups
from src.epidemics_simulator.gui.ui_network_connections import UiNetworkConnections
from src.epidemics_simulator.gui.ui_group_display import UiGroupDisplay
from src.epidemics_simulator.gui.ui_disease_editor import UiDiseaseEditor
from src.epidemics_simulator.gui.ui_simulation import UiSimulation
from src.epidemics_simulator.gui.ui_stat_simulation import UiSimulationStats
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.gui.ui_startup_window import UiStartupWindow
from src.epidemics_simulator.storage import Network, Project
from src.epidemics_simulator.gui.templates import templates
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
        self.disease = UiDiseaseEditor(self)
        self.simulation = UiSimulation(self)
        self.simulation_stats = UiSimulationStats(self)
        
        self.connect_menu_actions()
        
        self.launch_startup()
        #self.show()
        
    def launch_startup(self):
        # Launch initial startup dialog
        startup = UiStartupWindow(self)
        startup.show()
        #startup.close_startup() # TODO load network or create network with the Startup
        
        
    def connect_menu_actions(self):
        self.actionNew.triggered.connect(lambda: self.new_network(self))
        self.actionSave.triggered.connect(lambda: self.save_network(self))
        self.actionOpen.triggered.connect(lambda: self.open_network(self))
        self.populate_template_action()
        
    def populate_template_action(self):
        for i in range(0, len(templates)):
            template = templates[i]
            action = UiWidgetCreator.create_qaction(template.name, 'template_menu_item', self)
            action.triggered.connect(partial(self.new_network_from_template, i))
            self.menuNew_from_template.addAction(action)

        
    def load_network(self, network: Network):
        self.current_network = network
        self.load_groups(network)
        self.disease.load_properties(network.diseases)
        self.simulation_stats.load_info()
        
    def load_groups(self, network: Network):
        all_groups = network.groups
        for group in all_groups:
            self.groups.add_group(group, network)
        self.groups.new_group_button_input(network)
        
    def unload_all_segments(self):
        self.connections.unload()
        self.display.unload()
        self.groups.unload()
        
    def unload_all(self):
        self.unload_all_segments()
        self.disease.unload()
        self.simulation.unload()
        self.simulation_stats.unload()
        
        
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
        
        
    def new_network(self, parent):
        file_name = UiWidgetCreator.create_file(parent)
        if not file_name:
            return False
        self.unload_all()
        network = Network()
        network.name = os.path.basename(file_name)
        self.file_path = file_name
        self.load_network(network)
        print(file_name)
        return True
        
    def new_network_from_template(self, template_id, parent):
        file_name = UiWidgetCreator.create_file(parent)
        if not file_name:
            return False
        self.unload_all()
        network = templates[template_id]
        network.name = os.path.basename(file_name)
        self.file_path = file_name
        self.load_network(network)
        print(file_name)
        return True
    def save_network(self):
        # TODO save to the location
        pass
    def open_network(self, parent):
        file_name = UiWidgetCreator.open_file(parent)
        if not file_name:
            return False
        self.unload_all()
        network = Network() #TODO load network from file
        self.file_path = file_name
        self.load_network(network)
        print(file_name)
        return True