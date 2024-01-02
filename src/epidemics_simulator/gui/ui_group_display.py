from PyQt5 import QtWidgets
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from storage import Network, Node
import time
from src.epidemics_simulator.network_builder import NetworkBuilder
class Worker(QThread):
    finished = pyqtSignal()
    def __init__(self, network: Network, label: QtWidgets.QLabel) -> None:
        super().__init__()
        self.network = network
        self.label = label
        
    def run(self):
        start = time.time()
        self.generate_network(self.network)        
        generation_time = time.time() - start
        self.refresh_info_label(self.label, self.network, generation_time)
        
        self.finished.emit()
        
    def generate_network(self, network: Network):
        builder = NetworkBuilder(network)
        builder.build()

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
        self.webview.show()
        self.webview.load(QUrl("http://localhost:8050/view"))
        
        worker = Worker(network, self.network_editor.network_stats)
        worker.finished.connect(lambda: worker.quit())
        worker.finished.connect(lambda: worker.deleteLater())
        worker.start()       
        
    def unload(self):
        self.network_editor.unload_items_from_layout(self.network_editor.network_graph.layout())
    