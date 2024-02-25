from functools import partial
import os
import shutil
from PyQt5.QtCore import QThreadPool, QDir, pyqtSignal, pyqtSlot, QSize
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.gui.ui_startup import UiStartup
from src.epidemics_simulator.storage import Network, Project
from PyQt5.QtGui import QIcon
from src.epidemics_simulator.gui.templates import templates
from PyQt5 import QtWidgets, uic
from src.epidemics_simulator.gui.network_edit.ui_network_edit_tab import UiNetworkEditTab
from src.epidemics_simulator.gui.disease_edit.ui_disease_edit_tab import UiDiseaseEditTab
from src.epidemics_simulator.gui.text_simulation.ui_text_simulation import UiTextSimulationTab
from src.epidemics_simulator.gui.website_handler import WebsiteHandler
from src.epidemics_simulator.gui.website_views.ui_website_view import UiWebsiteView

class UiNetworkEditor(QtWidgets.QMainWindow):
    new_project: pyqtSignal = pyqtSignal(int)
    open_project: pyqtSignal = pyqtSignal()
    reset_ui: pyqtSignal = pyqtSignal()
    show_webviews: pyqtSignal = pyqtSignal(bool)
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        QDir.addSearchPath("assets", "assets/")
        self.set_font_size(12)
        self.init_icons()
        self.load_window()
        self.connect_signals()
        
        self.thread_pool  = QThreadPool()
        
        self.threads = []
        
        self.website_handler = WebsiteHandler(self, "http://127.0.0.1:8050")
        self.startup = UiStartup(self)
        self.network_edit_tab = UiNetworkEditTab(self)
        self.disease_edit_tab = UiDiseaseEditTab(self)
        self.simulation_tab = UiWebsiteView(self, "sim", self.simulation_view, self.open_browser_button, self.reload_sim)
        self.text_simulation_tab = UiTextSimulationTab(self)
        self.statistics_tab = UiWebsiteView(self, "stats", self.stat_view_widget, self.open_view_in_browser, self.reload_stats)
        
        self.project = None
        self.unsaved_changes = False
        
        self.website_handler.start_server.emit()
        self.startup.launch_startup.emit()
        
    def connect_signals(self):
        self.new_project.connect(self.new_network)
        self.open_project.connect(self.open_network)
        self.reset_ui.connect(self.reset)
        self.show_webviews.connect(self.enable_webviews)
        self.tabWidget.currentChanged.connect(self.on_tab_change)
        self.connect_menu_actions()
        
    def connect_menu_actions(self):
        self.actionNew.triggered.connect(lambda: self.new_network(-1))
        self.actionSave.triggered.connect(lambda: self.save_network())
        self.actionOpen.triggered.connect(lambda: self.open_network())
        self.populate_template_action()
        
    def populate_template_action(self):
        for i in range(0, len(templates)):
            template = templates[i]
            action = UiWidgetCreator.create_qaction(template.name, "template_menu_item", self)
            action.triggered.connect(partial(self.new_network, i))
            self.menuNew_from_template.addAction(action)
        
    def init_icons(self):
        # Icon Sources: https://www.flaticon.com/
        self.add_icon = QIcon("assets/add.png")
        self.save_icon = QIcon("assets/save.png")
        self.duplicate_icon = QIcon("assets/duplicate.png")
        self.remove_icon = QIcon("assets/delete.png")
        self.edit_icon = QIcon("assets/edit.png")
        
        self.start_icon = QIcon("assets/play.png")
        self.stop_icon = QIcon("assets/pause.png")
        
        self.new_icon = QIcon("assets/new_network.png")
        self.template_icon = QIcon("assets/template.png")
        self.open_icon = QIcon("assets/open.png")
        self.back_icon = QIcon("assets/back.png")
        
        self.window_icon = QIcon()
        self.window_icon.addFile("assets/window/16x16.png", QSize(16,16))
        self.window_icon.addFile("assets/window/24x24.png", QSize(24,24))
        self.window_icon.addFile("assets/window/32x32.png", QSize(32,32))
        self.window_icon.addFile("assets/window/48x48.png", QSize(48,48))
        self.window_icon.addFile("assets/window/256x256.png", QSize(256,256))
        self.window_icon.addFile("assets/window/512x512.png", QSize(256,256))
        
    def set_font_size(self, font_size: int):
        label = QtWidgets.QLabel("change_font", self)
        label.hide()
        font = label.font()
        font.setPointSize(font_size)  # Change the font size as needed
        QtWidgets.QApplication.setFont(font)
        label.deleteLater()
        
    def load_window(self):
        self.setWindowTitle("Epidemic Simulator")
        self.setWindowIcon(self.window_icon)
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        with open("qt/NetworkEdit/style_sheet.qss", mode="r", encoding="utf-8") as fp:
            self.stylesheet = fp.read()
        self.setStyleSheet(self.stylesheet)
        
   
    
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
            
    def create_alternate_line_color(self, iteration):
        return "rgb(65, 65, 65)" if iteration % 2 == 0 else "rgb(80, 80, 80)"
    
    
    def does_network_exist(self, folder_path: str):
        does_file_exist = os.path.join(folder_path, "network.json")
        if os.path.exists(does_file_exist) and os.path.isfile(does_file_exist):
            return True
        return False
    
    @pyqtSlot(int)
    def new_network(self, template_id=-1):        
        if self.unsaved_changes and self.ask_to_save():
            return
        folder_path, folder_name = UiWidgetCreator.open_folder(self, "Select New Project Folder")
        if not folder_path:
            return False
        if template_id != -1:
            network = templates[template_id]
        else:
            network = Network()
        if self.does_network_exist(folder_path):
            msg_box  = UiWidgetCreator.show_qmessagebox("A network file already exists in the directory.\nDo you want to override it?",  "Network Already Exists", default_button=1)
            result = msg_box.exec_()
            if result != QtWidgets.QMessageBox.AcceptRole:
                return
        stats_folder = os.path.join(folder_path, "stats")
        if os.path.exists(stats_folder):
            shutil.rmtree(stats_folder)
            
        network.name = os.path.basename(folder_name)
        self.project = Project(folder_path)
        self.project.network = network
        self.project.save_to_file()
        
        self.reset_ui.emit()
        try:
            self.startup.close_startup.emit()
        except RuntimeError:
            print("self.startup.close_startup No longer exists")
    
    @pyqtSlot()
    def open_network(self):       
        if self.unsaved_changes and self.ask_to_save():
            return
        folder_path, _ = UiWidgetCreator.open_folder(self, "Select Project Folder")
        if not folder_path:
            return False
        if not self.does_network_exist(folder_path):
            msg_box  = UiWidgetCreator.show_qmessagebox("No network was found in the directory.",  "No Network Found", only_ok=True)
            _ = msg_box.exec_()
            return
        try:
            self.project = Project.load_from_file(folder_path)
        except:
            msg_box  = UiWidgetCreator.show_qmessagebox("The file does not contain a valid JSON file.",  "Invalid Network File", only_ok=True)
            _ = msg_box.exec_()
            return
        if not self.project.network:
            msg_box  = UiWidgetCreator.show_qmessagebox("The file does not contain a valid network.",  "Invalid Network", only_ok=True)
            _ = msg_box.exec_()
            return
        self.reset_ui.emit()
        try:
            self.startup.close_startup.emit()
        except RuntimeError:
            print("self.startup.close_startup No longer exists")
    
    @pyqtSlot()
    def save_network(self):
        self.unsaved_changes = False
        if not self.project:
            return
        print("Saving project.")
        self.project.save_to_file()
        
    def ask_to_save(self):
        answer = UiWidgetCreator.save_popup("Do you want to save your changes?")
        if answer == QtWidgets.QMessageBox.Save:
            self.save_network()
            return False
        elif answer == QtWidgets.QMessageBox.No:
            return False
        elif answer == QtWidgets.QMessageBox.Cancel:
            return True
        
    def unload(self):
        self.network_edit_tab.unload()
        self.disease_edit_tab.unload()
        self.text_simulation_tab.unload()
        
    def init_uis(self):
        self.network_edit_tab.init_ui(self.project)
        self.disease_edit_tab.init_ui(self.project.network)
        self.text_simulation_tab.init_ui(self.project.network)  
        
    @pyqtSlot()
    def reset(self):
        self.enable_webviews(False)
        self.unload()
        
        self.push_to_dash(build=False)
        
        self.enable_webviews(True)
        self.init_uis()
        self.tabWidget.setCurrentIndex(0)

    
    @pyqtSlot(bool)
    def enable_webviews(self, status: bool):
        if not status or not self.website_handler.is_connected:
            self.network_edit_tab.hide_webview()
            self.simulation_tab.hide_webview()
            self.statistics_tab.hide_webview()
        else:
            self.network_edit_tab.show_webview()
            self.simulation_tab.show_webview()
            self.statistics_tab.show_webview()
    @pyqtSlot(int)
    def on_tab_change(self, index):
        network_change = self.network_edit_tab.changes_in_network
        disease_change = self.disease_edit_tab.disease_changed
        self.text_simulation_tab.stop_simulation()
        if index == 0:
            pass
        elif index == 1:
            pass
        elif index == 2:
            if network_change:
                self.ask_for_regeneration()
        elif index == 3:
            if network_change:
                self.ask_for_regeneration()
            elif disease_change:
                self.ask_for_reset()
        elif index == 4:
            self.push_to_dash(reset_view=True)
            
    def ask_for_regeneration(self):
        if len(self.project.network.groups) == 0:
            return False
        if self.network_edit_tab.group_display.generated_once:
            msg_string = "The changed network has not been built yet.\nDo you want to build the network?"
        else:
            msg_string = "The network has not been built yet.\nDo you want to build the network?"
        
        msg_box  = UiWidgetCreator.show_qmessagebox(msg_string, "Build the Network", default_button=0)
        result = msg_box.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return False
        self.network_edit_tab.generate_network.emit()
        return True
    
    def ask_for_reset(self):
        if len(self.project.network.groups) == 0:
            return
        msg_box  = UiWidgetCreator.show_qmessagebox(f"Diseases changed.\nDo you want to restart the simulation?", "Restart Simulation", default_button=0)
        result = msg_box.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return 
        self.text_simulation_tab.restart_simulation()
        self.disease_edit_tab.disease_changed = False

    def push_to_dash(self, reset_view: bool = False, build: bool = False):
        if not self.project:
            return
        if reset_view:
            data = {}
            sub_rul = "update-stats"
        else:
            data = {"data": self.project.to_dict(), "generate": build}
            sub_rul = "update-data"
        self.website_handler.push_to_dash.emit(sub_rul, data)
        
    def remove_sender_from_threads(self, sender):
        if sender in self.threads:
            self.threads.remove(sender)
            
    def generate_next_name(self, original_name: str, list_of_strings: list):
        i = 0
        next_name = f"{original_name}"
        while next_name in list_of_strings:
            i += 1
            next_name = f"{original_name} - ({i})"
        return next_name
        
    def closeEvent(self, event):
        if self.unsaved_changes and self.ask_to_save():
            event.ignore()
            return
        for thread in self.threads:
            thread.stop()
        self.website_handler.kill.emit()
        self.unload()
        event.accept()

    def content_changed(self):
        self.unsaved_changes = True