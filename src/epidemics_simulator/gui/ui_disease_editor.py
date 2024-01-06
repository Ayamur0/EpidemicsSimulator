from functools import partial
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage.disease import Disease
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
class UiDiseaseEditor:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.network_editor.disease_content.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.is_creating_disease = False
        
        
                    
    def load_properties(self, diseasees, disease_save=None):
        self.create_add_disease_button()
        for disease in diseasees:
            disease_prop = disease.get_properties_dict()
            if disease.id == disease_save:
                self.open_properties_input(disease_prop, disease, disease_save)
                continue
            self.open_properties_input(disease_prop, disease)
        
            
    def create_add_disease_button(self):
        widget = UiWidgetCreator.create_layout_widget('add_disease', QtWidgets.QVBoxLayout())
        widget.setMinimumSize(240, 256)
        form_layout = UiWidgetCreator.create_layout_widget('add_disease_form', QtWidgets.QFormLayout())
        _, line_edit = UiWidgetCreator.create_color_button('healty color', form_layout, color_value=self.network_editor.current_network.healthy_color)
        line_edit.textChanged.connect(lambda: self.network_editor.current_network.set_healty_color(line_edit.text()))
        line_edit.textChanged.connect(lambda: self.network_editor.disease_changed.emit())
        
        _, line_edit = UiWidgetCreator.create_color_button('cured color', form_layout, color_value=self.network_editor.current_network.cured_color)
        line_edit.textChanged.connect(lambda: self.network_editor.current_network.set_cured_color(line_edit.text()))
        line_edit.textChanged.connect(lambda: self.network_editor.disease_changed.emit())
        
        _, line_edit = UiWidgetCreator.create_color_button('vaccinated color', form_layout, color_value=self.network_editor.current_network.vaccinated_color)
        line_edit.textChanged.connect(lambda: self.network_editor.current_network.set_vaccinated_color(line_edit.text()))
        line_edit.textChanged.connect(lambda: self.network_editor.disease_changed.emit())
        
        _, line_edit = UiWidgetCreator.create_color_button('deceased color', form_layout, color_value=self.network_editor.current_network.deceased_color)
        line_edit.textChanged.connect(lambda: self.network_editor.current_network.set_deceased_color(line_edit.text()))
        line_edit.textChanged.connect(lambda: self.network_editor.disease_changed.emit())
        
        
        
        widget.layout().addWidget(form_layout)
        
        button = UiWidgetCreator.create_push_button('+', 'add_disease_button')
        button.clicked.connect(lambda: self.add_new_disease(form_layout))
        widget.layout().addWidget(button)
        self.network_editor.disease_content.layout().addWidget(widget, 0, 0)
        
    def open_properties_input(self, properties: dict, disease: Disease, disease_save=None):
        frame = UiWidgetCreator.create_qframe('disease_input_frame', QtWidgets.QVBoxLayout())
        content_widget = UiWidgetCreator.create_layout_widget('disease_input', QtWidgets.QVBoxLayout())
        #scroll_area = UiWidgetCreator.create_qscroll_area('disease_input')
        #frame.layout().addWidget(scroll_area)
        frame.layout().addWidget(content_widget)
        line_edits = {}
        form_layout = UiWidgetCreator.create_layout_widget('disease_form', QtWidgets.QFormLayout())
        #scroll_area.setWidget(form_layout)
        
        form_layout.setMinimumSize(240, 256)
        for p, v in properties.items():
            label = UiWidgetCreator.create_label(p, 'disease_label_properties')
            regex_validator = '^\d*\.\d+$'
            if p == 'name':
                regex_validator = '.*'
            elif p == 'initial infection count' or p == 'duration':
                regex_validator = '^[1-9]\d*$'
            elif p == 'color':
                _, line_edit = UiWidgetCreator.create_color_button(p, form_layout.layout(), v)
                line_edits[p] = line_edit
                continue            
            line_edit = UiWidgetCreator.create_line_edit(v, 'disease_line_edit_properties', regex_validator=regex_validator)
            form_layout.layout().addRow(label, line_edit)
            line_edits[p] = line_edit
        content_widget.layout().addWidget(form_layout)
        self.create_save_remove_button(frame, form_layout, line_edits, disease)
        if disease_save: # show success message here, because the page is reload so the message would be removed instantly
            UiWidgetCreator.show_message(form_layout, "Successfully created", 'success_message', True)
        UiWidgetCreator.move_grid_widgets_right(self.network_editor.disease_content, 1, 4)
        self.network_editor.disease_content.layout().addWidget(frame, 0, 1)
        return line_edits
           
    
    def create_save_remove_button(self, frame, line_edit_layout, line_edits, disease: Disease):
        layout = UiWidgetCreator.create_layout_widget('handle_input_layout', QtWidgets.QHBoxLayout())
        save = UiWidgetCreator.create_push_button('save', 'save_disease_button')
        
        
        
        save.clicked.connect(lambda: self.save_input(line_edits, line_edit_layout, disease))
        
        
        layout.layout().addWidget(save)
        
        if disease:
            duplicate = UiWidgetCreator.create_push_button('duplicate', 'duplicate_disease_button')
            remove = UiWidgetCreator.create_push_button('remove', 'remove_disease_button')
            duplicate.clicked.connect(lambda: self.duplicate_disease(disease))
            remove.clicked.connect(partial(self.remove_disease, disease))
            layout.layout().addWidget(duplicate)
            layout.layout().addWidget(remove)
            
        
        frame.layout().addWidget(layout)
        
    def duplicate_disease(self, disease: Disease):
        new_disease = Disease(disease.name, disease.color, disease.fatality_rate, disease.vaccinated_fatality_rate, disease.infection_rate, disease.reinfection_rate, disease.vaccinated_infection_rate, disease.duration, disease.initial_infection_count)
        self.network_editor.current_network.add_disease(new_disease)
        self.network_editor.disease_changed.emit()
        self.is_creating_disease = False
        self.unload()
        self.load_properties(self.network_editor.current_network.diseases, None)
        
    def save_input(self, line_edits, line_edit_layout, disease: Disease):
        updated_dict = {key: line_edits[key].text() for key in line_edits.keys()}
        
        if disease:
            try:
                disease.set_from_dict(updated_dict)
            except ValueError as e:
                UiWidgetCreator.show_message(line_edit_layout, "Pleas fill out every input", 'error_message', True)
                return
        else:
            try:
                disease = Disease.init_from_dict(updated_dict)
                self.network_editor.current_network.add_disease(disease)
            except ValueError as e:
                UiWidgetCreator.show_message(line_edit_layout, "Pleas fill out every input", 'error_message', True)
                return
            UiWidgetCreator.show_message(line_edit_layout, "Successfully created", 'success_message', True)
        self.unload()
        self.load_properties(self.network_editor.current_network.diseases, disease.id)
        self.is_creating_disease = False
        self.network_editor.disease_changed.emit()
    
    def remove_disease(self, disease: Disease):
        msg_box  = UiWidgetCreator.create_delete_dialog(f'Are you sure you want to delete "{disease.name}"?')
        result = msg_box.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return
        self.network_editor.current_network.remove_disease(disease.id)
        self.unload()
        self.load_properties(self.network_editor.current_network.diseases)
        self.is_creating_disease = False
    def add_new_disease(self, line_edit_layout):
        if self.is_creating_disease:
            UiWidgetCreator.show_message(line_edit_layout, 'Please finish current disease creation', 'error_message', True, is_row=False)
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
        }
        self.open_properties_input(default_dict, None)


    def unload(self):
        self.is_creating_disease = False
        self.network_editor.unload_items_from_layout(self.network_editor.disease_content.layout())
