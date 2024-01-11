import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import *
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Node, Project
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices


class UiStatisticTab:
    def __init__(self, main_window: QtWidgets.QMainWindow):
        self.main_window = main_window
        self.url = f'{self.main_window.server_url}/stats'
                
        self.open_view_in_browser = self.main_window.open_view_in_browser
        
        self.stat_view_widget = self.main_window.stat_view_widget
        self.tab_widget = self.main_window.stats_view
        
        self.webview = QWebEngineView()
        self.webview.load(QUrl(self.url))
        self.stat_view_widget.layout().addWidget(self.webview)
        
        
        self.open_view_in_browser.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url)))
        
    def init_ui(self):
        self.webview.hide()
        self.load_webview()
        
    def load_webview(self):
        self.show_webview()
        
    def hide_webview(self):
        self.webview.hide()
        
    def show_webview(self):
        if not self.main_window.is_server_connected:
            return
        try:
            self.webview.loadFinished.disconnect()
        except TypeError:
            pass
        self.webview.loadFinished.connect(lambda: self.webview.show())
        self.webview.reload()
        
        
        
    def unload(self):
        self.webview.hide()