import random
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5.QtCore import QRegExp, QTimer
from PyQt5.QtGui import QRegExpValidator, QColor
from src.epidemics_simulator.gui.cutsom_widgets import *

class UiWidgetCreator:
    def create_label(content: str, object_name: str, style_sheet=None):
        #label = DefaultLabel()
        label = QtWidgets.QLabel()
        label.setObjectName(object_name)
        label.setText(str(content))
        return label
    
    def create_push_button(content: str, object_name: str, is_checkable=False, is_checked=False, style_sheet=None):
        #button = DefaultButton()
        button = QtWidgets.QPushButton()
        button.setObjectName(object_name)
        button.setText(content)
        button.setCheckable(is_checkable)
        if is_checkable:
            button.setChecked(is_checked)
        if style_sheet:
            button.setStyleSheet(style_sheet)
        return button
        
        
    def create_checkbox(object_name: str, is_checked: bool, style_sheet=None):
        checkbox = QtWidgets.QCheckBox()
        checkbox.setObjectName(object_name)
        checkbox.setChecked(is_checked)
        if style_sheet:
            checkbox.setStyleSheet(style_sheet)
        return checkbox
    
    def create_line_edit(content: str, object_name: str, regex_validator = '.*', style_sheet=None):
        #line_edit = DefaultLineEdit()
        line_edit = QtWidgets.QLineEdit()
        line_edit.setObjectName(object_name)
        reg_ex = QRegExp(regex_validator)
        input_validator = QRegExpValidator(reg_ex, line_edit)
        line_edit.setValidator(input_validator)
        line_edit.setText(str(content))
        if style_sheet:
            line_edit.setStyleSheet(style_sheet)
        return line_edit
    
    def create_layout_widget(object_name: str, layout: QtWidgets.QBoxLayout, style_sheet=None):
        layout_widget = QtWidgets.QWidget()
        layout_widget.setObjectName(object_name)
        layout_widget.setLayout(layout)
        #layout_widget.setLayout(QtWidgets.QHBoxLayout())
        if style_sheet:
            layout_widget.setStyleSheet(style_sheet)
        return layout_widget
    
    def hide_message(label, timer):
        try:
            label.deleteLater()
            timer.deleteLater()  # Delete the timer to avoid memory leaks
        except RuntimeError:
            return
        
    def show_message(widget, label_text, object_name, remove_last_message: bool):
        if remove_last_message:
            last_item =  widget.layout().itemAt(widget.layout().count() - 1).widget()
            if isinstance(last_item, QtWidgets.QLabel):
                last_item.deleteLater()
        label = UiWidgetCreator.create_label(label_text, object_name)
        widget.layout().addRow(label)
        timer = QTimer()
        timer.singleShot(2000, lambda: UiWidgetCreator.hide_message(label, timer))
        
    def generate_random_color():
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        return QColor(red, green, blue)
        
    def show_color_dialog(line_edit, color_button):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            hex_color = color.name()
            line_edit.setText(hex_color)
            color_button.setStyleSheet(f'background: {hex_color};')
    
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
    
    def create_delete_dialog(content: str):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setWindowTitle('Delete Confirmation')
        msg_box.setText(content)
        
        
        yes_button = msg_box.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
        cancel_button = msg_box.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)
        
        msg_box.setDefaultButton(cancel_button)
        
        return msg_box
    
    def move_grid_widgets_right(grid, starting_pos, row_size):
        total_widgets = grid.layout().count()
        for i in range(total_widgets - 1, -1 + starting_pos, -1):
            row, col, _, _ = grid.layout().getItemPosition(i)
            if col == row_size - 1:
                row += 1
                col = 0
            else:
                col += 1
            grid.layout().addWidget(grid.layout().itemAt(i).widget(), row, col)
            
    def pop_grid_widget_at(grid, index):
        total_widgets = grid.layout().count()
        for i in range(index, total_widgets - 2):
            grid.layout().addWidget(grid.layout().getItemPosition(i + 1))
            
    def create_qaction(content, object_name, window):
        action = QtWidgets.QAction(content, window)
        action.setObjectName(object_name)
        return action