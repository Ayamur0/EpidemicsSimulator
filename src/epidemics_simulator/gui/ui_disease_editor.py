from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
class UiDiseaseEditor:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.network_editor.disease_content.layout().setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        
                    
    def load_properties(self, diseasees):
        
        self.create_add_disease_button()
        for disease in diseasees:
            disease_prop = disease.get_properties_dict()
            self.open_properties_input(disease_prop)
        
            
    def create_add_disease_button(self):
        v = None
        widget = UiWidgetCreator.create_layout_widget('add_disease', QtWidgets.QVBoxLayout())
        widget.setMinimumSize(240, 256)
        form_layout = UiWidgetCreator.create_layout_widget('add_disease_form', QtWidgets.QFormLayout())
        label = UiWidgetCreator.create_label('Healty color', 'disease_label_properties')
        color = UiWidgetCreator.generate_random_color().name() if not v else v # replace v with the real healthy color
        color_button = UiWidgetCreator.create_push_button(None, 'color_button', style_sheet=f'background: {color};')
        color_button.clicked.connect(lambda: UiWidgetCreator.show_color_dialog(line_edit, color_button))
        line_edit = UiWidgetCreator.create_line_edit(color, 'group_line_edit_properties', regex_validator='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        form_layout.layout().addRow(label, color_button)
        widget.layout().addWidget(form_layout)
        
        button = UiWidgetCreator.create_push_button('+', 'add_disease_button')
        button.clicked.connect(lambda: self.add_new_disease())
        widget.layout().addWidget(button)
        self.network_editor.disease_content.layout().addWidget(widget, 0, 0)
        
    def open_properties_input(self, properties: dict):
        line_edits = {}
        form_layout = UiWidgetCreator.create_layout_widget('disease_form', QtWidgets.QFormLayout())
        form_layout.setMinimumSize(240, 256)
        for p, v in properties.items():
            label = UiWidgetCreator.create_label(p, 'disease_label_properties')
            regex_validator = '^\d*\.\d+$'
            if p == 'name':
                regex_validator = '.*'
            elif p == 'initial infection count' or p == 'duration':
                regex_validator = '^[1-9]\d*$'
            elif p == 'infected color':
                color = UiWidgetCreator.generate_random_color().name() if not v else v
                color_button = UiWidgetCreator.create_push_button(None, 'color_button', style_sheet=f'background: {color};')
                color_button.clicked.connect(lambda: UiWidgetCreator.show_color_dialog(line_edit, color_button))
                line_edit = UiWidgetCreator.create_line_edit(color, 'group_line_edit_properties', regex_validator=regex_validator)
                form_layout.layout().addRow(label, color_button)
                line_edits[p] = line_edit
                continue
            
            line_edit = UiWidgetCreator.create_line_edit(v, 'group_line_edit_properties', regex_validator=regex_validator)
            form_layout.layout().addRow(label, line_edit)
            line_edits[p] = line_edit
            
        self.create_save_remove_button(form_layout, line_edits)
        UiWidgetCreator.move_grid_widgets_right(self.network_editor.disease_content, 1, 4)
        self.network_editor.disease_content.layout().addWidget(form_layout, 0, 1)
        return line_edits
           
    
    def create_save_remove_button(self, form_layout, line_edits):
        layout = UiWidgetCreator.create_layout_widget('handle_input_layout', QtWidgets.QHBoxLayout())
        save = UiWidgetCreator.create_push_button('save', 'save_disease_button')
        remove = UiWidgetCreator.create_push_button('remove', 'remove_disease_button')
        
        save.clicked.connect(lambda: self.save_input(line_edits))
        remove.clicked.connect(lambda: self.remove_disease())
        
        layout.layout().addWidget(save)
        layout.layout().addWidget(remove)
        form_layout.layout().addWidget(layout)
        
    def save_input(self, line_edits):
        for key, value in line_edits.items():
            print(value.text())
        pass
    
    def remove_disease(self):
        pass
    def add_new_disease(self):
        default_dict = {
            "name": '',
            "fatality rate": '',
            "vaccinated fatality rate ": '',
            "infection rate": '',
            "reinfection rate": '',
            "vaccinated infection rate": '',
            "duration": '',
            "initial infection count": '',
            "infected color": '',
        }
        self.open_properties_input(default_dict)




    #def get_properties_dict(self):
    #    return {
    #        "name": self.name,
    #        "fatality rate": self.fatality_rate,
    #        "vaccinated fatality rate ": self.vaccinated_fatality_rate ,
    #        "infection rate": self.infection_rate,
    #        "reinfection rate": self.reinfection_rate,
    #        "vaccinated infection rate": self.vaccinated_infection_rate,
    #        "duration": self.duration,
    #        "initial infection count": self.initial_infection_count,
    #        "infected color": self.color,
    #    }