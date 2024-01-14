from PyQt5 import QtWidgets
import random
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Project
from functools import partial
from PyQt5.QtCore import Qt

class UiConnectionEdit:
    def __init__(self, main_window: QtWidgets.QMainWindow):
        self.main_window = main_window
        
        self.con_label = self.main_window.con_label
        
        self.save_connection_prop_button = self.main_window.save_connections_btn
        self.save_connection_prop_button.setText(None)
        self.save_connection_prop_button.setIcon(self.main_window.save_icon)
        
        self.connection_list = self.main_window.connection_list_content
        self.connection_prop = self.main_window.connection_properties_content
                
        self.connection_buttons: dict = {}
        
    def init_ui(self, network: Network):
        self.network = network
        self.save_connection_prop_button.hide()        
        
    def load_connections(self, network: Network, group_from: NodeGroup):
        self.unload()
        self.con_label.setText(f'{group_from.name} Connections')
        other_groups = [g for g in network.groups if g.id != group_from.id]
        for group in other_groups:
            self.load_connection_button(group_from, group)
            
    def load_connection_button(self, group_from: NodeGroup, group_to: NodeGroup):
        layout_widget = UiWidgetCreator.create_qwidget('connection_select', QtWidgets.QHBoxLayout)
        
        group_button = UiWidgetCreator.create_qpush_button(group_to.name, 'group_select_button', is_checkable=True)
        
        group_button.clicked.connect(partial(self.show_connection_properties, group_from, group_to))
        
        self.connection_buttons[group_to.id] = group_button
        
        layout_widget.layout().addWidget(group_button)
        
        self.connection_list.layout().addWidget(layout_widget)
        
    def show_connection_properties(self, group_from: NodeGroup, group_to: NodeGroup):
        self.unload_properties()
        self.save_connection_prop_button.show()
        self.main_window.deselect_other_buttons(group_to.id, self.connection_buttons)
        
        
        
        properties = {'connection average': group_from.avrg_ext_con.get(group_to.id, 0),
                      "connection delta": group_from.delta_ext_con.get(group_to.id, 0)}
        
        line_edits = self.load_properties_input(properties)
        self.connect_save_button(group_from, group_to, line_edits)
        
    def connect_save_button(self, group_from: NodeGroup, group_to: NodeGroup, line_edits: dict):
        try:
            self.save_connection_prop_button.clicked.disconnect()
        except TypeError:
            pass
        self.save_connection_prop_button.clicked.connect(partial(self.save_connection_properties, group_from, group_to, line_edits))
        
    def save_connection_properties(self, group_from: NodeGroup, group_to: NodeGroup, line_edits: dict):
        updated_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        try:
            if updated_dict.get('connection average') == '' or updated_dict.get('connection delta') == '':
                raise TypeError
            con_avrg = int(updated_dict.get('connection average'))
            con_dc = int(updated_dict.get('connection delta'))
            if con_dc > con_avrg:
                raise ValueError
        except TypeError:
            UiWidgetCreator.show_status(self.connection_prop, "Pleas fill out every input", 'error_message', True)
            return
        except ValueError:
            UiWidgetCreator.show_status(self.connection_prop, "Delta has to be smalller then average", 'error_message', True)
            return
        if not group_from.add_external_connection(group_to.id, con_avrg, con_dc):
            group_from.delete_external_connection(group_to.id)
            group_from.add_external_connection(group_to.id, con_avrg, con_dc)
        self.main_window.network_changed.emit()
        UiWidgetCreator.show_status(self.connection_prop, "Successfully saved", "success_message", True)
        
    def load_properties_input(self, properties: dict):
        line_edits: dict = {}
        for key, value in properties.items():
            label = UiWidgetCreator.create_qlabel(key, 'connection_label_properties')
            line_edit = UiWidgetCreator.create_qline_edit(value, 'connection_line_edit_properties', regex_validator='^[0-9]+$')
            line_edits[key] = line_edit
            self.connection_prop.layout().addRow(label, line_edit)
        return line_edits
    
    def unload_properties(self):
        self.main_window.unload_items_from_layout(self.connection_prop.layout())
        
    def unload_connection_list(self):
        self.connection_buttons.clear()
        self.main_window.unload_items_from_layout(self.connection_list.layout())
        
    def unload(self):
        self.con_label.setText(f'Connections')
        self.unload_properties()
        self.unload_connection_list()
