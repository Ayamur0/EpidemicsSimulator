from functools import partial
from src.epidemics_simulator.storage import Network, Project
from src.epidemics_simulator.gui.templates import templates
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject
from storage import Network
import random
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRegExp, QTimer, QThread, QSize
from PyQt5.QtGui import QRegExpValidator, QColor, QMovie


class UiWidgetCreator:
    def create_qwidget(object_name: str, layout: QtWidgets.QBoxLayout, style_sheet=None) -> QtWidgets.QWidget:
        layout_widget = QtWidgets.QWidget()
        layout_widget.setObjectName(object_name)
        layout_widget.setLayout(layout())
        if style_sheet:
            layout_widget.setStyleSheet(style_sheet)
        return layout_widget
    
    def create_qcheckbox(object_name: str, is_checked: bool, style_sheet=None)-> QtWidgets.QCheckBox:
        checkbox = QtWidgets.QCheckBox()
        checkbox.setObjectName(object_name)
        checkbox.setChecked(is_checked)
        
        if style_sheet:
            checkbox.setStyleSheet(style_sheet)
        return checkbox
    
    def create_qaction(content: str, object_name: str, parent: QObject) -> QtWidgets.QAction:
        action = QtWidgets.QAction(content, parent)
        action.setObjectName(object_name)
        return action
    
    def create_qpush_button(content: str, object_name: str, is_checkable: bool=False, is_checked: bool=False, style_sheet: str=None) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton()
        button.setObjectName(object_name)
        button.setText(content)
        button.setCheckable(is_checkable)

        if is_checkable:
            button.setChecked(is_checked)
        if style_sheet:
            button.setStyleSheet(style_sheet)
        return button
    
    def create_qlabel(content: str, object_name: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel()
        label.setObjectName(object_name)
        label.setText(str(content))
        return label
    
    def create_qline_edit(content: str, object_name: str, regex_validator = '.*', style_sheet=None) -> QtWidgets.QLineEdit:
        line_edit = QtWidgets.QLineEdit()
        line_edit.setObjectName(object_name)
        reg_ex = QRegExp(regex_validator)
        input_validator = QRegExpValidator(reg_ex, line_edit)
        line_edit.setValidator(input_validator)
        line_edit.setText(str(content))
        if style_sheet:
            line_edit.setStyleSheet(style_sheet)
        return line_edit
    
    def create_qframe(object_name, layout: QtWidgets.QBoxLayout) -> QtWidgets.QFrame:
        frame = QtWidgets.QFrame()
        frame.setObjectName(object_name)
        frame.setLayout(layout())
        frame.layout().setStretch(0, 1)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        return frame
    
    def create_qcolor_button(color_value=None, content: str = None, widget: QObject = None) -> tuple[QtWidgets.QLineEdit, QtWidgets.QPushButton]:
        if color_value:
            color_value_object = UiWidgetCreator.rgb_string_to_qcolor(color_value)
            color = UiWidgetCreator.convert_color_to_int_rgb_string(color_value_object)
        else:
            color_value_object = UiWidgetCreator.generate_random_color()
            color = UiWidgetCreator.convert_color_to_int_rgb_string(color_value_object)
        regex_validator = '^rgb\((0(\.\d+)?|1(\.0+)?|0\.\d+|0)\s*,\s*(0(\.\d+)?|1(\.0+)?|0\.\d+|0)\s*,\s*(0(\.\d+)?|1(\.0+)?|0\.\d+|0)\)$'
        float_color = UiWidgetCreator.convert_color_to_float_rgb_string(color_value_object)
        line_edit = UiWidgetCreator.create_qline_edit(float_color, 'group_line_edit_properties', regex_validator=regex_validator)
        
        color_button = UiWidgetCreator.create_qpush_button(None, 'color_button', style_sheet=f'background: {color};')
        color_button.clicked.connect(partial(UiWidgetCreator.show_color_dialog, line_edit, color_button))
        
        if content and widget:
            label = UiWidgetCreator.create_qlabel(content, 'color_input_label')
            widget.layout().addRow(label, color_button)
        
        return line_edit, color_button
    
    def show_color_dialog(line_edit, color_button) -> None:
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            color_string = UiWidgetCreator.convert_color_to_float_rgb_string(color)
            hex_color = color.name()
            line_edit.setText(color_string)
            color_button.setStyleSheet(f'background: {hex_color};')
            
    def generate_random_color() -> QColor:
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        return QColor(red, green, blue)
    
    def convert_color_to_float_rgb_string(color: QColor) -> str:
        red = color.red() / 255.0
        green = color.green() / 255.0
        blue = color.blue() / 255.0
        return f'rgb({red:.2f}, {green:.2f}, {blue:.2f})'
    
    def convert_color_to_int_rgb_string(color: QColor) -> str:
        red = color.red()
        green = color.green()
        blue = color.blue()
        return f'rgb({red}, {green}, {blue})'
    
    def rgb_string_to_qcolor(rgb_string) -> QColor:
        rgb_values = [float(value) for value in rgb_string[4:-1].split(',')]
        rgb_int_values = [int(value * 255) for value in rgb_values]
        color = QColor(*rgb_int_values)
        return color
    
    def hide_message(label: QtWidgets.QLabel, timer: QTimer) -> None:
        try:
            label.deleteLater()
            timer.deleteLater()  # Delete the timer to avoid memory leaks
        except RuntimeError:
            return
        
    def show_status(widget, content: str, object_name: str, remove_last_message: bool, is_row=True) -> None:
        if remove_last_message:
            if  widget.layout():
                last_item =  widget.layout().itemAt(widget.layout().count() - 1).widget()
                if isinstance(last_item, QtWidgets.QLabel):
                    last_item.deleteLater()
        label = UiWidgetCreator.create_qlabel(content, object_name)
        if is_row:
            widget.layout().addRow(label)
        else:
            widget.layout().addWidget(label)
        timer = QTimer()
        timer.singleShot(2000, lambda: UiWidgetCreator.hide_message(label, timer))
    
    def show_message(content: str, title: str, default_button=1) -> QtWidgets.QMessageBox:
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(content)
        
        
        yes_button = msg_box.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
        cancel_button = msg_box.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)
        
        if default_button == 0:
            msg_box.setDefaultButton(yes_button)
        elif default_button == 1:
            msg_box.setDefaultButton(cancel_button)
        
        return msg_box
    def save_popup(content: str):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setWindowTitle('Unsaved Changes Detected')
        msg_box.setText('Do you want to save your changes before closing?')

        save_button = msg_box.addButton('Save',QtWidgets.QMessageBox.AcceptRole)
        no_button = msg_box.addButton('No',QtWidgets.QMessageBox.RejectRole)
        cancel_button = msg_box.addButton('Cancel',QtWidgets.QMessageBox.RejectRole)

        msg_box.exec_()

        if msg_box.clickedButton() == save_button:
            return QtWidgets.QMessageBox.Save
        elif msg_box.clickedButton() == no_button:
            return QtWidgets.QMessageBox.No
        else:  # msg_box.clickedButton() == cancel_button
            return QtWidgets.QMessageBox.Cancel
    
    def create_file_system_model() -> QtWidgets.QFileSystemModel:
        model = QtWidgets.QFileSystemModel()
        model.setRootPath("")
        model.setNameFilters(["*.json"])
        model.setNameFilterDisables(False)
        return model
    
    def create_file(window) -> str:     
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog  # Use the Qt dialog instead of the native one on some platforms

        # Add a filter to allow only JSON files
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(window, "Save File", "", "Json Files (*.json);;All Files (*)", options=options)
        
        # Check if the selected file has a JSON extension, if not, add it
        if file_name and not file_name.endswith('.json'):
            file_name += '.json'
        
        return file_name

    def open_file(window) -> str:
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog  # Use the Qt dialog instead of the native one on some platforms

        # Add a filter to allow only JSON files
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(window, "Open File", "", "Json Files (*.json);;All Files (*)", options=options)
        
        return file_name
    
    def create_generate_popup(parent) -> QtWidgets.QDialog:
        dialog = QtWidgets.QDialog(parent, flags=Qt.FramelessWindowHint)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setObjectName('generate_popup')
        dialog.setLayout(QtWidgets.QHBoxLayout())
        # Asset source: https://gifer.com/en/ZKZg
        loading = QMovie('assets/loading.gif')
        loading.setScaledSize(QSize(35, 35))
        loading_label = QtWidgets.QLabel()
        loading_label.setMovie(loading)
        loading.start()
        #loading_label.setFixedSize(50, 50)
        
        text_label = UiWidgetCreator.create_qlabel('Generating...', 'generating_label')
        dialog.layout().addWidget(loading_label)
        dialog.layout().addWidget(text_label)
        
        return dialog
    
    
    def move_grid_widgets_right(grid: QtWidgets.QLayout , starting_pos, row_size,  ) -> None:
        total_widgets = grid.count()
        for i in range(total_widgets - 1, -1 + starting_pos, -1):
            row, col, _, _ = grid.getItemPosition(i)
            if col == row_size - 1:
                row += 1
                col = 0
            else:
                col += 1
            grid.layout().addWidget(grid.layout().itemAt(i).widget(), row, col)
            
    def move_grid_widgets_left(grid: QtWidgets.QLayout, starting_pos, row_size) -> None:
        starting_row = int(starting_pos / row_size)
        starting_col = starting_pos % row_size
        
        print(f'Row: {starting_row}, Col: {starting_col}')
        
        for row in range(starting_row, grid.rowCount()):
        # Iterate through the columns
            for col in range(starting_col, row_size - 1):
                current_index = row * row_size + col
                
                current_widget = grid.itemAt(current_index)
                next_widget = grid.itemAt(current_index + 1)
                
                
                
                if current_widget and next_widget:
                    grid.addWidget(current_widget.widget(), row, col)
                    grid.addWidget(next_widget.widget(), row, col + 1)
        # Clear the last column in the last row
        last_index = grid.rowCount() * row_size - 1
        last_widget = grid.itemAt(last_index)

        if last_widget:
            last_widget.widget().setParent(None)
                        
    def pop_grid_widget_at(grid: QtWidgets.QLayout, index) -> None:
        if index < 0: 
            return
        elif index >= grid.count():
            return
        item = grid.itemAt(index)
        if item is None:
            return

        widget = item.widget()
        if widget is None:
            return
        grid.removeItem(item)
        widget.setParent(None)
        widget.deleteLater()



    def ask_for_regeneration(network: Network, button_for_generating: QtWidgets.QPushButton):
        if len(network.groups) == 0:
            return False
        msg_box  = UiWidgetCreator.show_message(f'Network has not been generated. Do you want to generate the network', 'Regenerate network', default_button=0)
        result = msg_box.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return False
        button_for_generating.click()
        return True