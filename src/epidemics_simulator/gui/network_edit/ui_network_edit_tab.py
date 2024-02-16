from typing import Union
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable
from src.epidemics_simulator.gui.network_edit.ui_groups_edit import UiGroupEdit, ADD_ACTION, DUPLICATE_ACTION, UPDATE_ACTION, DELETE_ACTION
from src.epidemics_simulator.gui.network_edit.ui_connections_edit import UiConnectionEdit
from src.epidemics_simulator.gui.network_edit.ui_display_groups import UiDisplayGroup
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Project



class WorkerSignals(QObject):
    change_finished: pyqtSignal = pyqtSignal(NodeGroup)

class ChangeNetwork(QRunnable):
    def __init__(self, network: Network, action: int, group: NodeGroup, update_group: Union[dict, None], signals: WorkerSignals):
        super(ChangeNetwork, self).__init__()
        self.network = network
        self.action = action
        self.group = group
        self.update_group = update_group
        self.signals = signals
    def run(self):
        if self.action == ADD_ACTION:
            self.add_group()
        elif self.action == UPDATE_ACTION:
            self.change_group()
        elif self.action == DUPLICATE_ACTION:
            self.duplicate_group()
        elif self.action == DELETE_ACTION:
            self.delete_group()
        else:
            self.signals.change_finished.emit(None) # Should not happen
        
    def add_group(self):
        group = NodeGroup.init_from_dict(self.network, self.update_group)
        self.network.add_group(group)
        self.signals.change_finished.emit(group)
        
    def change_group(self):
        self.group.set_from_dict(self.update_group)
        self.signals.change_finished.emit(self.group)
        
    def duplicate_group(self):
        new_group = NodeGroup(self.network, self.group.name, self.group.size, self.group.age, self.group.vaccination_rate, self.group.max_vaccination_rate, self.group.avrg_int_con, self.group.delta_int_con, self.group.color)
        self.network.add_group(new_group)
        for ext_group, value in self.group.avrg_ext_con.items():
            new_group.add_external_connection(ext_group, value, self.group.delta_ext_con[ext_group])
        self.signals.change_finished.emit(new_group)
        
    def delete_group(self):
        self.network.delete_group(self.group.id)
        self.signals.change_finished.emit(self.group)
        


class UiNetworkEditTab(QObject):
    open_group_connections: pyqtSignal = pyqtSignal(NodeGroup)
    network_changed: pyqtSignal = pyqtSignal()
    generate_network: pyqtSignal = pyqtSignal()
    def __init__(self, parent: QtWidgets.QMainWindow):
        super(UiNetworkEditTab, self).__init__()
        self.parent = parent
        self.group_edit = UiGroupEdit(self, self.parent)
        self.connection_edit = UiConnectionEdit(self, self.parent)
        self.group_display = UiDisplayGroup(self, self.parent)
        self.tab_widget = self.parent.network_edit
        
        self.signals = WorkerSignals()
        
        self.popup = None
        self.changes_in_network = True
        
        self.connect_signals()

    def connect_signals(self):
        self.open_group_connections.connect(self.connection_edit.load_connections)
        self.network_changed.connect(self.parent.content_changed)
        self.network_changed.connect(self.network_change)
        self.signals.change_finished.connect(self.change_finished)
        self.generate_network.connect(self.group_display.start_generating)
        
        
    def init_ui(self, project: Project):
        self.group_edit.init_ui(project.network)
        self.connection_edit.init_ui(project.network)
        self.group_display.init_ui(project)
        
    def change_network(self, network: Network, action: int, group: NodeGroup, update_group: Union[dict, None]=None):
        popup_string = ''
        if action == ADD_ACTION:
            popup_string = 'Adding group...'
        elif action == UPDATE_ACTION:
            popup_string = 'Changing group...'
        elif action == DUPLICATE_ACTION:
            popup_string = 'Copying group...'
        elif action == DELETE_ACTION:
            popup_string = 'Deleting group...'
        self.popup = UiWidgetCreator.create_generate_popup(self.parent, content=popup_string)
        thread = ChangeNetwork(network, action, group, update_group, self.signals)
        self.parent.thread_pool.start(thread)
        self.popup.exec_()
        return self.changed_group
        
    def change_finished(self, group: Union[NodeGroup, None] = None):
        self.changed_group = group
        self.popup.deleteLater()
        
    def network_change(self):
        self.changes_in_network = True
                
    def show_webview(self):
        self.group_display.show_webview()
        
    def hide_webview(self):
        self.group_display.hide_webview()
        
    def unload(self):
        self.changes_in_network = True
        self.connection_edit.unload()
        self.group_edit.unload()
        self.group_display.unload()