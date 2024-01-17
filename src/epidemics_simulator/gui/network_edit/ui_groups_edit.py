from PyQt5 import QtWidgets
import random
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Project
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor

#class GroupsCheckBox(QtWidgets.QCheckBox):
#    def __init__(self, selected_icon: QIcon, deselct_icon: QIcon, checked=False, parent=None):
#        super(GroupsCheckBox, self).__init__(parent)
#        self.selected_icon = selected_icon
#        self.deselct_icon = deselct_icon
#        if checked:
#            self.icon = self.selected_icon
#        else:
#            self.icon = self.deselct_icon
#        
#    def updateIcon(self, state):
#        if state == Qt.Checked:
#            self.setIcon(self.selected_icon)
#        else:
#            self.setIcon(self.deselected_icon)


class UiGroupEdit:
    def __init__(self, main_window: QtWidgets.QMainWindow, connection_edit):
        self.main_window = main_window
        self.connection_edit = connection_edit
        
        self.new_group_button = self.main_window.new_group_btn
        self.save_group_prop_button = self.main_window.save_properties_btn
        
        self.group_list = self.main_window.group_list_content
        self.group_prop = self.main_window.group_properties_content
        # self.group_prop.layout().setSpacing(0)
        self.group_list.layout().setAlignment(Qt.AlignTop)
        #self.group_prop.layout().setLabelAlignment(Qt.AlignRight)
        # self.group_prop.layout().setFormAlignment(Qt.AlignRight)
        
        self.new_group_button.clicked.connect(lambda: self.create_new_group())
        
        self.save_status = self.main_window.save_status
        self.save_status.layout().setAlignment(Qt.AlignCenter)
        
        self.porp_label = self.main_window.prop_label
        self.porp_label.layout().setAlignment(Qt.AlignTop)
        self.prop_input = self.main_window.prop_input
        self.prop_input.layout().setAlignment(Qt.AlignTop)
        
        self.group_buttons: dict = {}
        
        self.is_creating_group = False
    
                
        self.new_group_button.setText(None)
        self.save_group_prop_button.setText(None)
        self.new_group_button.setIcon(self.main_window.add_icon)
        self.save_group_prop_button.setIcon(self.main_window.save_icon)

    def init_ui(self, network: Network):
        self.network = network
        self.save_group_prop_button.hide()
        self.load_groups(self.network)
        
    def load_groups(self, network: Network):
        self.group_buttons['-1'] = self.new_group_button
        for group in network.groups:
            self.load_group_button(group)
            
    def load_group_button(self, group: NodeGroup):
        layout_widget = UiWidgetCreator.create_qwidget('group_select', QtWidgets.QHBoxLayout)
        layout_widget.layout().setAlignment(Qt.AlignCenter)
        
        checkbox = UiWidgetCreator.create_qcheckbox('activity_checkbox', group.active)
        duplicate_button = UiWidgetCreator.create_qpush_button(None, 'duplicate_button')
        duplicate_button.setIcon(self.main_window.duplicate_icon)
        
        remove_button = UiWidgetCreator.create_qpush_button(None, 'delete_button')
        remove_button.setIcon(self.main_window.remove_icon)
        group_button = UiWidgetCreator.create_qpush_button(None, 'select_button', is_checkable=True)
        group_button.setIcon(self.main_window.edit_icon)
        checkbox.stateChanged.connect(partial(self.set_group_activity, checkbox, group))
        duplicate_button.clicked.connect(partial(self.dupliacte_group, group))
        remove_button.clicked.connect(partial(self.remove_group, group))
        group_label = UiWidgetCreator.create_qlabel(group.name, 'group')
        
        group_button.clicked.connect(partial(self.show_group_properties, group))
        group_button.clicked.connect(partial(self.connection_edit.load_connections, self.network, group))
        
        #layout_widget.setStyleSheet('background-color: lightblue;')
        self.group_buttons[group.id] = group_button
        
        layout_widget.layout().addWidget(checkbox)
        layout_widget.layout().addWidget(duplicate_button)
        layout_widget.layout().addWidget(remove_button)
        layout_widget.layout().addWidget(group_label)
        layout_widget.layout().addWidget(group_button)
        self.group_list.layout().addWidget(layout_widget)
        
    def set_group_activity(self, checkbox: QtWidgets.QCheckBox, group: NodeGroup):
        group.active = checkbox.isChecked()
        self.main_window.network_changed.emit()
        
    def dupliacte_group(self, group: NodeGroup):
        #new_group = NodeGroup.from_dict(group.to_dict(), network) not usable because the id would not change
        new_group = NodeGroup(self.network, group.name, group.size, group.age, group.vaccination_rate, group.max_vaccination_rate, group.avrg_int_con, group.delta_int_con, group.color)
        self.network.add_group(new_group)
        for ext_group, value in group.avrg_ext_con.items():
            new_group.add_external_connection(ext_group, value, group.delta_ext_con[ext_group])
        self.unload()
        self.load_groups(self.network)
        self.group_buttons[new_group.id].click()
        self.main_window.network_changed.emit()
        
    def remove_group(self, group: NodeGroup):
        message = UiWidgetCreator.show_message(f'Are you sure you want to delete group {group.name}', 'Group deleting')
        result = message.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return
        self.network.delete_group(group.id)
        self.unload()
        self.load_groups(self.network)
        self.main_window.network_changed.emit()
        
            
    def show_group_properties(self, group: NodeGroup=None, default_properties: dict=None):
        self.unload_group_properties()
        if group:
            self.is_creating_group = False
            self.main_window.deselect_other_buttons(group.id, self.group_buttons)
            properties = group.get_properties_dict()
        else:
            self.main_window.deselect_other_buttons('-1', self.group_buttons)
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
            if i % 2 == 0:
                color = 'rgb(65, 65, 65)'
            else:
                color = 'rgb(80, 80, 80)'
            i += 1
            label = UiWidgetCreator.create_input_label(key, color)
            
            widget = UiWidgetCreator.create_input_field_widget(color)
            self.porp_label.layout().addWidget(label)
            regex_validator = '.*'
            if key == 'vaccination rate' or key == 'max vaccination rate':
                regex_validator = '^0(\.\d+)?$|^1(\.0+)?$'
            elif key == 'color':
                line_edit, color_button = UiWidgetCreator.create_qcolor_button(color, value)
                line_edits[key] = line_edit
                # line_edit.setStyleSheet(f'border-radius: 20px;background: {color};')
                # color_button.setStyleSheet(f'background: {color};border-radius: 0;')
                # color_button.layout().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                # color_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed) 
                # color_button.setMinimumSize(100, 35)
                widget.layout().addWidget(color_button)
                self.prop_input.layout().addWidget(widget)
                #self.prop_input.layout().addWidget(color_widget)
                #self.group_prop.layout().addRow(label, color_button)
                continue
            elif key != 'name':
                regex_validator = '^(?!10000001$)[0-9]{1,8}$ '# Only allows numbers that are below 10 Million
            #line_edit = UiWidgetCreator.create_qline_edit(value, 'group_line_edit_properties', regex_validator=regex_validator)
            line_edit = UiWidgetCreator.create_input_line_edit(value, regex_validator, color)
            line_edits[key] = line_edit
            widget.layout().addWidget(line_edit)
            #line_edit.setMinimumSize(100, 35)
            #line_edit.setStyleSheet(f'border-radius: 5px;background: rgb(40, 40, 40);')
            #line_edit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            #line_edit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed) 
            self.prop_input.layout().addWidget(widget)
            #self.prop_input.layout().addWidget(line_edit)
            #self.group_prop.layout().addRow(label, line_edit)
        return line_edits
    
    def save_group_properties(self, group: NodeGroup, line_edits: dict):
        update_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        if not group:
            try:
                group = NodeGroup.init_from_dict(self.network, update_dict)
                self.network.add_group(group)
            except ValueError as e:
                if str(e) == "Delta has to be smalller then average":
                    UiWidgetCreator.show_status(self.save_status, str(e), 'error_message', True, is_row=False)
                else:
                    UiWidgetCreator.show_status(self.save_status, "Pleas fill out every input", 'error_message', True, is_row=False)
                return
            success_message = "Successfully added"
        else:
            try:
                group.set_from_dict(update_dict)
            except ValueError as e:
                if str(e) == "Delta has to be smalller then average":
                    UiWidgetCreator.show_status(self.save_status, str(e), 'error_message', True, is_row=False, content_of_last_label='color')
                else:
                    UiWidgetCreator.show_status(self.save_status, "Pleas fill out every input", 'error_message', True, is_row=False, content_of_last_label='color')
                return
            success_message = "Successfully saved"
        self.is_creating_group = False
        self.unload()
        self.load_groups(self.network)
        self.main_window.network_changed.emit()
        self.group_buttons[group.id].click()
        UiWidgetCreator.show_status(self.save_status, success_message, "success_message", True, is_row=False, content_of_last_label='color')
        
    def create_new_group(self):
        self.main_window.deselect_other_buttons('-1', self.group_buttons)
        if self.is_creating_group:
            return
        self.unload_group_properties()
        self.is_creating_group = True
        
        default_dict = {
            "name": 'NodeGroup',
            "color": '',
            "member count": 100,
            "average internal connections": 4,
            "internal connection delta": 2,
            "age": 25,
            "vaccination rate": 0.5,
            "max vaccination rate": 0.7
        }
        self.show_group_properties(default_properties=default_dict)
        
        
    def unload_group_list(self):
        self.group_buttons.clear()
        self.main_window.unload_items_from_layout(self.group_list.layout())
        self.connection_edit.unload()
           
    def unload_group_properties(self):
        self.save_group_prop_button.hide()
        self.main_window.unload_items_from_layout(self.porp_label.layout())
        self.main_window.unload_items_from_layout(self.prop_input.layout())
        
        # self.main_window.unload_items_from_layout(self.group_prop.layout())
        self.connection_edit.unload()
            
    def unload(self):
        self.is_creating_group = False
        self.main_window.deselect_other_buttons('None', self.group_buttons)
        self.unload_group_list()
        self.unload_group_properties()
        
    def change_icon_theme(self, new_theme):
        for button in self.group_list.findChildren(QtWidgets.QPushButton):
            icon = button.icon()
            if icon.isNull():
                continue
            