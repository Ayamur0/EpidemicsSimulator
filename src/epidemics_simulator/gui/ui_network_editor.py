from functools import partial
import json
import os
import signal
import subprocess
import sys
import time

import requests
from PyQt5.QtCore import QThreadPool, QRunnable, QThread, Qt, QSize
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.gui.ui_startup import UiStartup
from src.epidemics_simulator.storage import Network, Project
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QPixmap
from src.epidemics_simulator.gui.templates import templates
from PyQt5 import QtWidgets, uic
from storage import Network
from src.epidemics_simulator.gui.network_edit.ui_network_edit_tab import UiNetworkEditTab
from src.epidemics_simulator.gui.disease_edit.ui_disease_edit_tab import UiDiseaseEditTab
from src.epidemics_simulator.gui.simulation.ui_simulation import UiSimulationTab
from src.epidemics_simulator.gui.statistics.ui_statistics import UiStatisticTab
from src.epidemics_simulator.gui.text_simulation.ui_text_simulation import UiTextSimulationTab
from src.epidemics_simulator.storage.sim_stats import SimStats
from src.epidemics_simulator.gui.listen_server import WebServer
import psutil
class PushData(QThread):
    no_response_signal = pyqtSignal()
    finished = pyqtSignal(QThread)
    def __init__(self, project: Project, base_url: str):
        super().__init__()
        self.url = f'{base_url}/update-data'
        self.project = project

    def run(self):
        try:
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
            except requests.ConnectionError or requests.exceptions.ReadTimeout:
                print('Error Connecting')
                time.sleep(1)
        self.connection_established.emit()
        self.finished.emit(self)


class UiNetworkEditor(QtWidgets.QMainWindow):
    network_changed = pyqtSignal() # TODO connect emit
    disease_changed = pyqtSignal() # TODO connect emit
    icon_themes = {'Dark': QColor(Qt.white), 'Light': QColor(Qt.black)}
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        self.server_process = None
        self.server_url = 'http://localhost:8050'
        self.changed_disease = False
        self.generated_network = False
        self.is_server_connected = False
        self.checking_connection = False
        self.is_project_loaded = False
        self.server_check_in_progress = False
        self.unsaved_changes = False
        self.is_asking_for_restart = False
        self.server_push = None
        self.network_changed.connect(self.on_network_change)
        self.disease_changed.connect(self.on_disease_change)
        self.listen_server = WebServer()
        self.listen_server.signal_update_received.connect(self.stats_update)
        self.listen_server.start_server()
        self.init_icons()
        
        self.server_process  = self.start_server()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        with open('qt/NetworkEdit/themes.json', 'r') as fp:
            self.themes = json.load(fp)
        with open("qt\\NetworkEdit\\style_sheet.qss", mode="r", encoding="utf-8") as fp:
            self.stylesheet = fp.read()
        self.fill_theme(self.themes)

        self.connect_menu_actions()
        self.tabWidget.currentChanged.connect(self.on_tab_change)
        
        self.startup = UiStartup(self)
        self.network_edit_tab = UiNetworkEditTab(self)
        self.disease_edit_tab = UiDiseaseEditTab(self)
        self.simulation_tab = UiSimulationTab(self)
        self.text_simulation_tab = UiTextSimulationTab(self)
        self.statistics_tab = UiStatisticTab(self)
        self.change_theme('Dark')
        self.startup.launch_startup()
        
    def init_icons(self):
        self.add_icon = QIcon('assets/add.png')
        self.save_icon = QIcon('assets/save.png')
        self.duplicate_icon = QIcon('assets/duplicate.png')
        self.remove_icon = QIcon('assets/delete.png')
        
        self.start_icon = QIcon('assets/play.png')
        self.stop_icon = QIcon('assets/pause.png')
        self.forward_icon = QIcon('assets/forward.png')
        self.rewind_icon = QIcon('assets/rewind.png')
        self.restart_icon = QIcon('assets/restart.png')

    def launch(self):
        self.network = self.project.network
        self.unload()
        self.init_uis()

        
    def init_uis(self):
        self.is_project_loaded = True
        self.network_edit_tab.init_ui(self.network)
        self.disease_edit_tab.init_ui(self.network)
        self.simulation_tab.init_ui()
        self.text_simulation_tab.init_ui(self.network)
        self.statistics_tab.init_ui()
        
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
        
    def fill_theme(self, theme: dict):
        menu = self.menuThemes
        for key in theme.keys():
            action = UiWidgetCreator.create_qaction(key, 'theme_action', self)
            action.triggered.connect(partial(self.change_theme, key))
            menu.addAction(action)
            
    def change_theme(self, new_theme):
        new_style = self.stylesheet
        for key, value in self.themes[new_theme].items():
            new_style = new_style.replace(key, value)
        self.setStyleSheet(new_style)
        if new_theme == 'Dark':
            old_theme = 'Light'
        else:
            old_theme = 'Dark'
        self.add_icon = self.button_change(self.add_icon, old_theme, new_theme)
        self.duplicate_icon = self.button_change(self.duplicate_icon, old_theme, new_theme)
        self.remove_icon = self.button_change(self.remove_icon, old_theme, new_theme)
        self.save_icon = self.button_change(self.save_icon, old_theme, new_theme)
        
        self.start_icon = self.button_change(self.start_icon, old_theme, new_theme)
        self.stop_icon = self.button_change(self.stop_icon, old_theme, new_theme)
        self.forward_icon = self.button_change(self.forward_icon, old_theme, new_theme)
        self.rewind_icon = self.button_change(self.rewind_icon, old_theme, new_theme)
        self.restart_icon = self.button_change(self.restart_icon, old_theme, new_theme)
                
        self.change_all_button_icons(UiNetworkEditor.icon_themes[old_theme], UiNetworkEditor.icon_themes[new_theme])
        
    def button_change(self, icon: QIcon, old_theme: str, new_theme: str) -> QIcon:
        return QIcon(self.change_icon_color(icon, UiNetworkEditor.icon_themes[old_theme], UiNetworkEditor.icon_themes[new_theme]))
        
    def new_network(self, parent, template_id=None):
        if self.is_project_loaded and self.unsaved_changes:
            if self.ask_to_save():
                return
        file_name = UiWidgetCreator.create_file(parent)
        if not file_name:
            return False
        if template_id:
            network = templates[template_id]
        else:
            network = Network()
        network.name = os.path.basename(file_name[0:-5])
        self.project = Project()
        self.project.network = network
        self.project.file_location = file_name
        self.project.save_to_file()
        
        self.launch()
        return True
        
    def save_network(self):
        self.unsaved_changes = False
        self.project.save_to_file()
        
    def open_network(self, parent):
        if self.is_project_loaded and self.unsaved_changes:
            if self.ask_to_save():
                return
        file_name = UiWidgetCreator.open_file(parent)
        if not file_name:
            return False
        self.project = Project.load_from_file(file_name)
        self.project.file_location = file_name
        self.launch()
        return True
    
    def unload(self):
        self.generated_network = False
        self.changed_disease = False
        self.is_project_loaded = False
        self.unsaved_changes = False
        self.network_edit_tab.unload()
        self.disease_edit_tab.unload()
        self.simulation_tab.unload()
        self.text_simulation_tab.unload()
        self.statistics_tab.unload()

    def on_tab_change(self, index):
        for i in range(self.tabWidget.count()):
            if i != index:
                self.tabWidget.widget(i).hide()
            else:
                self.tabWidget.widget(i).show()
        if index != 3:
            self.text_simulation_tab.stop_simulation()
        if index == 0:
            pass
        elif index == 1:
            pass
        elif index == 2:
            if len(self.network.groups) == 0:
                return
            if not self.generated_network:
                self.simulation_tab.ask_for_regeneration()
        elif index == 3:
            if len(self.network.groups) == 0:
                return
            if not self.generated_network:
                self.text_simulation_tab.ask_for_regeneration()
            elif self.changed_disease:
                self.text_simulation_tab.ask_for_reset()
        elif index == 4:
            pass
            #self.statistics_tab.show_webview()
    
    def hide_webviews(self):
        self.network_edit_tab.group_display.hide_webview()
        self.simulation_tab.hide_webview()
        self.statistics_tab.hide_webview()
        
    def show_webviews(self):
        self.network_edit_tab.group_display.show_webview()
        self.simulation_tab.show_webview()
        self.statistics_tab.show_webview()
    
    def on_network_change(self):
        ## TODO do i want to reset the text simulation?
        self.generated_network = False
        self.unsaved_changes = True
        #self.push_to_dash()
        print('Network Changed')
        
    def on_disease_change(self):
        self.changed_disease = True
        self.unsaved_changes = True
        #self.push_to_dash()
        print('Disease Changed')
        
    def check_server_connection(self, is_initial_test=False):
        if self.server_check_in_progress:
            return
        if not is_initial_test:
            self.ask_if_server_should_restart() # Could inflict bugs
        self.is_server_connected = False
        self.server_check_in_progress = True
        self.server_check = CheckConnection(self.server_url)
        self.server_check.connection_established.connect(self.connection_established)
        self.server_check.finished.connect(self.server_check_finished)
        self.server_check.start()
        
    def connection_established(self):
        
        self.is_server_connected = True
        self.server_check_in_progress = False
        self.push_to_dash()
        self.show_webviews()
        
    
        
    def push_to_dash(self):
        if not self.is_project_loaded:
            return
        self.server_push = PushData(self.project, self.server_url)
        self.server_push.no_response_signal.connect(self.check_server_connection)
        self.server_push.finished.connect(self.push_finished)
        self.server_push.start()

    def server_check_finished(self):
        if not self.server_check:
            return
        self.server_check.wait()
        self.server_check.quit()
        self.server_check.deleteLater()
        self.server_check = None
        
    def push_finished(self):
        # self.show_webviews()
        if not self.server_push:
            return
        self.server_push.wait()
        self.server_push.quit()
        self.server_push.deleteLater()
        self.server_push = None
        
    def ask_if_server_should_restart(self):
        if self.is_asking_for_restart:
            return
        self.is_asking_for_restart = True
        
        message = UiWidgetCreator.show_message('Connection to server lost. Do you want to restart the server?', 'Connection lost')
        result = message.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return
        self.terminate_server()
        self.server_process = self.start_server()
        self.is_asking_for_restart = False
        
    def start_server(self):
        if self.is_server_connected:
            return
        try:
                response = requests.head(self.server_url, timeout=1)
                # Check if the response status code is in the 2xx range (success)
                if response.status_code // 100 == 2:
                    self.is_server_connected = True
                    return
        except requests.ConnectionError or requests.exceptions.ReadTimeout:
            pass
        try:
            activate_script = os.path.join('venv', 'Scripts' if sys.platform == 'win32' else 'bin', 'activate')
            activate_command = [activate_script, '&&', 'python', 'src\epidemics_simulator\launch_webview.py']

            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0

            process = subprocess.Popen(activate_command, stdout=subprocess.PIPE, shell=True, executable=os.environ.get('SHELL'), creationflags=creation_flags)
            self.check_server_connection(is_initial_test=True)
            return process
        except Exception as e:
            print(f'Error starting server: {e}')
            return None
      
    def kill(self, proc_pid):
        # Source: https://stackoverflow.com/a/25134985
        try:
            process = psutil.Process(proc_pid)#
        except psutil.NoSuchProcess:
            return    
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
            
    def terminate_server(self):
        if self.server_process:
            self.kill(self.server_process.pid)
            
    def closeEvent(self, event):
        if self.unsaved_changes:
            if self.ask_to_save():
                event.ignore()
                return
        self.terminate_server()
        self.listen_server.stop()
        self.listen_server.deleteLater()
        event.accept()
        
    def ask_to_save(self):
        answer = UiWidgetCreator.save_popup('Do you want to save your changes?')
        if answer == QtWidgets.QMessageBox.Save:
            self.save_network()
            return False
        elif answer == QtWidgets.QMessageBox.No:
            return False
        elif answer == QtWidgets.QMessageBox.Cancel:
            return True
        
    def change_icon_color(self, icon: QIcon, original_color: QColor, new_color: QColor):
        pixel_map = icon.pixmap(QSize(512, 152))
        image = pixel_map.toImage()
        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixelColor(x, y) == original_color:
                    image.setPixelColor(x, y, new_color)
        return QPixmap.fromImage(image)
    
    def change_all_button_icons(self, old_color: QColor, new_color: QColor):
        for button in self.findChildren(QtWidgets.QPushButton):
            button_icon = button.icon()
            if button_icon.isNull():
                continue
            new_icon = QIcon(self.change_icon_color(button_icon, old_color, new_color))
            button.setIcon(new_icon)
            
    def stats_update(self, data):
        if 'stats' not in data.keys() or 'filename' not in data.keys():
            return
        self.project.stats[data['filename']] = SimStats.from_dict(data["stats"])
        self.unsaved_changes = True
        # self.statistics_tab.show_webview()
