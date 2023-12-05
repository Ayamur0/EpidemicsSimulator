from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
import sys
from storage import Network, NodeGroup
from functools import partial


class UiNetworkEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        self.group_buttons: dict = {}
        self.connection_buttons: dict = {}
        self.show()

    def load_groups(self, network: Network):
        all_groups = network.groups
        for group in all_groups:
            self.add_group(group)
        v_layout = self._create_hbox_layout_widget("group_list_entry")
        btn = QtWidgets.QPushButton('+')
        btn.setObjectName("add_group_btn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.create_new_group_input())
        v_layout.layout().addWidget(btn)
        self.group_buttons['-1'] = btn
        self.group_list_layout.addWidget(v_layout)
        
    def create_new_group_input(self):
        self.unload_items_from_layout(self.group_properties_content.layout())
        self.unload_items_from_layout(self.connection_properties_content.layout())
        self.deselect_other_group_buttons('-1', self.group_buttons)
        default_dict = {
            "name": '',
            "member count": '',
            "average internal connections": '',
            "internal connection delta": '',
            "age": '',
            "vaccination rate": '',
        }
        line_edits = self._create_group_prop_input(default_dict)
        btn = QtWidgets.QPushButton('Save')
        btn.setObjectName("save_group_btn")
        btn.clicked.connect(lambda: self.create_new_group(line_edits))
        self.group_properties_content.layout().addRow(btn)
    
    def create_new_group(self, line_edits):
        pass
        
    def save_input(self, line_edits, ext_con_change=False):
        pass
        print(line_edits)
        test = line_edits.items()
        print(test)

        
        
    def deselect_other_group_buttons(self, sender_id, button_dict):
        for button in button_dict:
            btn_object = button_dict[button]
            if button == sender_id: # So it is not possible to deleselct the same button
                btn_object.setChecked(True)
                continue
            if not btn_object.isChecked():
                continue
            btn_object.setChecked(False)
            
    def _create_hbox_layout_widget(self, widget_name):
        v_layout = QtWidgets.QWidget()
        v_layout.setObjectName(widget_name)
        v_layout.setLayout(QtWidgets.QHBoxLayout())
        return v_layout
            
    def unload_items_from_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
               
    def add_group(self, group: NodeGroup):
        v_layout = self._create_hbox_layout_widget("group_list_entry")
        checkbox = QtWidgets.QCheckBox()
        checkbox.setChecked(True)
        btn = QtWidgets.QPushButton(group.name)
        btn.setObjectName("group_list_btn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.load_properties(group))
        self.group_buttons[group.id] = btn
        v_layout.layout().addWidget(checkbox)
        v_layout.layout().addWidget(btn)
        self.group_list_layout.addWidget(v_layout)
        
    def load_properties(self, group: NodeGroup):
        self.unload_items_from_layout(self.group_properties_content.layout())
        self.unload_items_from_layout(self.connection_properties_content.layout())
        
        self.deselect_other_group_buttons(group.id, self.group_buttons)
        
        properties = group.get_properties_dict()
        
        
        line_edits = self._create_group_prop_input(properties)
        
        btn = QtWidgets.QPushButton('Save')
        btn.setObjectName("save_group_btn")
        btn.clicked.connect(lambda: self.save_input(line_edits))
        self.group_properties_content.layout().addRow(btn)
        self.load_connections(group)
        
    def _create_group_prop_input(self, properties):
        line_edits = {}
        for p, v in properties.items():
            label = QtWidgets.QLabel(p)
            label.setObjectName("group_label_properties")
            line_edit = QtWidgets.QLineEdit()
            if p == 'vaccination rate':
                reg_ex = QRegExp("^\d+(\.\d+)?$")
                input_validator = QRegExpValidator(reg_ex, line_edit)
                line_edit.setValidator(input_validator)
            elif p != 'name':
                reg_ex = QRegExp("^[0-9]+$")
                input_validator = QRegExpValidator(reg_ex, line_edit)
                line_edit.setValidator(input_validator)
            
                
            line_edit.setObjectName("group_line_edit_properties")
            line_edit.setText(str(v))
            self.group_properties_content.layout().addRow(label, line_edit)
            line_edits[p] = line_edit
        return line_edits
        
            
    def load_connections(self, group: NodeGroup):
        self.unload_items_from_layout(self.con_list_layout)
        
        other_groups = [g for g in group.network.groups if g.id != group.id]
        
        self.connection_buttons.clear()
        
        for g in other_groups:
            v_layout = self._create_hbox_layout_widget("connection_list_entry")
            btn = QtWidgets.QPushButton(g.name)
            btn.setObjectName("connection_list_btn")
            self.connection_buttons[g.id] = btn
            btn.setCheckable(True)
            btn.clicked.connect(partial(self.load_connection_properties, group, g.id))
            
            v_layout.layout().addWidget(btn) 
            self.con_list_layout.addWidget(v_layout)
            
            
    def load_connection_properties(self, group_from: NodeGroup, group_to: str):
        self.unload_items_from_layout(self.connection_properties_content.layout())
        
        self.deselect_other_group_buttons(group_to, self.connection_buttons)
        
        line_edits = {}
        
        for p, v in [
            ("connection average", group_from.avrg_ext_con.get(group_to, 0)),
            ("connection delta", group_from.delta_ext_con.get(group_to, 0)),
        ]:
            label = QtWidgets.QLabel(p)
            label.setObjectName("connection_label_properties")
            line_edit = QtWidgets.QLineEdit()
            line_edit.setObjectName("connection_line_edit_properties")
            line_edit.setText(str(v))
            reg_ex = QRegExp("^[0-9]+$")
            input_validator = QRegExpValidator(reg_ex, line_edit)
            line_edit.setValidator(input_validator)
            self.connection_properties_content.layout().addRow(label, line_edit)
            line_edits[p] = line_edit
        btn = QtWidgets.QPushButton('Save')
        btn.setObjectName("save_group_btn")
        btn.clicked.connect(lambda: self.save_input(line_edits, ext_con_change=True))
        self.connection_properties_content.layout().addRow(btn)