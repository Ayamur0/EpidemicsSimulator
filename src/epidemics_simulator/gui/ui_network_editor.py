import random
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QRegExp, QTimer, Qt
from PyQt5.QtGui import QRegExpValidator, QColor
import sys
from storage import Network, NodeGroup
from functools import partial


class UiNetworkEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        self.con_list_layout.setAlignment(Qt.AlignTop)
        self.group_buttons: dict = {}
        self.connection_buttons: dict = {}
        self.show()
        
    def hide_message(self, label, timer):
        try:
            label.deleteLater()
            timer.deleteLater()  # Delete the timer to avoid memory leaks
        except RuntimeError:
            return
        
    def show_message(self, widget, label_text, object_name):
        label = QtWidgets.QLabel(label_text)
        label.setObjectName(object_name)
        widget.layout().addRow(label)

        timer = QTimer()
        timer.singleShot(2000, lambda: self.hide_message(label, timer))
        
    #def fade(self, widget):
    #    effect = QtWidgets.QGraphicsOpacityEffect()
    #    widget.setGraphicsEffect(effect)
    #    animation = QPropertyAnimation(effect, b"opacity")
    #    animation.setDuration(1000)
    #    animation.setStartValue(1)
    #    animation.setEndValue(0)
    #    animation.start()

    #def unfade(self, widget):
    #    effect = QtWidgets.QGraphicsOpacityEffect()
    #    widget.setGraphicsEffect(effect)

    #    animation = QPropertyAnimation(effect, b"opacity")
    #    animation.setDuration(1000)
    #    animation.setStartValue(0)
    #    animation.setEndValue(1)
    #    animation.start()
        
    #def show_error(self, message):
    #    error_box = QtWidgets.QMessageBox(self)
    #    error_box.setIcon(QtWidgets.QMessageBox.Warning)
    #    error_box.setText(message)
    #    error_box.setWindowTitle('Validation Error')
    #    error_box.exec_()

    def load_groups(self, network: Network):
        all_groups = network.groups
        for group in all_groups:
            self.add_group(group)
        v_layout = self._create_hbox_layout_widget("group_list_entry")
        btn = QtWidgets.QPushButton('+')
        btn.setObjectName("add_group_btn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.create_new_group_input(network))
        v_layout.layout().addWidget(btn)
        self.group_buttons['-1'] = btn
        self.group_list_layout.addWidget(v_layout)
        
    def create_new_group_input(self, network: Network):
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
            "max vaccination rate": '',
            "color": ''
        }
        line_edits = self._create_group_prop_input(default_dict)
        btn = QtWidgets.QPushButton('Save')
        btn.setObjectName("save_group_btn")
        btn.clicked.connect(lambda: self.create_new_group(line_edits, network))
        self.group_properties_content.layout().addRow(btn)
    
    def create_new_group(self, line_edits, network: Network):
        try:
            name = line_edits['name'].text()
            size = int(line_edits['member count'].text())
            age = int(line_edits['age'].text())
            vaccination_rate = float(line_edits['vaccination rate'].text())
            aic = int(line_edits['average internal connections'].text())
            dic = int(line_edits['internal connection delta'].text())
            vac_rate = int(line_edits['max vaccination rate'].text())
            color = line_edits['color'].text()
        except ValueError:
            self.show_message(self.group_properties_content, "Pleas fill out every input", "error_message")
            return
        try:
            tmp_group = NodeGroup(network, name, size, age, vaccination_rate, vac_rate, aic, dic, color)
        except ValueError:
            self.show_message(self.group_properties_content, "Delta has to be smalller then average", "error_message")
            return
        self.error_incomplete_input = False
        self.error_delta = False
        self.unload_items_from_layout(self.group_properties_content.layout())
        self.unload_items_from_layout(self.group_list_layout)
        network.add_group(tmp_group)
        self.load_groups(network)
        self.deselect_other_group_buttons(tmp_group.id, self.group_buttons)
        self.load_properties(tmp_group) # might cause errors later 
        
    def save_con_input(self, line_edits, group:NodeGroup, target):
        try:
            con_avr = int(line_edits['connection average'].text())
            con_dc = int(line_edits['connection delta'].text())
            if con_dc > con_avr:
                raise ValueError
        except ValueError:
            self.show_message(self.connection_properties_content, "Invalid input", "error_message")
            return
        if not group.add_external_connection(target, con_avr, con_dc):
            group.delete_external_connection(target)
            group.add_external_connection(target, con_avr, con_dc)
        self.show_message(self.connection_properties_content, "Successfully saved", "success_message")
        
    def save_group_input(self, line_edits, group:NodeGroup):      
        try:
            name = line_edits['name'].text()
            size = int(line_edits['member count'].text())
            age = int(line_edits['age'].text())
            vaccination_rate = float(line_edits['vaccination rate'].text())
            aic = int(line_edits['average internal connections'].text())
            dic = int(line_edits['internal connection delta'].text())
            vac_rate = int(line_edits['max vaccination rate'].text())
            color = line_edits['color'].text()
            if dic > aic:
                raise ValueError
        except ValueError:
            self.show_message(self.group_properties_content, "Invalid input", "error_message")
            return
        group.name = name
        if size != group.size:
            group.members.clear()
            group.create_members(size)
        group.age = age
        group.vaccination_rate = vaccination_rate
        group.avrg_int_con = aic
        group.delta_int_con = dic
        group.max_vaccination_rate = vac_rate
        group.color = color
        self.show_message(self.group_properties_content, "Successfully saved", "success_message")
        
        
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
        self.error_incomplete_input = False
        self.error_delta = False
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
        btn.clicked.connect(lambda: self.save_group_input(line_edits, group))
        self.group_properties_content.layout().addRow(btn)
        self.load_connections(group)
        
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
            elif p == 'color':
                pick_color_button = QtWidgets.QPushButton()
                pick_color_button.setObjectName('color_button')
                pick_color_button.clicked.connect(lambda: self.show_color_dialog(line_edit, pick_color_button))
                line_edit.setText(str(v))
                if v == '':
                    line_edit.setText(self.generate_random_color().name())
                pick_color_button.setStyleSheet(f'background: {line_edit.text()};')
                
                line_edits[p] = line_edit
                self.group_properties_content.layout().addRow(label, pick_color_button)
                continue
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
            #v_layout = self._create_hbox_layout_widget("connection_list_entry")
            #v_layout.setFixedSize(QSize(100, 20))
            btn = QtWidgets.QPushButton(g.name)
            #v_layout.setStyleSheet('background: red;')
            btn.setObjectName("connection_list_btn")
            self.connection_buttons[g.id] = btn
            btn.setCheckable(True)
            btn.clicked.connect(partial(self.load_connection_properties, group, g.id))
            
            #v_layout.layout().addWidget(btn) 
            self.con_list_layout.addWidget(btn)
            
            
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
        btn.clicked.connect(lambda: self.save_con_input(line_edits, group_from, group_to))
        self.connection_properties_content.layout().addRow(btn)