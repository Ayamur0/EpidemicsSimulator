import random
from storage import Network, NodeGroup
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .ui_widget_creator import UiWidgetCreator
class UiNetworkGroups:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.network_editor.group_list_content.layout().setAlignment(Qt.AlignTop)
        self.group_buttons: dict = {}
        
    def add_group(self, group, network):
        self.error_incomplete_input = False
        self.error_delta = False
        
        layout_widget = UiWidgetCreator.create_hbox_widget('group_list_layout')
        
        checkbox = UiWidgetCreator.create_checkbox('group_list_btn', True)
        
        group_button = UiWidgetCreator.create_push_button(group.name, 'group_list_btn', True)
        group_button.clicked.connect(lambda: self.load_properties(group, network))
        self.group_buttons[group.id] = group_button
        
        layout_widget.layout().addWidget(checkbox)
        layout_widget.layout().addWidget(group_button)
        
        self.network_editor.group_list_content.layout().addWidget(layout_widget)
    
    def new_group_button_input(self, network):
        add_group_button = UiWidgetCreator.create_push_button('+', 'add_group_btn', is_checkable=True)
        add_group_button.clicked.connect(lambda: self.create_new_group_input(network))
        self.network_editor.group_list_content.layout().addWidget(add_group_button)
        self.group_buttons['-1'] = add_group_button
    
    def create_new_group_input(self, network):
        self.network_editor.unload_items_from_layout(self.network_editor.group_properties_content.layout())
        self.network_editor.unload_items_from_layout(self.network_editor.connection_properties_content.layout())
        
        self.network_editor.deselect_other_buttons('-1', self.group_buttons)
        
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
        
        line_edits = line_edits = self.open_group_properties_input(default_dict)
        
        self.save_properties_button(line_edits, None, network)
        
    def load_properties(self, group, network):
        self.network_editor.unload_items_from_layout(self.network_editor.group_properties_content.layout())
        self.network_editor.unload_items_from_layout(self.network_editor.connection_properties_content.layout())
        
        self.network_editor.deselect_other_buttons(group.id, self.group_buttons)
        
        self.network_editor.connections.load_connections(group)
        
        properties = group.get_properties_dict()
        
        line_edits = self.open_group_properties_input(properties)
        
        self.save_properties_button(line_edits, group, network)
        
    def save_properties_button(self, line_edits, group, network):
        save_btn = UiWidgetCreator.create_push_button('Save', 'save_group_btn')
        save_btn.clicked.connect(lambda: self.save_properties_input(line_edits, group, network))
        self.network_editor.group_properties_content.layout().addRow(save_btn)
        
    def save_properties_input(self, line_edits: dict, group: NodeGroup, network: Network):
        updated_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        if group:
            try:
                group.set_from_dict(updated_dict)
            except ValueError as e:
                if str(e) == "Delta has to be smalller then average":
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, str(e), 'error_message')
                else:
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, "Pleas fill out every input", 'error_message')
                return
            self.network_editor.unload_items_from_layout(self.network_editor.group_list_content.layout())
            self.network_editor.unload_items_from_layout(self.network_editor.group_properties_content.layout())
            self.network_editor.load_groups(network)
            self.network_editor.deselect_other_buttons(group.id, self.group_buttons)
            self.load_properties(group, network) # might cause errors later 
            UiWidgetCreator.show_message(self.network_editor.group_properties_content, "Successfully saved", "success_message")
        else:
            try:
                group = NodeGroup.init_from_dict(network, updated_dict)
                network.add_group(group)
            except ValueError as e:
                if str(e) == "Delta has to be smalller then average":
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, str(e), 'error_message')
                else:
                    UiWidgetCreator.show_message(self.network_editor.group_properties_content, "Pleas fill out every input", 'error_message')
                return
            self.network_editor.unload_items_from_layout(self.network_editor.group_list_content.layout())
            self.network_editor.unload_items_from_layout(self.network_editor.group_properties_content.layout())
            self.network_editor.load_groups(network)
            self.network_editor.deselect_other_buttons(group.id, self.group_buttons)
            self.load_properties(group, network) # might cause errors later 
    

    def open_group_properties_input(self, properties):
        line_edits = {}
        for p, v in properties.items():
            label = UiWidgetCreator.create_label(p, 'group_label_properties')
            regex_validator = '.*'
            if p == 'vaccination rate' or p == 'max vaccination rate':
                regex_validator = '^0(\.\d+)?$|^1(\.0+)?$'
            elif p == 'color':
                color = self.generate_random_color().name() if not v else v
                color_button = UiWidgetCreator.create_push_button(None, 'color_button', style_sheet=f'background: {color};')
                color_button.clicked.connect(lambda: UiWidgetCreator.show_color_dialog(line_edit, color_button))
                line_edit = UiWidgetCreator.create_line_edit(color, 'group_line_edit_properties', regex_validator=regex_validator)
                line_edits[p] = line_edit
                self.network_editor.group_properties_content.layout().addRow(label, color_button)
                continue
            elif p != 'name':
                regex_validator = '^[0-9]+$'
            line_edit = UiWidgetCreator.create_line_edit(v, 'group_line_edit_properties', regex_validator=regex_validator)
            self.network_editor.group_properties_content.layout().addRow(label, line_edit)
            line_edits[p] = line_edit
        return line_edits

    def generate_random_color(self):
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        return QColor(red, green, blue)
    
    def show_color_dialog(self, line_edit, color_button):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            hex_color = color.name()
            line_edit.setText(hex_color)
            color_button.setStyleSheet(f'background: {hex_color};')