from functools import partial
import json
import os
import signal
import subprocess
import sys
import time

import requests
from PyQt5.QtCore import QThreadPool, QRunnable, QThread, Qt, QSize, QDir
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
#from src.epidemics_simulator.gui.listen_server import WebServer
import psutil
class PushData(QThread):
    no_response_signal = pyqtSignal()
    finished = pyqtSignal(QThread)
    def __init__(self, data: dict, base_url: str, sub_url: str = 'update-data'):
        super().__init__()
        self.url = f'{base_url}/{sub_url}'
        self.data = data

    def run(self):
        try: 
            response = requests.post(self.url, json=self.data)

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
class SaveStats(QThread):
    finished = pyqtSignal()
    def __init__(self, path, filename, stats):
        super().__init__()
        self.path = path
        self.filename = filename
        self.stats = stats
    def run(self):
        self.stats.to_csv(self.path, self.filename)
        #filename = self.data['filename']
        #stats = SimStats.from_dict(self.data["stats"])
        self.finished.emit()
        return
class UiNetworkEditor(QtWidgets.QMainWindow):
    network_changed = pyqtSignal() # TODO connect emit
    disease_changed = pyqtSignal() # TODO connect emit
    # icon_themes = {'Dark': QColor(Qt.white), 'Light': QColor(Qt.black)}
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        QDir.addSearchPath('assets', 'assets/')
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
        #self.listen_server = WebServer()
        #self.listen_server.signal_update_received.connect(self.stats_update)
        #self.listen_server.start_server()
        self.init_icons()
        
        self.server_process  = self.start_server()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        #with open('qt/NetworkEdit/themes.json', 'r') as fp:
        #    self.themes = json.load(fp)
        with open("qt\\NetworkEdit\\style_sheet.qss", mode="r", encoding="utf-8") as fp:
            self.stylesheet = fp.read()
        # self.fill_theme(self.themes)
        self.setStyleSheet(self.stylesheet)
        label = QtWidgets.QLabel('change_font', self)
        label.hide()
        font = label.font()
        font.setPointSize(12)  # Change the font size as needed
        QtWidgets.QApplication.setFont(font)
        label.deleteLater()
        self.connect_menu_actions()
        self.tabWidget.currentChanged.connect(self.on_tab_change)
        
        self.startup = UiStartup(self)
        self.network_edit_tab = UiNetworkEditTab(self)
        self.disease_edit_tab = UiDiseaseEditTab(self)
        self.simulation_tab = UiSimulationTab(self)
        self.text_simulation_tab = UiTextSimulationTab(self)
        self.statistics_tab = UiStatisticTab(self)
        #self.change_theme('Dark')
        self.startup.launch_startup()
        self.setWindowTitle('Network tool')
        
    def init_icons(self):
        self.add_icon = QIcon('assets/add.png')
        self.save_icon = QIcon('assets/save.png')
        self.duplicate_icon = QIcon('assets/duplicate.png')
        self.remove_icon = QIcon('assets/delete.png')
        self.edit_icon = QIcon('assets/edit.png')
        
        self.active_icon = QIcon('assets/selected.png')
        self.inactive_icon = QIcon('assets/unselect.png')
        
        self.start_icon = QIcon('assets/play.png')
        self.stop_icon = QIcon('assets/pause.png')
        #self.forward_icon = QIcon('assets/forward.png')
        #self.rewind_icon = QIcon('assets/rewind.png')
        #self.restart_icon = QIcon('assets/restart.png')
        
        

    def launch(self):
        self.network = self.project.network
        self.unload()
        self.init_uis()
        self.tabWidget.setCurrentIndex(0)

        
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

    def new_network(self, parent, template_id=None):
        self.text_simulation_tab.stop_simulation()
        if self.is_project_loaded and self.unsaved_changes:
            if self.ask_to_save():
                return
        folder_path, folder_name = UiWidgetCreator.open_folder(parent)
        if not folder_path:
            return False
        if template_id:
            network = templates[template_id]
        else:
            network = Network()
        network.name = os.path.basename(folder_name)
        self.project = Project(folder_path)
        self.project.network = network
        # self.project.file_location = file_name
        self.project.save_to_file()
        self.push_to_dash()
        
        self.launch()
        return True
        
    def save_network(self):
        self.unsaved_changes = False
        self.project.save_to_file()
        
    def open_network(self, parent):
        self.text_simulation_tab.stop_simulation()
        if self.is_project_loaded and self.unsaved_changes:
            if self.ask_to_save():
                return
        folder_path, _ = UiWidgetCreator.open_folder(parent)
        if not folder_path:
            return False
        self.project = Project.load_from_file(folder_path)
        # self.project.file_location = file_name
        self.push_to_dash()
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
            pass
            # self.ask_if_server_should_restart() # Could inflict bugs
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
        
    
        
    def push_to_dash(self, data: dict = None, sub_url = 'update-data'):
        if not self.is_project_loaded:
            return
        if not data:
            data = self.project.to_dict()
        self.server_push = PushData(data, self.server_url, sub_url=sub_url)
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
        
    #def ask_if_server_should_restart(self):
        #if self.is_asking_for_restart:
        #    return
        #self.is_asking_for_restart = True
        #
        #message = UiWidgetCreator.show_message('Connection to server lost. Do you want to restart the server?', 'Connection lost')
        #result = message.exec_()
        #if result != QtWidgets.QMessageBox.AcceptRole:
        #    return
        #self.terminate_server()
        #self.server_process = self.start_server()
        #self.is_asking_for_restart = False
        
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
        #self.listen_server.stop()
        #self.listen_server.deleteLater()
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
            
    def stats_update(self, filename, stats):
        #if 'stats' not in data.keys() or 'filename' not in data.keys():
        #    return
        self.popup = UiWidgetCreator.create_generate_popup(self, content='Saving...')
        self.save_thread = SaveStats(os.path.join(self.project.file_location, 'stats'), filename, stats)
        self.save_thread.finished.connect(self.save_finsihed)
        self.save_thread.start()
        self.popup.exec_()
        return
        
        
        self.project.stats[data['filename']] = SimStats.from_dict(data["stats"])
        self.unsaved_changes = True#
        # self.statistics_tab.show_webview()
        
    def save_finsihed(self):
        # self.project.stats[filename] = stats
        self.push_to_dash(data={})
        self.unsaved_changes = True
        self.save_thread.quit()
        self.save_thread.deleteLater()
        self.save_thread = None
        self.popup.deleteLater()
        
        return