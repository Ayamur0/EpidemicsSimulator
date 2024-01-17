from typing import Type, Union
from datetime import datetime
from functools import partial
from src.epidemics_simulator.storage import Network, Project
from src.epidemics_simulator.gui.templates import templates
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, QPoint, pyqtSignal, QRect
from storage import Network
import random
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRegExp, QTimer, QThread, QSize
from PyQt5.QtGui import QRegExpValidator, QColor, QMovie, QPainter, QFontMetrics, QTextLayout


class UiWidgetCreator:
    def create_qwidget(object_name: str, layout: QtWidgets.QBoxLayout, style_sheet=None) -> QtWidgets.QWidget:
        layout_widget = QtWidgets.QWidget()
        layout_widget.setObjectName(object_name)
        layout_widget.setLayout(layout())
        if style_sheet:
            layout_widget.setStyleSheet(style_sheet)
        return layout_widget
    
    def create_qframe(object_name: str, layout: QtWidgets.QBoxLayout, style_sheet=None) -> QtWidgets.QWidget:
        layout_Frame = QtWidgets.QFrame()
        layout_Frame.setObjectName(object_name)
        layout_Frame.setLayout(layout())
        if style_sheet:
            layout_Frame.setStyleSheet(style_sheet)
        return layout_Frame
    
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
    
    def create_qcolor_button(line_edit_color: str, color_value=None) -> tuple[QtWidgets.QLineEdit, QtWidgets.QPushButton]:
        if color_value:
            color_value_object = UiWidgetCreator.rgb_string_to_qcolor(color_value)
            color = UiWidgetCreator.convert_color_to_int_rgb_string(color_value_object)
        else:
            color_value_object = UiWidgetCreator.generate_random_color()
            color = UiWidgetCreator.convert_color_to_int_rgb_string(color_value_object)
        
        #widget: QtWidgets.QWidget = UiWidgetCreator.create_qwidget('input', QtWidgets.QVBoxLayout)
        #widget.layout().setContentsMargins(0, 0, 0, 0)
        # widget.setStyleSheet('background-color: red; border-radius: 0;')
            
            
        regex_validator = '^rgb\((0(\.\d+)?|1(\.0+)?|0\.\d+|0)\s*,\s*(0(\.\d+)?|1(\.0+)?|0\.\d+|0)\s*,\s*(0(\.\d+)?|1(\.0+)?|0\.\d+|0)\)$'
        float_color = UiWidgetCreator.convert_color_to_float_rgb_string(color_value_object)
        #line_edit = UiWidgetCreator.create_qline_edit(float_color, 'input', regex_validator=regex_validator)
        line_edit = UiWidgetCreator.create_input_line_edit(float_color, regex_validator, line_edit_color)
        color_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(None, 'input', style_sheet=f'border-radius: 10px; background-color: {color};')
        color_button.setFixedHeight(20)
        color_button.setMinimumWidth(100)
        #color_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(None, 'color_button', style_sheet=f'background: {color};')
        color_button.clicked.connect(partial(UiWidgetCreator.show_color_dialog, line_edit, color_button))
        
        #if content and widget:
        #    label = UiWidgetCreator.create_qlabel(content, 'color_input_label')
        #    widget.layout().addRow(label, color_button)
        
        #widget.layout().addWidget(color_button)
        #return line_edit, widget
        return line_edit, color_button
    
    def show_color_dialog(line_edit, color_button) -> None:
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            color_string = UiWidgetCreator.convert_color_to_float_rgb_string(color)
            hex_color = color.name()
            line_edit.setText(color_string)
            rgb_color = UiWidgetCreator.convert_color_to_int_rgb_string(color)
            color_button.setStyleSheet(f'border-radius: 10px; background-color: {rgb_color};')
            
    def generate_random_color() -> QColor:
        red = random.randint(0, 255)
        green = random.randint(0, 255)
        blue = random.randint(0, 255)

        return QColor(red, green, blue)
    
    def convert_color_to_float_rgb_string(color: QColor) -> str:
        red = min(color.red() / 255.0, 0.999)
        green = min(color.green() / 255.0, 0.999)
        blue = min(color.blue() / 255.0, 0.999)
        
        return f'rgb({red:.3f}, {green:.3f}, {blue:.3f})'
    
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
    message_box_qss = """QWidget {background: rgb(100, 100, 100); color: white;} 
        QPushButton {background: rgb(60, 60, 60); border-radius: 5px; min-width: 50; min-height: 30;}
        QPushButton:hover {background: rgb(90, 90, 90);}
        QPushButton:checked {background: rgb(70, 120, 190);}
        QPushButton:default {border: 1; border-style: outset; border-color: rgba(70, 120, 190, 200);}
        """
    def show_status(widget, content: str, object_name: str, remove_last_message: bool, is_row=True, content_of_last_label:str ='') -> None:
        if remove_last_message:
            if  widget.layout():
                last_item =  widget.layout().itemAt(widget.layout().count() - 1).widget()
                if isinstance(last_item, QtWidgets.QLabel) and last_item.text() != content_of_last_label:
                    last_item.deleteLater()
        label = UiWidgetCreator.create_qlabel(content, object_name)
        if is_row:
            widget.layout().addRow(label)
        else:
            widget.layout().addWidget(label)
        timer = QTimer()
        timer.singleShot(2000, lambda: UiWidgetCreator.hide_message(label, timer))
    
    def show_message(content: str, title: str, default_button=1, only_ok=False) -> QtWidgets.QMessageBox:
        msg_box = QtWidgets.QMessageBox()
        msg_box.setStyleSheet(UiWidgetCreator.message_box_qss)
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(content)
        
        if only_ok:
            ok_button = msg_box.addButton('Ok', QtWidgets.QMessageBox.AcceptRole)
            return msg_box
        
        yes_button = msg_box.addButton('Yes', QtWidgets.QMessageBox.AcceptRole)
        cancel_button = msg_box.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)
        
        if default_button == 0:
            msg_box.setDefaultButton(yes_button)
        elif default_button == 1:
            msg_box.setDefaultButton(cancel_button)
        
        return msg_box
    def save_popup(content: str):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setStyleSheet(UiWidgetCreator.message_box_qss)
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
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog  # Use the Qt dialog instead of the native one on some platforms

        # Add a filter to allow only JSON files
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(window, "Save File", "", "Json Files (*.json);;All Files (*)", options=options)
        
        # Check if the selected file has a JSON extension, if not, add it
        if file_name and not file_name.endswith('.json'):
            file_name += '.json'
        
        return file_name

    def open_file(window) -> str:
        options = QtWidgets.QFileDialog.Options()
        # options |= QtWidgets.QFileDialog.DontUseNativeDialog  # Use the Qt dialog instead of the native one on some platforms

        # Add a filter to allow only JSON files
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(window, "Open File", "", "Json Files (*.json);;All Files (*)", options=options)
        
        return file_name
    
    def create_generate_popup(parent, content: str='Generating...') -> QtWidgets.QDialog:
        dialog = QtWidgets.QDialog(parent, flags=Qt.FramelessWindowHint)
        dialog.setWindowModality(Qt.ApplicationModal)
        #dialog.setObjectName('generate_popup')
        dialog.setStyleSheet('background: rgb(70, 70, 70); border-radius: 5px;')
        dialog.setLayout(QtWidgets.QHBoxLayout())
        # Asset source: https://gifer.com/en/ZKZg
        loading = QMovie('assets/loading.gif')
        loading.setScaledSize(QSize(35, 35))
        loading_label = QtWidgets.QLabel()
        loading_label.setMovie(loading)
        loading.start()
        #loading_label.setFixedSize(50, 50)
        
        text_label = UiWidgetCreator.create_qlabel(content, 'generating_label')
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
    
    def open_save_sim_popup():
        dialog = SaveDialog()
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            # User clicked OK, retrieve the text from the line edit
            return dialog.line_edit.text()
        else:
            return None
        
    def create_input_field_widget(color: str, object_name: str = 'input'):
        widget: QtWidgets.QWidget = UiWidgetCreator.create_qwidget(object_name, QtWidgets.QVBoxLayout)
        widget.layout().setContentsMargins(0, 0, 0, 0)
        widget.setMinimumSize(100, 35)
        widget.layout().setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed) 
        widget.setStyleSheet(f'border-radius: none;background: {color};')
            
        return widget    
    
    def create_input_label(content: str, color: str, object_name: str = 'input'):
        # label: QtWidgets.QLabel = UiWidgetCreator.create_qlabel(content, object_name)
        label: ElidedLabel = ElidedLabel(content)
        label.setObjectName(object_name)
        #label: ElidingLabel = ElidingLabel(text=content, mode= Qt.ElideRight, padding=15)
        font_metrics = label.fontMetrics()
        elided_text = font_metrics.elidedText(label.text(), Qt.ElideRight, label.width())
        label.setText(elided_text)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed) 
        label.setMinimumSize(100, 35)
        label.setStyleSheet(f'border-radius: none;background: {color};padding-left: 15px;padding-right: 15px;')
        
        return label
    
    def label_clicked(input: Union[Type[QtWidgets.QLineEdit], Type[QtWidgets.QPushButton]], is_button: bool, event):
        print(event)
        if is_button:
            input.click()
        else:
            input.setFocus()
        
    
    def create_input_line_edit(content: str, regex_validator: str, color: str, object_name: str = 'input'):
        line_edit: QtWidgets.QLineEdit = UiWidgetCreator.create_qline_edit(content, object_name, regex_validator=regex_validator)
        line_edit.setMinimumSize(10, 20)
        line_edit.setStyleSheet(f'border-radius: 5px;background: {color};')
        line_edit.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed) 
        line_edit.setMaximumSize(100, 35)
        return line_edit
    
    def create_input_layout_widgets(object_name: str = 'input'):
        base_widget: QtWidgets.QWidget = UiWidgetCreator.create_qwidget(object_name, QtWidgets.QVBoxLayout)
        save_widget: QtWidgets.QWidget = UiWidgetCreator.create_qwidget(object_name, QtWidgets.QVBoxLayout)
        frame: QtWidgets.QFrame = UiWidgetCreator.create_qframe(object_name, QtWidgets.QHBoxLayout)
        label_widget: QtWidgets.QWidget = UiWidgetCreator.create_qwidget(object_name, QtWidgets.QVBoxLayout)
        input_widget: QtWidgets.QWidget = UiWidgetCreator.create_qwidget(object_name, QtWidgets.QVBoxLayout)
        
        base_widget.layout().setContentsMargins(0, 9, 0, 0)
        base_widget.layout().setSpacing(9)
        
        save_widget.layout().setAlignment(Qt.AlignBottom)
        
        frame.layout().setContentsMargins(0, 0, 0, 9)
        frame.layout().setSpacing(0)
        
        label_widget.layout().setContentsMargins(0, 0, 0, 0)
        label_widget.layout().setSpacing(0)
        label_widget.layout().setAlignment(Qt.AlignTop)
        
        input_widget.layout().setContentsMargins(0, 0, 0, 0)
        input_widget.layout().setSpacing(0)
        input_widget.layout().setAlignment(Qt.AlignTop)
        
        frame.layout().addWidget(label_widget, stretch=10)
        frame.layout().addWidget(input_widget, stretch=6)
        base_widget.layout().addWidget(frame, stretch=10)
        base_widget.layout().addWidget(save_widget, stretch=1)
        
        return base_widget, save_widget, frame, label_widget, input_widget
      
# Source: https://gist.github.com/rsgalloway/9514597
class ElidedLabel(QtWidgets.QLabel):
    def __init__(self, text, parent=None, padding = 15):
        super(ElidedLabel, self).__init__(text, parent)
        self.padding = padding

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        
        available_width = self.width() - self.padding
        
        elided_text = metrics.elidedText(self.text(), Qt.ElideRight, available_width)

        painter.drawText(QRect(self.padding, 0, available_width, self.height()), self.alignment(), elided_text)

      
        
class SaveDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SaveDialog, self).__init__(parent)
        self.setWindowTitle("Save simulation stats")

        self.label = QtWidgets.QLabel("Simulation name: ")
        self.line_edit = QtWidgets.QLineEdit(self)
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.line_edit.setText(str(formatted_datetime))
        self.ok_button = QtWidgets.QPushButton("Save", self)
        self.cancel_button = QtWidgets.QPushButton("Cancel", self)

        # Set up layouts
        label_line_edit_layout = QtWidgets.QHBoxLayout()
        label_line_edit_layout.addWidget(self.label)
        label_line_edit_layout.addWidget(self.line_edit)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(label_line_edit_layout)
        main_layout.addLayout(button_layout)

        # Connect buttons to slots
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
    
    
