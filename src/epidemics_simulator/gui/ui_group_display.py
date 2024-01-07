from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from storage import Network, Node
import time
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator

class Worker(QThread):
    finished = pyqtSignal()
    def __init__(self, network: Network) -> None:
        super().__init__()
        self.network = network
        
    def run(self):
        self.network.build()    
        self.finished.emit()
        
    

class UiGroupDisplay:
    def __init__(self, network_editor) -> None:      
        self.network_editor = network_editor
        self.view_buttons: dict = {}
        self.network_editor.network_stats.setText('\n\n\n')
        self.network_editor.generate_button.clicked.connect(lambda: self.start_generate_thread(self.network_editor.current_network))
        self.webview = QWebEngineView()
        self.webview.hide()
        self.network_editor.network_graph.layout().addWidget(self.webview)
        
        
    def start_generate_thread(self, network: Network):
        if self.network_editor.network_was_build:
            return
        
        self.worker = Worker(network)
        self.worker.finished.connect(lambda: self.worker_finished())
        self.start_time = time.time()
        self.worker.start() 
        self.popup = UiWidgetCreator.create_generate_popup(self.network_editor)
        self.popup.exec_()
        
    def refresh_info_label(self, label_to_write: QtWidgets.QLabel, network: Network, generation_time: float):
        label_text = f'Some stats about graph creation\n'
        total_nodes, total_connections = self.get_network_info(network)
        label_text += f'Total nodes {total_nodes}\n'
        label_text += f'Total connections {total_connections}\n'
        label_text += f'Generation time {generation_time:.2f}s'
        label_to_write.setText(label_text)
        
    def get_network_info(self, network: Network):
        total_nodes = 0
        total_connections = 0
        visited_groups: list[str] = []
        for group in network.groups:
            if not group.active:
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
        
    def worker_finished(self):
        generation_time = time.time() - self.start_time
        label = self.network_editor.network_stats
        self.refresh_info_label(label, self.network_editor.current_network, generation_time)
        print('Finished Generating')
        self.popup.deleteLater()
        
        
        self.worker.quit()
        self.worker.deleteLater()
        if self.network_editor.server_connected:
            self.webview.show()
            self.webview.load(QUrl("http://localhost:8050/view"))
        self.network_editor.network_was_build = True
        
    def unload(self):
        self.webview.hide()
        self.network_editor.network_stats.setText('\n\n\n')
        try:
            self.popup.deleteLater()
        except AttributeError:
            pass
        except RuntimeError:
            pass
    