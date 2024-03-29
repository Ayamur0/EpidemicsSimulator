from functools import partial
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, Disease
from src.epidemics_simulator.gui.flowlayout import FlowLayout

class UiDiseaseEditTab(QObject):
    disease_change_singal: pyqtSignal = pyqtSignal()
    def __init__(self, parent: QtWidgets.QMainWindow):
        super(UiDiseaseEditTab, self).__init__()
        self.parent = parent
        
        self.disease_content = self.parent.disease_content
        flow = FlowLayout(self.disease_content)
        self.disease_content.setLayout(flow)
        self.disease_content.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.disease_layout_list = []
        self.min_frame_size = (380, 550)
                
        self.is_creating_disease = False
        self.disease_changed = False
        
        self.connect_signals()
        
    def connect_signals(self):
        self.disease_change_singal.connect(self.on_disese_change)
        self.disease_change_singal.connect(self.parent.content_changed)
    
    def on_disese_change(self):
        self.disease_changed = True
    
    def init_ui(self, network: Network):
        self.network = network
        # in the inital creating save the loaded color to the keys so the color can be displayed. After that it contains line_edits
        self.load_inputs()
        
    def load_inputs(self):
        self.line_edits: dict = {"healty": self.network.healthy_color, "cured": self.network.cured_color, "vaccinated": self.network.vaccinated_color, "deceased": self.network.deceased_color}
        self.load_add_disease_input()
        for disease in self.network.diseases:
            self.load_disease(disease)
            
    def load_add_disease_input(self):
        base_widget, button_widget, _, label_widget, input_widget = UiWidgetCreator.create_input_layout_widgets()
        i = 0
        for typ, line_edit in self.line_edits.items():
            color = self.parent.create_alternate_line_color(i)
            i += 1
            label = UiWidgetCreator.create_input_label(f"{typ} color", color)
            widget = UiWidgetCreator.create_input_field_widget(color)
            line_edit, color_button = UiWidgetCreator.create_qcolor_button(color, line_edit)
            self.line_edits[typ] = line_edit
            widget.mousePressEvent = partial(UiWidgetCreator.label_clicked, color_button, True)
            label.mousePressEvent = partial(UiWidgetCreator.label_clicked, color_button, True)
            widget.layout().addWidget(color_button)
            input_widget.layout().addWidget(widget)
            label_widget.layout().addWidget(label)
            line_edit.textChanged.connect(lambda: self.update_type_colors())
            line_edit.textChanged.connect(lambda: self.disease_change_singal.emit())
            
        self.add_disease_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(None, "add_button", icon=self.parent.add_icon)
        self.add_disease_button.clicked.connect(lambda: self.add_disease())
        button_widget.layout().addWidget(self.add_disease_button)
        base_widget.setFixedSize(*self.min_frame_size)
        base_widget.setMinimumSize(*self.min_frame_size)
        self.disease_layout_list.insert(0, -1)
        self.disease_content.layout().addWidget(base_widget)
    
    def load_disease(self, disease: Disease, default_properties: dict = None, is_success_save: bool=False):
        base_widget, save_widget, _, label_widget, input_widget = UiWidgetCreator.create_input_layout_widgets()
        save_widget.layout().setAlignment(Qt.AlignCenter)
        properties = disease.get_properties_dict() if disease else default_properties

        line_edits = self.load_properties(label_widget, input_widget, save_widget, properties, is_success_save=is_success_save)
        base_widget.setMinimumSize(*self.min_frame_size)
        if default_properties:
            insertion_index = 1
        elif self.is_creating_disease:
            insertion_index = 2
        else:
            insertion_index = 1
        self.disease_layout_list.insert(insertion_index, disease.id if not default_properties else None)
        self.insert_to_flowlayout_at(self.disease_content.layout, base_widget, insertion_index)
        button_widget = self.create_input_buttons(line_edits, disease, save_widget)
        base_widget.layout().addWidget(button_widget, alignment=Qt.AlignBottom)
        if default_properties:
            line_edits["name"].setFocus()
        else:
            base_widget.setFocus()
    
    def create_input_buttons(self, line_edits, disease, form_widget):
        layout_widget = UiWidgetCreator.create_qwidget("handle_input_layout", QtWidgets.QHBoxLayout)
        save_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(None, "add_button", icon=self.parent.save_icon)
        save_button.clicked.connect(partial(self.save_disease, disease, line_edits, form_widget))
        
        delete_button = UiWidgetCreator.create_qpush_button(None, "delete_button", icon=self.parent.remove_icon)
        delete_button.clicked.connect(partial(self.delete_disease, disease))
        
        layout_widget.layout().addWidget(delete_button)
        if disease:
            duplicate_button = UiWidgetCreator.create_qpush_button(None, "duplicate_button", icon=self.parent.duplicate_icon)
            duplicate_button.clicked.connect(partial(self.duplicate_disease, disease))

            layout_widget.layout().addWidget(duplicate_button)
        layout_widget.layout().addWidget(save_button)
        return layout_widget
    
    def load_properties(self, label_widget: QtWidgets.QWidget, input_widget: QtWidgets.QWidget, save_widget: QtWidgets.QWidget, properties: dict, is_success_save: bool=False):
        line_edits: dict = {}
        i = 0
        for key, value in properties.items():
            color = self.parent.create_alternate_line_color(i)
            i += 1
            label = UiWidgetCreator.create_input_label(key, color)
            label_widget.layout().addWidget(label)
            widget = UiWidgetCreator.create_input_field_widget(color)
            regex_validator = "^0(\.\d+)?$|^1(\.0+)?$"
            if key == "name":
                regex_validator = ".*"
            elif key == "color":
                line_edit, color_button = UiWidgetCreator.create_qcolor_button(color, value)
                line_edits[key] = line_edit
                widget.mousePressEvent = partial(UiWidgetCreator.label_clicked, color_button, True)
                label.mousePressEvent = partial(UiWidgetCreator.label_clicked, color_button, True)
                widget.layout().addWidget(color_button)
                input_widget.layout().addWidget(widget)
                continue
            elif key == "initial infection count" or key == "duration" or key == "immunity period":
                regex_validator = "^(?!10000001$)[0-9]{1,8}$ "# Only allows numbers that are below 10 Million (amount of nodes cant exceed 10 Mil)
            line_edit = UiWidgetCreator.create_input_line_edit(value, regex_validator, color)
            line_edits[key] = line_edit
            widget.mousePressEvent = partial(UiWidgetCreator.label_clicked, line_edit, False)
            label.mousePressEvent = partial(UiWidgetCreator.label_clicked, line_edit, False)
            widget.layout().addWidget(line_edit)
            
            input_widget.layout().addWidget(widget)
        if is_success_save:
            UiWidgetCreator.show_message(save_widget, "Successfully created.", "success_message", True, is_row=False)
        return line_edits
    
    def update_type_colors(self):
        self.network.set_healthy_color(self.line_edits["healty"].text())
        self.network.set_cured_color(self.line_edits["cured"].text())
        self.network.set_vaccinated_color(self.line_edits["vaccinated"].text())
        self.network.set_deceased_color(self.line_edits["deceased"].text())
        
    def add_disease(self):
        if self.is_creating_disease:
            return  
        self.add_disease_button.setDisabled(True)
        self.is_creating_disease = True
        default_dict = {
            "name": "Disease",
            "color": "",
            "fatality rate": 0.2,
            "vaccinated fatality rate": 0.05,
            "infection rate": 0.2,
            "reinfection rate": 0.05,
            "vaccinated infection rate": 0.001,
            "duration": 5,
            "initial infection count": 10,
            "cure chance": 0.2,
            "immunity period": 8,
            "infectiousness factor": 1.0
        }
        self.load_disease(None, default_properties=default_dict)
        
    def change_wrong_float_inputs(self, line_edits: dict):
        not_float_keys = ["name", "color", "duration", "initial infection count", "immunity period"]
        for key in line_edits:
            if key in not_float_keys:
                continue
            line_string = line_edits[key].text()
            if "." in line_string and not line_string.endswith("."):
                continue
            float_value = float(line_string)
            line_edits[key].setText("{:.1f}".format(float_value))
        
    def save_disease(self, disease: Disease, line_edits: dict, save_widget):
        self.change_wrong_float_inputs(line_edits)
        updated_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        if any(value == "" for value in updated_dict.values()):
            UiWidgetCreator.show_message(save_widget, "Please fill out every input.", "error_message", True, is_row=False)
            return
        if disease:
            disease.set_from_dict(updated_dict)
            UiWidgetCreator.show_message(save_widget, "Successfully saved.", "success_message", True, is_row=False)
            self.disease_change_singal.emit()
            return
        else:
            disease = Disease.init_from_dict(updated_dict)
            self.network.add_disease(disease)
        self.delete_disease_from_layout_at(1)
        self.is_creating_disease = False
        self.add_disease_button.setDisabled(False)
        self.load_disease(disease, is_success_save=True)
        self.disease_change_singal.emit()
        
    def create_disease_name_list(self):
        return [d.name for d in self.network.diseases]
        
    def duplicate_disease(self, disease: Disease):
        new_group_name = self.parent.generate_next_name(disease.name, self.create_disease_name_list())
        new_disease = Disease(new_group_name, disease.color, disease.fatality_rate, disease.vaccinated_fatality_rate, disease.infection_rate, disease.reinfection_rate, disease.vaccinated_infection_rate, disease.duration, disease.initial_infection_count)
        self.network.add_disease(new_disease)
        self.load_disease(new_disease)
        self.disease_change_singal.emit()
        
    def delete_disease(self, disease: Disease):
        if not disease:
            self.delete_disease_from_layout_at(1)
            self.is_creating_disease = False
            self.add_disease_button.setDisabled(False)
            return
        message = UiWidgetCreator.show_qmessagebox(f"Are you sure you want to delete disease {disease.name}?", "Delete Disease")
        result = message.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return
        self.network.remove_disease(disease.id)
        index = self.get_disease_widget_position(disease.id)
        if not index:
            print("Error occured that should not happen.")
        self.delete_disease_from_layout_at(index)
        self.disease_change_singal.emit()
        
        self.parent.setFocus()
    
    def delete_disease_from_layout_at(self, index):
        item = self.disease_content.layout().takeAt(index)
        widget = item.widget()
        if not widget:
            return
        self.disease_layout_list.pop(index)
        widget.setParent(None)
        widget.deleteLater()
        
    def get_disease_widget_position(self, disease_id):
        for i in range(0, len(self.disease_layout_list)):
            item_id = self.disease_layout_list[i]
            if item_id != disease_id:
                continue
            return i
        return None
    
    def insert_to_flowlayout_at(self, layout: QtWidgets.QLayout, widget: QtWidgets.QWidget, index: int):
        widget_list = [widget]
        for _ in range(index, layout().count()):
            widget_list.append(layout().takeAt(index).widget())
        for item in widget_list:
            layout().addWidget(item) 
    
    def unload(self):
        self.disease_layout_list.clear()
        self.is_creating_disease = False
        self.disease_changed = False
        try:
            self.add_disease_button.setDisabled(False)
        except AttributeError:
            pass
        self.parent.unload_items_from_layout(self.disease_content.layout())