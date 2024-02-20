from typing import Union
from PyQt5 import QtWidgets
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup
from functools import partial
from PyQt5.QtCore import Qt, QObject
ADD_ACTION = 0
UPDATE_ACTION = 1
DUPLICATE_ACTION = 2
DELETE_ACTION = 3
class UiGroupEdit(QObject):
    def __init__(self, parent: QObject, main_window: QtWidgets.QMainWindow):
        super(UiGroupEdit, self).__init__()
        self.parent = parent
        self.main_window = main_window
        
        self.new_group_button = self.main_window.new_group_btn
        self.save_group_prop_button = self.main_window.save_properties_btn
        
        self.group_list = self.main_window.group_list_content

        self.save_status = self.main_window.save_status
        self.porp_label = self.main_window.prop_label
        self.prop_input = self.main_window.prop_input
        
        self.group_buttons: dict = {}
        
        self.is_creating_group = False
        
        self.set_alignments()
        self.connect_signals()
        self.set_button_contents()
    
                

        
    def set_alignments(self):
        self.group_list.layout().setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.save_status.layout().setAlignment(Qt.AlignCenter)
        self.porp_label.layout().setAlignment(Qt.AlignTop)
        self.prop_input.layout().setAlignment(Qt.AlignTop)
        
    def connect_signals(self):
        self.new_group_button.clicked.connect(lambda: self.create_new_group())
        
    def set_button_contents(self):
        self.new_group_button.setText(None)
        self.save_group_prop_button.setText(None)
        self.new_group_button.setIcon(self.main_window.add_icon)
        self.save_group_prop_button.setIcon(self.main_window.save_icon)
        
    def init_ui(self, network: Network):
        self.network = network
        self.save_group_prop_button.hide()
        self.load_groups()
        
    def load_groups(self):
        self.group_buttons["-1"] = self.new_group_button
        for group in self.network.groups:
            self.load_group_button(group)
            
    def load_group_button(self, group: NodeGroup):
        layout_widget = UiWidgetCreator.create_qwidget("group_select", QtWidgets.QHBoxLayout)
        layout_widget.layout().setAlignment(Qt.AlignCenter)
        
        checkbox = UiWidgetCreator.create_qcheckbox("activity_checkbox", group.active)
        duplicate_button = UiWidgetCreator.create_qpush_button(None, "duplicate_button", icon=self.main_window.duplicate_icon)
        remove_button = UiWidgetCreator.create_qpush_button(None, "delete_button", icon=self.main_window.remove_icon)
        group_button = UiWidgetCreator.create_qpush_button(None, "select_button", is_checkable=True, icon=self.main_window.edit_icon)
        group_label = UiWidgetCreator.create_qlabel(group.name, "group")
        
        checkbox.stateChanged.connect(partial(self.set_group_activity, checkbox, group))
        duplicate_button.clicked.connect(partial(self.dupliacte_group, group))
        remove_button.clicked.connect(partial(self.remove_group, group))
        group_label.mousePressEvent = partial(UiWidgetCreator.label_clicked, group_button, True)
        group_button.clicked.connect(partial(self.show_group_properties, group))
        
        self.group_buttons[group.id] = group_button
        
        layout_widget.layout().addWidget(checkbox)
        layout_widget.layout().addWidget(duplicate_button)
        layout_widget.layout().addWidget(remove_button)
        layout_widget.layout().addWidget(group_label)
        layout_widget.layout().addWidget(group_button)
        self.group_list.layout().addWidget(layout_widget,alignment=Qt.AlignLeft|Qt.AlignTop)
        
    def set_group_activity(self, checkbox: QtWidgets.QCheckBox, group: NodeGroup):
        group.active = checkbox.isChecked()
        self.parent.network_changed.emit()
        
    def dupliacte_group(self, group: NodeGroup):
        new_group = self.parent.change_network(self.network, DUPLICATE_ACTION, group)
        self.unload()
        self.load_groups()
        self.parent.network_changed.emit()
        self.group_buttons[new_group.id].click()
        
    def remove_group(self, group: NodeGroup):
        message = UiWidgetCreator.show_qmessagebox(f"Are you sure you want to delete group {group.name}?", "Delete Group")
        result = message.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return
        self.parent.change_network(self.network, DELETE_ACTION, group)
        self.unload()
        self.load_groups()
        self.parent.network_changed.emit()
        
    def show_group_properties(self, group: NodeGroup=None, default_properties: dict=None):
        self.unload_group_properties()
        if group:
            self.parent.open_group_connections.emit(group)
        if group:
            self.is_creating_group = False
            self.main_window.deselect_other_buttons(group.id, self.group_buttons)
            properties = group.get_properties_dict()
        else:
            self.main_window.deselect_other_buttons("-1", self.group_buttons)
            properties = default_properties
        self.save_group_prop_button.show()
        line_edits = self.load_properties_input(properties)
        self.connect_save_button(group, line_edits)
        
    def connect_save_button(self, group: NodeGroup, line_edits: dict):
        try:
            self.save_group_prop_button.clicked.disconnect()
        except TypeError:
            pass
        self.save_group_prop_button.clicked.connect(partial(self.save_group_properties, group, line_edits))
        
    def load_properties_input(self, properties: dict):
        line_edits: dict = {}
        i = 0
        for key, value in properties.items():
            color = self.main_window.create_alternate_line_color(i)
            i += 1
            label: QtWidgets.QLabel = UiWidgetCreator.create_input_label(key, color)
            
            widget: QtWidgets.QWidget = UiWidgetCreator.create_input_field_widget(color)
            self.porp_label.layout().addWidget(label)
            regex_validator = ".*"
            if key == "vaccination rate" or key == "max vaccination rate":
                regex_validator = "^0(\.\d+)?$|^1(\.0+)?$"
            elif key == "color":
                line_edit, color_button = UiWidgetCreator.create_qcolor_button(color, value)
                label.mousePressEvent = partial(UiWidgetCreator.label_clicked, color_button, True)
                widget.mousePressEvent = partial(UiWidgetCreator.label_clicked, color_button, True)
                line_edits[key] = line_edit
                widget.layout().addWidget(color_button)
                self.prop_input.layout().addWidget(widget)
                continue
            elif key != "name":
                regex_validator = "^(?!10000001$)[0-9]{1,8}$"# Only allows numbers that are below 10 Million
            line_edit: QtWidgets.QLineEdit = UiWidgetCreator.create_input_line_edit(value, regex_validator, color)
            widget.mousePressEvent = partial(UiWidgetCreator.label_clicked, line_edit, False)
            label.mousePressEvent = partial(UiWidgetCreator.label_clicked, line_edit, False)
            line_edits[key] = line_edit
            widget.layout().addWidget(line_edit)
            self.prop_input.layout().addWidget(widget)
        return line_edits
    def save_group_properties(self, group: Union[NodeGroup, None], line_edits: dict):
        update_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        if update_dict["average intra group edges"] < update_dict["delta intra group edges"]:
            UiWidgetCreator.show_message(self.save_status, "Delta has to be smaller than average.", "error_message", True, is_row=False)
        if any(value == "" for value in update_dict.values()):
            UiWidgetCreator.show_message(self.save_status, "Please fill out every input.", "error_message", True, is_row=False)
            return
        if not group:
            group = self.parent.change_network(self.network, ADD_ACTION, group, update_dict)
            if not group:
                return # Should not happen
            success_message = "Successfully created."
        else:
            group = self.parent.change_network(self.network, UPDATE_ACTION, group, update_dict)
            success_message = "Successfully saved."
        self.is_creating_group = False
        self.unload()
        self.load_groups()
        self.parent.network_changed.emit()
        self.group_buttons[group.id].click()
        UiWidgetCreator.show_message(self.save_status, success_message, "success_message", True, is_row=False, content_of_last_label="color")
        
        
    def create_new_group(self):
        self.main_window.deselect_other_buttons("-1", self.group_buttons)
        if self.is_creating_group:
            return
        self.unload_group_properties()
        self.is_creating_group = True
        
        default_dict = {
            "name": "NodeGroup",
            "color": "",
            "member count": 100,
            "average intra group edges": 4,
            "delta intra group edges": 2,
            "age": 25,
            "vaccination rate": 0.5,
            "max vaccination rate": 0.7
        }
        self.show_group_properties(default_properties=default_dict)
        
        
        
        
    def unload_group_list(self):
        self.group_buttons.clear()
        self.main_window.unload_items_from_layout(self.group_list.layout())
        # self.parent.connection_edit.unload()
           
    def unload_group_properties(self):
        self.save_group_prop_button.hide()
        self.main_window.unload_items_from_layout(self.porp_label.layout())
        self.main_window.unload_items_from_layout(self.prop_input.layout())

        self.parent.connection_edit.unload()
            
    def unload(self):
        self.is_creating_group = False
        self.main_window.deselect_other_buttons("None", self.group_buttons)
        self.unload_group_list()
        self.unload_group_properties()