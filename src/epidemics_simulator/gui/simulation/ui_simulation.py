import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import *
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Node, Project
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices


class UiSimulationTab:
    def __init__(self, main_window: QtWidgets.QMainWindow):
        self.main_window = main_window
        
        self.url = f'{self.main_window.server_url}/sim'
                
        self.open_browser_button = self.main_window.open_browser_button
        
        self.simulation_view = self.main_window.simulation_view
        self.tab_widget = self.main_window.simulation
        self.webview = QWebEngineView()
        self.simulation_view.layout().addWidget(self.webview)
        
        
        self.open_browser_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url)))
        
    def init_ui(self):
        self.webview.hide()
        self.load_webview()
        
    def load_webview(self):
        if not self.main_window.is_server_connected:
            return
        self.webview.load(QUrl(self.url))
        self.show_webview()
        
    def hide_webview(self):
        self.webview.hide()
        
    def show_webview(self):
        print(self.main_window.is_server_connected)
        if not self.main_window.is_server_connected:
            return
        self.webview.show()
        
    def ask_for_regeneration(self):
        if UiWidgetCreator.ask_for_regeneration(self.main_window.network, self.main_window.network_edit_tab.group_display.generate_button):
           return # Did not want to regenerate 
    def unload(self):
        self.webview.hide()
        