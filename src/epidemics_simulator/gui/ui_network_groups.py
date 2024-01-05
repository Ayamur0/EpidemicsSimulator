import random
from storage import Network, NodeGroup
from PyQt5 import QtWidgets
from functools import partial
from PyQt5.QtCore import Qt

from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
class UiNetworkGroups:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.network_editor.group_list_content.layout().setAlignment(Qt.AlignTop)
        self.group_buttons: dict = {}
        self.group_layouts: dict = {}
        self.network_editor.save_properties_btn.hide()
        self.is_creating_group = False
        
    def add_group(self, group: NodeGroup, network: Network):
        self.error_incomplete_input = False
        self.error_delta = False
        
        layout_widget = UiWidgetCreator.create_layout_widget('group_list_layout', QtWidgets.QHBoxLayout())
        
        checkbox = UiWidgetCreator.create_checkbox('group_list_btn', group.active)
        checkbox.stateChanged.connect(lambda: self.change_group_activity(checkbox, group))
        
        group_button = UiWidgetCreator.create_push_button(group.name, 'group_list_btn', True)
        group_button.clicked.connect(lambda: self.load_properties(group, network))
        self.group_buttons[group.id] = group_button
        
        delete_button = UiWidgetCreator.create_push_button('del', 'group_del_btn')
        delete_button.clicked.connect(lambda: self.delete_group(group, network))
        
        layout_widget.layout().addWidget(checkbox)
        layout_widget.layout().addWidget(group_button)
        layout_widget.layout().addWidget(delete_button)
        
        self.group_layouts[group.id] = layout_widget
        self.network_editor.group_list_content.layout().addWidget(layout_widget)
        
    def duplicate_group(self):
        self.network_editor.network_changed.emit()
        # TODO
        
    def delete_group(self, group: NodeGroup, network: Network):
        msg_box  = UiWidgetCreator.create_delete_dialog(f'Are you sure you want to delete the group "{group.name}"?')
        result = msg_box.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return
        index = self.network_editor.group_list_content.layout().indexOf(self.group_layouts[group.id])
        if index == -1:
            raise ValueError
        selected_button = self.network_editor.get_selected_button(self.group_buttons)
        widget_item = self.network_editor.group_list_content.layout().takeAt(index)
        widget_item.widget().deleteLater()
        if selected_button == self.group_buttons[group.id]:
            self.reset_group_view()
        del self.group_buttons[group.id]
        del self.group_layouts[group.id]
        network.delete_group(group.id)
        self.network_editor.network_changed.emit()

        
    def change_group_activity(self, checkbox: QtWidgets.QCheckBox, group: NodeGroup):
        group.active = checkbox.isChecked()
    
    def new_group_button_input(self, network: Network):
        add_group_button = self.network_editor.new_group_btn
        try:
            add_group_button.clicked.disconnect()
        except TypeError:
            pass
        add_group_button.clicked.connect(lambda: self.create_new_group_input(network))
        self.group_buttons['-1'] = add_group_button
    
    def create_new_group_input(self, network: Network):
        self.network_editor.deselect_other_buttons('-1', self.group_buttons)

        if self.is_creating_group:
            UiWidgetCreator.show_message(self.network_editor.group_list_content, 'Please finish current group creation', 'error_message', True, is_row=False)
            return

        self.is_creating_group = True
        self.unload_group_properties()
        self.network_editor.connections.unload()

        default_dict = {
            "name": '',
            "member count": '',
            "average internal connections": '',
            "internal connection delta": '',
            "age": '',
            "vaccination rate": '',
            "max vaccination rate": '',
            "color": ''
        }

        line_edits = self.open_group_properties_input(default_dict)

        # Disconnect the signal before connecting it again
        add_group_button = self.network_editor.new_group_btn
        #add_group_button.clicked.disconnect()
        #add_group_button.clicked.connect(lambda: self.create_new_group_input(network))
        
        self.save_properties_button(line_edits, None, network)
        
    def load_properties(self, group: NodeGroup, network: Network):
        self.is_creating_group = False
        self.unload_group_properties()
        #self.network_editor.unload_items_from_layout(self.network_editor.group_properties_content.layout())
        self.network_editor.connections.unload()
        
        self.network_editor.deselect_other_buttons(group.id, self.group_buttons)
        
        self.network_editor.connections.load_connections(group)
        
        properties = group.get_properties_dict()
        
        line_edits = self.open_group_properties_input(properties)
        
        self.save_properties_button(line_edits, group, network)
        
    def save_properties_button(self, line_edits: list, group: NodeGroup, network: Network):
        save_btn = self.network_editor.save_properties_btn
        try:
            save_btn.clicked.disconnect()
        except TypeError:
            pass
        save_btn.clicked.connect(lambda: self.save_properties_input(line_edits, group, network))
        
    def save_properties_input(self, line_edits: dict, group: NodeGroup, network: Network):
        updated_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        if group:
            try:
                group.set_from_dict(updated_dict)
            except ValueError as e:
                if str(e) == "Delta has to be smalller then average":
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, str(e), 'error_message', True)
                else:
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, "Pleas fill out every input", 'error_message', True)
                return
            self.is_creating_group = False
            self.unload_group_list()
            self.network_editor.load_groups(network)
            UiWidgetCreator.show_message(self.network_editor.group_properties_content, "Successfully saved", "success_message", True)
        else:
            try:
                group = NodeGroup.init_from_dict(network, updated_dict)
                network.add_group(group)
            except ValueError as e:
                if str(e) == "Delta has to be smalller then average":
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, str(e), 'error_message', True)
                else:
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, "Pleas fill out every input", 'error_message', True)
                return
            self.is_creating_group = False
            self.unload()
            self.network_editor.load_groups(network)
            self.load_properties(group, network)
            UiWidgetCreator.show_message(self.network_editor.group_properties_content, "Successfully added", "success_message", True)
        #self.network_editor.unload_items_from_layout(self.network_editor.group_list_content.layout())
        self.network_editor.deselect_other_buttons(group.id, self.group_buttons)
        self.network_editor.network_changed.emit()
    

    def open_group_properties_input(self, properties: dict):
        self.network_editor.save_properties_btn.show()
        line_edits = {}
        for p, v in properties.items():
            label = UiWidgetCreator.create_label(p, 'group_label_properties')
            regex_validator = '.*'
            if p == 'vaccination rate' or p == 'max vaccination rate':
                regex_validator = '^0(\.\d+)?$|^1(\.0+)?$'
            elif p == 'color':
                _, line_edit = UiWidgetCreator.create_color_button(p, self.network_editor.group_properties_content.layout(), v)
                line_edits[p] = line_edit
                continue
            elif p != 'name':
                regex_validator = '^[0-9]+$'
            line_edit = UiWidgetCreator.create_line_edit(v, 'group_line_edit_properties', regex_validator=regex_validator)
            self.network_editor.group_properties_content.layout().addRow(label, line_edit)
            line_edits[p] = line_edit
        return line_edits
    
    def show_color_dialog(self, line_edit: QtWidgets.QLineEdit, color_button: QtWidgets.QPushButton):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            hex_color = color.name()
            line_edit.setText(hex_color)
            color_button.setStyleSheet(f'background: {hex_color};')
            
    def reset_group_view(self):
        
        #self.network_editor.save_properties_btn.hide()
        self.network_editor.connections.unload()
        self.unload_group_properties()
        #self.network_editor.unload_items_from_layout(self.network_editor.group_properties_content.layout())
        
    def unload_group_list(self):
        self.group_buttons.clear()
        self.network_editor.unload_items_from_layout(self.network_editor.group_list_content.layout())
           
    def unload_group_properties(self):
        self.network_editor.save_properties_btn.hide()
        self.network_editor.unload_items_from_layout(self.network_editor.group_properties_content.layout())
            
    def unload(self):
        self.unload_group_list()
        self.unload_group_properties()