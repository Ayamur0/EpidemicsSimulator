from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
class UiSimulation:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.webview = QWebEngineView()
        self.network_editor.simulation_view.layout().addWidget(self.webview)
        self.webview.hide()
        self.network_editor.open_browser_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("http://localhost:8050/sim")))
        
    def load_simulation(self):
        if not self.network_editor.server_connected:
            return
        self.webview.load(QUrl("http://localhost:8050/sim"))
        self.webview.show()
        
        
    def unload(self):
        # TODO refresh network on server
        pass
    