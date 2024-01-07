from functools import partial
import json
import os
import time

import requests
from PyQt5.QtCore import QThreadPool, QRunnable, QThread
from src.epidemics_simulator.gui.ui_network_groups import UiNetworkGroups
from src.epidemics_simulator.gui.ui_network_connections import UiNetworkConnections
from src.epidemics_simulator.gui.ui_group_display import UiGroupDisplay
from src.epidemics_simulator.gui.ui_disease_editor import UiDiseaseEditor
from src.epidemics_simulator.gui.ui_simulation import UiSimulation
from src.epidemics_simulator.gui.ui_stat_simulation import UiSimulationStats
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.gui.ui_startup_window import UiStartupWindow
from src.epidemics_simulator.gui.ui_stats_view import UiStatsView
from src.epidemics_simulator.storage import Network, Project
from PyQt5.QtCore import pyqtSignal
from src.epidemics_simulator.gui.templates import templates
from PyQt5 import QtWidgets, uic
from storage import Network

class NetworkRunnable(QThread):
    no_response_signal = pyqtSignal()
    finished = pyqtSignal(QThread)
    def __init__(self, project: Project):
        super().__init__()
        self.url = "http://127.0.0.1:8050/update-data"
        self.project = project

    def run(self):
        try:
            # Make the POST request
            response = requests.post(self.url, json=self.project.to_dict())

            # Check the response
            if response.status_code == 200:
                print("POST request successful")
            else:
                print(f"POST request failed with status code {response.status_code}")

        except requests.ConnectionError:
            # Emit a signal to handle the exception in the main thread
            self.no_response_signal.emit()
        except Exception as e:
            # Emit a signal to handle other exceptions in the main thread
            print(f"An error occurred: {e}")
        self.finished.emit(self)
class CheckConnection(QThread):
    connection_established = pyqtSignal()
    finished = pyqtSignal(QThread)
    def __init__(self, url):
        super().__init__()
        self.url = url
    def run(self):
        connected = False
        while not connected:
            try:
                response = requests.head(self.url, timeout=5)
                print(response.status_code)
                # Check if the response status code is in the 2xx range (success)
                if response.status_code // 100 == 2:
                    connected = True
            except requests.ConnectionError:
                print('Error Connecting')
                time.sleep(0.5)
        self.connection_established.emit()
        self.finished.emit(self)

class UiNetworkEditor(QtWidgets.QMainWindow):
    network_changed = pyqtSignal()
    disease_changed = pyqtSignal()
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        self.network_was_build = False
        self.is_project_loaded = False
        self.network_changed.connect(self.on_network_change)
        self.disease_changed.connect(self.on_disease_change)
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        with open('qt/NetworkEdit/themes.json', 'r') as fp:
            self.themes = json.load(fp)
        with open("qt\\NetworkEdit\\style_sheet.qss", mode="r", encoding="utf-8") as fp:
            self.stylesheet = fp.read()
        self.thread_pool = QThreadPool.globalInstance()
        self.change_theme('Dark')
        self.fill_theme(self.themes)
        self.groups = UiNetworkGroups(self)
        self.connections = UiNetworkConnections(self)
        self.display = UiGroupDisplay(self)
        self.disease = UiDiseaseEditor(self)
        self.simulation = UiSimulation(self)
        self.simulation_stats = UiSimulationStats(self)
        self.stats_view = UiStatsView(self)
        self.server_connected = False
        self.server_check_in_progress = False
        self.start_server_check()
        
        self.connect_menu_actions()
        self.tabWidget.currentChanged.connect(self.on_tab_change)
        
        self.launch_startup()
        #self.show()

    def start_server_check(self):
        if self.server_check_in_progress:
            return
        self.server_check_in_progress = True
        self.server_check = CheckConnection('http://127.0.0.1:8050')
        self.server_check.connection_established.connect(self.connection_established)
        self.server_check.finished.connect(self.thread_finished)
        self.server_check.start()
        #self.thread_pool.start(self.server_check)
        
    def connection_established(self):
        self.server_connected = True
        self.server_check_in_progress = False
        self.push_to_dash()
        self.show_webviews()

    def launch_startup(self):
        # Launch initial startup dialog
        startup = UiStartupWindow(self)
        startup.show()
        #startup.close_startup() # TODO load network or create network with the Startup
        
        
    def connect_menu_actions(self):
        self.actionNew.triggered.connect(lambda: self.new_network(self))
        self.actionSave.triggered.connect(lambda: self.save_network())
        self.actionOpen.triggered.connect(lambda: self.open_network(self))
        self.populate_template_action()
        
    def populate_template_action(self):
        for i in range(0, len(templates)):
            template = templates[i]
            action = UiWidgetCreator.create_qaction(template.name, 'template_menu_item', self)
            action.triggered.connect(partial(self.new_network, self, i))
            self.menuNew_from_template.addAction(action)

        
    def load_network(self, network: Network):
        self.current_network = network
        self.is_project_loaded = True
        self.network_changed.emit()
        self.load_groups(network)
        self.disease.load_properties(network.diseases)
        self.simulation.load_simulation()
        self.simulation_stats.load_info()
        self.stats_view.load_stats()
        
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
        self.stats_view.unload()
        
        
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
        
        
    def new_network(self, parent, template_id=None):
        
        file_name = UiWidgetCreator.create_file(parent)
        if not file_name:
            return False
        self.unload_all()
        if template_id:
            network = templates[template_id]
        else:
            network = Network()
        network.name = os.path.basename(file_name[0:-5])
        self.project = Project()
        self.project.network = network
        self.project.file_location = file_name
        self.load_network(network)
        self.project.save_to_file()
        return True
        
    def save_network(self):
        self.project.save_to_file()
        
    def open_network(self, parent):
        file_name = UiWidgetCreator.open_file(parent)
        if not file_name:
            return False
        self.unload_all()
        self.project = Project.load_from_file(file_name)
        self.project.file_location = file_name
        self.load_network(self.project.network)
        return True
    
    def push_to_dash(self):
        if not self.is_project_loaded:
            return
        self.server_push = NetworkRunnable(self.project)
        self.server_push.no_response_signal.connect(self.start_server_check)
        self.server_push.finished.connect(self.thread_finished)
        self.server_push.start()
        #self.thread_pool.start(self.server_push)
            
    def on_tab_change(self, index):
        self.groups.unload()
        self.connections.unload()
        self.disease.unload()
        #self.unload_all()
        if index == 0:
            self.load_groups(self.current_network)
        elif index == 1:
            self.disease.load_properties(self.current_network.diseases)
        if index == 3:
            return
        self.simulation_stats.stop_simulation()
        #if index == 2: # Tab index of simulation
        #    self.push_to_dash()
        #elif index == 3:
        #    self.simulation.load_simulation()
        #elif index == 4:
        #    self.simulation_stats.load_info()
        
    def on_network_change(self):
        self.network_was_build = False
        self.on_disease_change()
        #self.push_to_dash()
        #self.simulation_stats.reset_simulation()
        
    def on_disease_change(self):
        # TODO if nothing changes remove this function and only call on_network_change
        # Diseases should not be displayed on the view?
        #self.on_network_change()
        self.push_to_dash()
        self.simulation_stats.reset_simulation()
        
    def show_webviews(self):
        self.simulation.load_simulation()
        self.stats_view.load_stats()
        
    def thread_finished(self, worker: QThread):
        worker.quit()
        worker.deleteLater()