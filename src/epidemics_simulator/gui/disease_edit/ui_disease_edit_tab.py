from functools import partial
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QObject
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network, NodeGroup, Project, Disease
from src.epidemics_simulator.gui.flowlayout import FlowLayout

class UiDiseaseEditTab:
    def __init__(self, main_window: QtWidgets.QMainWindow):
        self.main_window = main_window
        
        self.disease_content = self.main_window.disease_content
        flow = FlowLayout(self.disease_content)
        self.disease_content.setLayout(flow)
        self.disease_layout_list = []
        self.min_frame_size = (380, 550)
                
        self.tab_widget = self.main_window.disease_edit
        self.is_creating_disease = False
        
    def init_ui(self, network: Network):
        self.is_creating_disease = False
        self.disease_content.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.network = network
        # in the inital creating save the loaded color to the keys so the color can be displayed. After that it contains line_edits
        self.load_inputs(self.network)
        
    def insert_to_flowlayout_at(self, layout: QtWidgets.QLayout, widget: QtWidgets.QWidget, index: int):
        widget_list = [widget]
        for _ in range(index, layout().count()):
            widget_list.append(layout().takeAt(index).widget())
        for item in widget_list:
            layout().addWidget(item)  
    def load_inputs(self, network: Network):
        self.line_edits: dict = {'healty': self.network.healthy_color, 'cured': self.network.cured_color, 'vaccinated': self.network.vaccinated_color, 'deceased': self.network.deceased_color}
        self.load_add_disease_input()
        for disease in network.diseases:
            self.load_disease(disease)
            #if disease.id == id_success_save:
            #    self.load_disease(disease, id_success_save=id_success_save)
            #else:
            #    self.load_disease(disease)

    def load_add_disease_input(self):
        base_widget, button_widget, _, label_widget, input_widget = UiWidgetCreator.create_input_layout_widgets()
        # button_widget.layout().setAlignment(Qt.AlignBottom)
        # button_widget = UiWidgetCreator.create_qwidget('add_disease', QtWidgets.QVBoxLayout)
        i = 0
        for typ, line_edit in self.line_edits.items():
            if i % 2 == 0:
                color = 'rgb(65, 65, 65)'
            else:
                color = 'rgb(80, 80, 80)'
            i += 1
            label = UiWidgetCreator.create_input_label(f'{typ} color', color)
            widget = UiWidgetCreator.create_input_field_widget(color)
            line_edit, color_button = UiWidgetCreator.create_qcolor_button(color, line_edit)
            self.line_edits[typ] = line_edit
            widget.layout().addWidget(color_button)
            input_widget.layout().addWidget(widget)
            label_widget.layout().addWidget(label)
            line_edit.textChanged.connect(lambda: self.update_type_colors())
            line_edit.textChanged.connect(lambda: self.main_window.disease_changed.emit())
            
        add_disease_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(None, 'add_button')
        add_disease_button.setIcon(self.main_window.add_icon)
        add_disease_button.clicked.connect(lambda: self.add_disease())
        button_widget.layout().addWidget(add_disease_button)
        base_widget.setFixedSize(*self.min_frame_size)
        base_widget.setMinimumSize(*self.min_frame_size)
        self.disease_layout_list.insert(0, -1)
        
        # base_widget.layout().addWidget(button_widget)
        self.disease_content.layout().addWidget(base_widget)
        
        
        
        
        #input_widget = UiWidgetCreator.create_qwidget('add_disease', QtWidgets.QVBoxLayout)
        #form_layout = UiWidgetCreator.create_qwidget('add_disease_form', QtWidgets.QFormLayout)
        
        #for typ, line_edit in self.line_edits.items():
        #    line_edit, _ = UiWidgetCreator.create_qcolor_button(color_value=line_edit, content=f'{typ} color', widget=form_layout)
        #    self.line_edits[typ] = line_edit
        #    line_edit.textChanged.connect(lambda: self.update_type_colors())
        #    line_edit.textChanged.connect(lambda: self.main_window.disease_changed.emit())
        
        #input_widget.layout().addWidget(form_layout)
        
        #add_disease_button = UiWidgetCreator.create_qpush_button(None, 'add_button')
        #add_disease_button.setIcon(self.main_window.add_icon)
        #add_disease_button.clicked.connect(lambda: self.add_disease())
        #input_widget.layout().addWidget(add_disease_button)
        #input_widget.setFixedSize(*self.min_frame_size)
        #input_widget.setMinimumSize(*self.min_frame_size)
        #self.disease_layout_list.insert(0, -1)
        #self.disease_content.layout().addWidget(input_widget)
        #self.disease_content.layout().addWidget(input_widget, 0, 0)
        
    def load_disease(self, disease: Disease, default_properties: dict = None, is_success_save: bool=False, insertion_index: int=1):
        base_widget, save_widget, frame, label_widget, input_widget = UiWidgetCreator.create_input_layout_widgets()
        save_widget.layout().setAlignment(Qt.AlignCenter)
        #frame = UiWidgetCreator.create_qframe('disease_input_frame', QtWidgets.QVBoxLayout)
        #form_widget = UiWidgetCreator.create_qwidget('disease_form', QtWidgets.QFormLayout)
        properties = disease.get_properties_dict() if disease else default_properties
        
        #if disease and disease.id == id_success_save:
        #    line_edits = self.load_properties(form_widget, properties, id_success_save=id_success_save)
        #else:
        #    line_edits = self.load_properties(form_widget, properties, id_success_save=id_success_save)
        line_edits = self.load_properties(label_widget, input_widget, save_widget, properties, is_success_save=is_success_save)
        # line_edits = self.load_properties(form_widget, properties, is_success_save=is_success_save)
        #frame.layout().addWidget(form_widget)
        #frame.setFixedSize(*self.min_frame_size)
        base_widget.setMinimumSize(*self.min_frame_size)
        #frame.setMinimumSize(*self.min_frame_size)
        if default_properties:
            self.disease_layout_list.insert(1, None)
        elif self.is_creating_disease:
            self.disease_layout_list.insert(2, disease.id)
        else:
            self.disease_layout_list.insert(1, disease.id)
        self.insert_to_flowlayout_at(self.disease_content.layout, base_widget, insertion_index)
        #UiWidgetCreator.move_grid_widgets_right(self.disease_content.layout(), 1, 4)
        #self.disease_content.layout().addWidget(frame, 0, 1, alignment=Qt.AlignLeft)
        
        # button_widget = self.create_input_buttons(line_edits, disease, base_widget)
        # frame.layout().addWidget(button_widget, alignment=Qt.AlignBottom)
        button_widget = self.create_input_buttons(line_edits, disease, save_widget)
        base_widget.layout().addWidget(button_widget, alignment=Qt.AlignBottom)
        
        
    def create_input_buttons(self, line_edits, disease, form_widget):
        layout_widget = UiWidgetCreator.create_qwidget('handle_input_layout', QtWidgets.QHBoxLayout)
        save_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(None, 'add_button')
        save_button.setIcon(self.main_window.save_icon)
        save_button.clicked.connect(partial(self.save_disease, disease, line_edits, form_widget))
        
        delete_button = UiWidgetCreator.create_qpush_button(None, 'delete_button')
        delete_button.setIcon(self.main_window.remove_icon)
        delete_button.clicked.connect(partial(self.delete_disease, disease))
        
        layout_widget.layout().addWidget(delete_button)
        if disease:
            duplicate_button = UiWidgetCreator.create_qpush_button(None, 'duplicate_button')
            duplicate_button.setIcon(self.main_window.duplicate_icon)
            duplicate_button.clicked.connect(partial(self.duplicate_disease, disease))

            layout_widget.layout().addWidget(duplicate_button)
        layout_widget.layout().addWidget(save_button)
        return layout_widget
        
    # def load_properties(self, form_widget: QtWidgets.QWidget, properties: dict, is_success_save: bool=False):
    def load_properties(self, label_widget: QtWidgets.QWidget, input_widget: QtWidgets.QWidget, save_widget: QtWidgets.QWidget, properties: dict, is_success_save: bool=False):
        line_edits: dict = {}
        i = 0
        for key, value in properties.items():
            if i % 2 == 0:
                color = 'rgb(65, 65, 65)'
            else:
                color = 'rgb(80, 80, 80)'
            i += 1
            # label = UiWidgetCreator.create_qlabel(key, 'group_propertie_label')
            label = UiWidgetCreator.create_input_label(key, color)
            label_widget.layout().addWidget(label)
            widget = UiWidgetCreator.create_input_field_widget(color)
            regex_validator = '^0(\.\d+)?$|^1(\.0+)?$'
            if key == 'name':
                regex_validator = '.*'
            elif key == 'color':
                line_edit, color_button = UiWidgetCreator.create_qcolor_button(color, value)
                line_edits[key] = line_edit
                widget.layout().addWidget(color_button)
                input_widget.layout().addWidget(widget)
                # form_widget.layout().addRow(label, color_button)
                continue
            elif key == 'initial infection count' or key == 'duration' or key == 'immunity period':
                regex_validator = '^(?!10000001$)[0-9]{1,8}$ '# Only allows numbers that are below 10 Million (amount of nodes cant exceed 10 Mil)
            # line_edit = UiWidgetCreator.create_qline_edit(value, 'group_line_edit_properties', regex_validator=regex_validator)
            line_edit = UiWidgetCreator.create_input_line_edit(value, regex_validator, color)
            line_edits[key] = line_edit
            widget.layout().addWidget(line_edit)
            
            input_widget.layout().addWidget(widget)
            # form_widget.layout().addRow(label, line_edit)
        if is_success_save:
            UiWidgetCreator.show_status(save_widget, "Successfully created", 'success_message', True, is_row=False)
            # UiWidgetCreator.show_status(form_widget, "Successfully created", 'success_message', True)
        return line_edits
           
        
    def update_type_colors(self):
        self.network.set_healthy_color(self.line_edits['healty'].text())
        self.network.set_cured_color(self.line_edits['cured'].text())
        self.network.set_vaccinated_color(self.line_edits['vaccinated'].text())
        self.network.set_deceased_color(self.line_edits['deceased'].text())
        
    def add_disease(self):
        if self.is_creating_disease:
            return  
        self.is_creating_disease = True
        default_dict = {
            "name": '',
            "color": '',
            "fatality rate": '',
            "vaccinated fatality rate": '',
            "infection rate": '',
            "reinfection rate": '',
            "vaccinated infection rate": '',
            "duration": '',
            "initial infection count": '',
            "cure chance": '',
            "immunity period": '',
            "infectiousness factor": ''
        }
        self.load_disease(None, default_properties=default_dict)
     
    def save_disease(self, disease: Disease, line_edits: dict, save_widget):
        updated_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        if disease:
            try:
                disease.set_from_dict(updated_dict)
            except ValueError:
                UiWidgetCreator.show_status(save_widget, "Pleas fill out every input", 'error_message', True, is_row=False)
                return
            UiWidgetCreator.show_status(save_widget, "Successfully saved", 'success_message', True, is_row=False)
            self.main_window.disease_changed.emit()
            return
        else:
            try:
                disease = Disease.init_from_dict(updated_dict)
                self.network.add_disease(disease)
            except ValueError:
                UiWidgetCreator.show_status(save_widget, "Pleas fill out every input", 'error_message', True, is_row=False)
                return
        self.delete_disease_from_layout_at(1)
        if len(self.disease_layout_list) == 1:
            self.disease_layout_list.append(disease.id)
        else:
            self.disease_layout_list[1] = disease.id
        self.is_creating_disease = False
        #self.unload()
        #self.load_inputs(self.network, id_success_save=disease.id)
        self.load_disease(disease, is_success_save=True)
        self.main_window.disease_changed.emit()
    
    def duplicate_disease(self, disease: Disease):
        new_disease = Disease(disease.name, disease.color, disease.fatality_rate, disease.vaccinated_fatality_rate, disease.infection_rate, disease.reinfection_rate, disease.vaccinated_infection_rate, disease.duration, disease.initial_infection_count)
        self.network.add_disease(new_disease)
        #new_disease.name = new_disease.id
        self.load_disease(new_disease, insertion_index=2)
        self.main_window.disease_changed.emit()
        
    def delete_disease(self, disease: Disease):
        if not disease:
            self.delete_disease_from_layout_at(1)
            self.is_creating_disease = False
            return
        message = UiWidgetCreator.show_message(f'Are you sure you want to delete disease {disease.name}', 'Disease deletion')
        result = message.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return
        self.network.remove_disease(disease.id)
        index = self.get_disease_widget_position(disease.id)
        if not index:
            print('Error occured that should not happen')
        self.delete_disease_from_layout_at(index)
        
        #self.unload()
        #self.load_inputs(self.network)
        self.main_window.disease_changed.emit()
        
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
    def unload(self):
        self.disease_layout_list.clear()
        self.is_creating_disease = False
        self.main_window.unload_items_from_layout(self.disease_content.layout())