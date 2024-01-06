from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
class UiStatsView:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.webview = QWebEngineView()
        self.network_editor.stat_view_widget.layout().addWidget(self.webview)
        self.webview.hide()
        self.network_editor.open_view_in_browser.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("http://localhost:8050/stats")))
        
    def load_stats(self):
        if not self.network_editor.server_connected:
            return
        self.webview.load(QUrl("http://localhost:8050/stats"))
        self.webview.show()
        
        
    def unload(self):
        # TODO refresh network on server
        pass
    