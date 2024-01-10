import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import *
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Node, Project
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices

class GenerateNetwork(QThread):
    finished = pyqtSignal()
    def __init__(self, network: Network) -> None:
        super().__init__()
        self.network = network
        
    def run(self):
        self.network.build()    
        self.finished.emit()

class UiDisplayGroup:
    def __init__(self, main_window: QtWidgets.QMainWindow):
        self.main_window = main_window
        self.url = f'{self.main_window.server_url}/view'
                
        self.generate_button = self.main_window.generate_button
        
        self.network_graph = self.main_window.network_graph
        self.stat_label: QtWidgets.QLabel = self.main_window.network_stats
        self.open_browser_button = self.main_window.open_in_browser_button
        
        self.webview = QWebEngineView()
        self.webview.load(QUrl(self.url))
        self.network_graph.layout().addWidget(self.webview)
        
        
        
        self.open_browser_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url)))
        
        self.generated_once = False
        
        
        
    def init_ui(self, network: Network):
        self.network = network
        self.stat_label.setText('\n\n\n')
        self.webview.hide()
        try:
            self.generate_button.clicked.disconnect()
        except TypeError:
            pass
        self.generate_button.clicked.connect(partial(self.start_generating, self.network))
            
        
    def start_generating(self, network: Network):
        self.generate_thread = GenerateNetwork(network)
        self.generate_thread.finished.connect(lambda: self.generating_finished())
        self.start_time = time.time()
        self.generate_thread.start() 
        self.popup = UiWidgetCreator.create_generate_popup(self.main_window)
        self.popup.exec_()
        
    def generating_finished(self):
        generation_time = time.time() - self.start_time
        self.refresh_info_label(self.network, generation_time)
        self.main_window.push_to_dash()
        self.main_window.server_push.wait()
        self.main_window.generated_network = True
        self.generated_once = True
        print('Finished Generating')
        self.popup.deleteLater()
        self.load_webview()
        
        
        
        
    def load_webview(self):
        self.main_window.show_webviews()
        #self.show_webview()
        
    def hide_webview(self):
        if self.generated_once:
            return
        self.webview.hide()
        
    def show_webview(self):
        if not self.main_window.is_server_connected:
            return
        if not self.generated_once:
            return
        try:
            self.webview.loadFinished.disconnect()
        except TypeError:
            pass
        self.webview.loadFinished.connect(lambda: self.webview.show())
        self.webview.reload()
        #self.webview.show()
        
    def refresh_info_label(self, network: Network, generation_time: float):
        label_text = f'Some stats about graph creation\n'
        total_nodes, total_connections = self.get_network_info(network)
        label_text += f'Total nodes {total_nodes}\n'
        label_text += f'Total connections {total_connections}\n'
        label_text += f'Generation time {generation_time:.2f}s'
        self.stat_label.setText(label_text)
        
    def get_network_info(self, network: Network):
        total_nodes = 0
        total_connections = 0
        visited_groups: list[str] = []
        for group in network.groups:
            if not group.active:
                visited_groups.append(group.id)
                continue
            total_nodes += group.size
            for node in group.members:
                total_connections += node.int_conn_amount
                total_connections += node.get_ext_conn_amount()
                total_connections -= self.uncount_duplicate_connections(node, visited_groups)
            visited_groups.append(group.id)
        return total_nodes, total_connections
    
    def uncount_duplicate_connections(self, node: Node, already_visited_groups: list[str]):
        to_remove = 0
        for group in already_visited_groups:
            to_remove += node.get_ext_conn_amount(to_group=group)
        return to_remove
        
    def unload_woker(self):
        try:
            self.worker.quit()
            self.worker.deleteLater()
        except AttributeError:
            pass
        except RuntimeError:
            pass
        
    def unload(self):
        try:
            self.popup.deleteLater()
        except AttributeError:
            pass
        except RuntimeError:
            pass
        self.unload_woker()
        self.stat_label.setText('\n\n\n')
        self.webview.hide()
        