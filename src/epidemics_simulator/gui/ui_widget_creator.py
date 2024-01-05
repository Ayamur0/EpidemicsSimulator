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
        
    def show_message(widget, label_text, object_name, remove_last_message: bool, is_row=True):
        if remove_last_message:
            if  widget.layout():
                last_item =  widget.layout().itemAt(widget.layout().count() - 1).widget()
                if isinstance(last_item, QtWidgets.QLabel):
                    last_item.deleteLater()
        label = UiWidgetCreator.create_label(label_text, object_name)
        if is_row:
            widget.layout().addRow(label)
        else:
            widget.layout().addWidget(label)
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
            color_string = UiWidgetCreator.convert_color_to_float_rgb_string(color)
            hex_color = color.name()
            line_edit.setText(color_string)
            color_button.setStyleSheet(f'background: {hex_color};')
    
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
    
    def create_file_system_model():
        model = QtWidgets.QFileSystemModel()
        model.setRootPath("")
        model.setNameFilters(["*.json"])
        model.setNameFilterDisables(False)
        return model
    
    def create_file(window):     
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog  # Use the Qt dialog instead of the native one on some platforms

        # Add a filter to allow only JSON files
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(window, "Save File", "", "Json Files (*.json);;All Files (*)", options=options)
        
        # Check if the selected file has a JSON extension, if not, add it
        if file_name and not file_name.endswith('.json'):
            file_name += '.json'
        
        return file_name

    def open_file(window):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog  # Use the Qt dialog instead of the native one on some platforms

        # Add a filter to allow only JSON files
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(window, "Open File", "", "Json Files (*.json);;All Files (*)", options=options)
        
        return file_name

    def create_color_button(label_content, form_widget, color_value=None):
        label = UiWidgetCreator.create_label(label_content, 'disease_label_properties')
        if color_value:
            color_value_object = UiWidgetCreator.rgb_string_to_qcolor(color_value)
            print(color_value)
            color = UiWidgetCreator.convert_color_to_int_rgb_string(color_value_object)
        else:
            color_value_object = UiWidgetCreator.generate_random_color()
            color = UiWidgetCreator.convert_color_to_int_rgb_string(color_value_object)
        float_color = UiWidgetCreator.convert_color_to_float_rgb_string(color_value_object)
        color_button = UiWidgetCreator.create_push_button(None, 'color_button', style_sheet=f'background: {color};')
        color_button.clicked.connect(lambda: UiWidgetCreator.show_color_dialog(line_edit, color_button))
        regex_validator = '^rgb\((0(\.\d+)?|1(\.0+)?|0\.\d+|0)\s*,\s*(0(\.\d+)?|1(\.0+)?|0\.\d+|0)\s*,\s*(0(\.\d+)?|1(\.0+)?|0\.\d+|0)\)$'
        line_edit = UiWidgetCreator.create_line_edit(float_color, 'group_line_edit_properties', regex_validator=regex_validator)
        form_widget.layout().addRow(label, color_button)
        return label, line_edit, 

    def convert_color_to_float_rgb_string(color: QColor):
        red = color.red() / 255.0
        green = color.green() / 255.0
        blue = color.blue() / 255.0
        return f'rgb({red:.2f}, {green:.2f}, {blue:.2f})'
    
    def convert_color_to_int_rgb_string(color: QColor):
        red = color.red()
        green = color.green()
        blue = color.blue()
        return f'rgb({red}, {green}, {blue})'
    
    def rgb_string_to_qcolor(rgb_string):
        # Extracting the RGB values from the string
        rgb_values = [float(value) for value in rgb_string[4:-1].split(',')]
        
        # Converting float values to integers (0-255 range)
        rgb_int_values = [int(value * 255) for value in rgb_values]

        
        # Creating a QColor object
        color = QColor(*rgb_int_values)
        
        return color
    
    def create_qframe(object_name, layout: QtWidgets.QBoxLayout):
        frame = QtWidgets.QFrame()
        frame.setObjectName(object_name)
        frame.setLayout(layout)
        frame.layout().setStretch(0, 1)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        return frame
    
    def create_qscroll_area(object_name):
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setObjectName(object_name)

        return scroll_area