from .ui_widget_creator import UiWidgetCreator
from functools import partial
from PyQt5.QtCore import Qt
from storage import Network, NodeGroup
class UiNetworkConnections:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.network_editor.connection_list_content.layout().setAlignment(Qt.AlignTop)
        self.connection_buttons: dict = {}
        
    def load_connections(self, group: NodeGroup):
        self.network_editor.unload_items_from_layout(self.network_editor.connection_list_content.layout())
        
        other_groups = [g for g in group.network.groups if g.id != group.id]
        self.connection_buttons.clear()
        
        
        for g in other_groups:
            group_button = UiWidgetCreator.create_push_button(g.name, 'connection_list_btn', is_checkable=True)
            self.connection_buttons[g.id] = group_button
            group_button.clicked.connect(partial(self.load_connection_properties, group, g.id))
            self.network_editor.connection_list_content.layout().addWidget(group_button)
        
            
    def load_connection_properties(self, group_from: NodeGroup, group_to: str):
        self.network_editor.unload_items_from_layout(self.network_editor.connection_properties_content.layout())
        
        self.network_editor.deselect_other_buttons(group_to, self.connection_buttons)
        
        line_edits = self.open_connection_properties_input(group_from, group_to)
        
        save_button = UiWidgetCreator.create_push_button('Save', 'save_group_btn')
        save_button.clicked.connect(lambda: self.save_connection_input(line_edits, group_from, group_to))
        self.network_editor.connection_properties_content.layout().addRow(save_button)
        
    def open_connection_properties_input(self, group_from: NodeGroup, group_to: str):
        line_edits = {}
        for p, v in [
            ("connection average", group_from.avrg_ext_con.get(group_to, 0)),
            ("connection delta", group_from.delta_ext_con.get(group_to, 0)),
        ]:
            label = UiWidgetCreator.create_label(p, 'connection_label_properties')
            line_edit = UiWidgetCreator.create_line_edit(v, 'connection_line_edit_properties', regex_validator='^[0-9]+$')
            line_edits[p] = line_edit
            self.network_editor.connection_properties_content.layout().addRow(label, line_edit)
        return line_edits
        
        
    def save_connection_input(self, line_edits, group_from, group_to):
        updated_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        try:
            con_avrg = int(updated_dict.get('connection average'))
            con_dc = int(updated_dict.get('connection delta'))
            if con_dc > con_avrg:
                raise ValueError
        except TypeError:
            UiWidgetCreator.show_message(self.network_editor.connection_properties_content, "Pleas fill out every input", 'error_message')
            return
        except ValueError:
            UiWidgetCreator.show_message(self.network_editor.connection_properties_content, "Delta has to be smalller then average", 'error_message')
            return
        if not group_from.add_external_connection(group_to, con_avrg, con_dc):
            group_from.delete_external_connection(group_to)
            group_from.add_external_connection(group_to, con_avrg, con_dc)
        UiWidgetCreator.show_message(self.network_editor.connection_properties_content, "Successfully saved", "success_message")
            