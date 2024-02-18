import time
from urllib.parse import urljoin
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QUrl, QObject, QRunnable
from PyQt5.QtWebEngineWidgets import *
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Node, Project
from PyQt5.QtGui import QDesktopServices
class WorkerSignals(QObject):
    generation_finished: pyqtSignal = pyqtSignal()
    
class NetworkGenerator(QRunnable):
    def __init__(self, project: Project, push_to_dash_signal: pyqtSignal, signals: WorkerSignals):
        super(NetworkGenerator, self).__init__()
        self.project = project
        self.push_to_dash_signal = push_to_dash_signal
        self.signal = signals
        
    def run(self):
        self.push_to_dash_signal.emit('update-data', self.project.to_dict())
        self.project.network.build()    
        self.signal.generation_finished.emit()
class UiDisplayGroup(QObject):
    def __init__(self, parent: QObject, main_window: QtWidgets.QMainWindow):
        super(UiDisplayGroup, self).__init__()
        self.parent = parent
        self.main_window = main_window
        self.url = urljoin(self.main_window.website_handler.base_url, 'view')
                
        self.generate_button = self.main_window.generate_button
        
        self.push_to_dash_signal = self.main_window.website_handler.push_to_dash
        self.worker_signals = WorkerSignals()
        
        self.network_graph = self.main_window.network_graph
        self.stat_label: QtWidgets.QLabel = self.main_window.network_stats
        self.open_browser_button = self.main_window.open_in_browser_button
        self.reload_view = self.main_window.reload_view
        
        self.generated_once = False
        self.generation_in_progress = False
        
        self.thread_pool = self.main_window.thread_pool
        
        self.load_webview()
        self.connect_signals()

        
    def load_webview(self):
        self.webview = QWebEngineView()
        self.webview.load(QUrl(self.url))
        self.network_graph.layout().addWidget(self.webview)
        
    def connect_signals(self):
        self.open_browser_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url)))
        self.reload_view.clicked.connect(lambda: self.webview.reload())
        
        self.worker_signals.generation_finished.connect(self.generating_finished)
        
    def init_ui(self, project: Project):
        self.project = project
        self.network = project.network
        self.stat_label.setText('Graph building stats\nTotal nodes 0\nTotal connections 0\nGeneration time 0s')
        self.webview.hide()
        try:
            self.generate_button.clicked.disconnect()
        except TypeError:
            pass
        self.generate_button.clicked.connect(self.start_generating)
        
        
    def start_generating(self):
        if self.generated_once and not self.parent.changes_in_network and not self.main_window.disease_edit_tab.disease_changed:
            msg_box = UiWidgetCreator.show_qmessagebox('Network did not cahnge.\nDo you want to build again?', 'Building network')
            result = msg_box.exec_()
            if result != QtWidgets.QMessageBox.AcceptRole:
                return
        total_nodes = self.get_node_count()
        if total_nodes >= 20000:
            msg_box = UiWidgetCreator.show_qmessagebox('Building a network with more than 20,000 nodes may take a while.\nDo you want to continue?', 'Building network')
            result = msg_box.exec_()
            if result != QtWidgets.QMessageBox.AcceptRole:
                return
        print('Started building.')
        self.generation_in_progress = True
        thread = NetworkGenerator(self.project, self.push_to_dash_signal, self.worker_signals)
        self.popup = UiWidgetCreator.create_generate_popup(self.main_window)
        self.start_time = time.time()
        self.thread_pool.start(thread)
        self.popup.exec_()
        
        
    def generating_finished(self):
        self.generation_in_progress = False
        self.main_window.text_simulation_tab.restart_simulation()
        generation_time = time.time() - self.start_time
        self.refresh_info_label(generation_time)
        self.generated_once = True
        print('Finished building')
        self.main_window.show_webviews.emit(True)
        self.parent.changes_in_network = False
        self.main_window.disease_edit_tab.disease_changed = False
        self.popup.deleteLater()
        
    def hide_webview(self):
        if self.generated_once:
            return
        self.webview.hide()
        
    def show_webview(self):
        if not self.generated_once:
            return
        try:
            self.webview.loadFinished.disconnect()
        except TypeError:
            pass
        self.webview.loadFinished.connect(lambda: self.webview.show())
        self.webview.reload()
        
    def refresh_info_label(self, generation_time: float):
        label_text = f'Graph building stats\n'
        total_nodes, total_connections = self.get_network_info()
        label_text += f'Total nodes {total_nodes}\n'
        label_text += f'Total connections {total_connections}\n'
        label_text += f'Generation time {generation_time:.2f}s'
        self.stat_label.setText(label_text)
        
    def get_node_count(self):
        total_nodes = 0
        for group in self.network.groups:
            if not group.active:
                continue
            total_nodes += group.size
        return total_nodes
        
        
        
    def get_network_info(self):
        total_nodes = 0
        total_connections = 0
        visited_groups: list[str] = []
        for group in self.network.groups:
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
    
    
    def unload(self):
        try:
            self.popup.deleteLater()
        except AttributeError:
            pass
        except RuntimeError:
            pass
        self.generated_once = False
        self.generation_in_progress = False
        
        self.stat_label.setText('Graph building stats\nTotal nodes 0\nTotal connections 0\nGeneration time 0s')
        self.webview.hide()
        