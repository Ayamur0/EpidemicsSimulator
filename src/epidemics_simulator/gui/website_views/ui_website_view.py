from urllib.parse import urljoin
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import *
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from PyQt5.QtGui import QDesktopServices
class UiWebsiteView:
    def __init__(self, parent: QtWidgets.QMainWindow, sub_url, view_widget, open_browser_button, reload_button):
        super(UiWebsiteView, self).__init__()
        self.parent = parent
        self.view_widget = view_widget
        self.open_browser_button = open_browser_button
        self.reload_button = reload_button
        self.url = urljoin(self.parent.website_handler.base_url, sub_url)
                        
        self.load_webview()
        self.connect_signals()
        
        
    def load_webview(self):
        self.webview = QWebEngineView()
        self.webview.load(QUrl(self.url))
        self.view_widget.layout().addWidget(self.webview)
        
    def connect_signals(self):
        self.open_browser_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url)))
        self.reload_button.clicked.connect(lambda: self.webview.reload())
        
    def hide_webview(self):
        self.webview.hide()
        
    def show_webview(self):
        try:
            self.webview.loadFinished.disconnect()
        except TypeError:
            pass
        self.webview.loadFinished.connect(lambda: self.webview.show())
        self.webview.reload()
        
    def unload(self):
        self.webview.hide()