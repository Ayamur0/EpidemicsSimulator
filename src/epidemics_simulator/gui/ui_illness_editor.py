from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from PyQt5 import QtWidgets
class UiIllnessEditor:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.load_properties([])
                    
    def load_properties(self, illnesses):
        self.create_add_illness_button()
        for illness in illnesses:
            # illness_prop = illness.get_properties()
            # self.open_properties_input(illness_prop)
            pass
        
            
    def create_add_illness_button(self):
        widget = UiWidgetCreator.create_layout_widget('add_illness', QtWidgets.QHBoxLayout())
        button = UiWidgetCreator.create_push_button('+', 'add_illness_button')
        button.clicked.connect(lambda: self.add_new_illness())
        widget.layout().addWidget(button)
        self.network_editor.illness_content.layout().addWidget(widget, 0, 0)
        
    def open_properties_input(self, properties: dict):
        line_edits = {}
        form_layout = UiWidgetCreator.create_layout_widget('illness_form', QtWidgets.QFormLayout())
        for p, v in properties.items():
            label = UiWidgetCreator.create_label(p, 'illness_label_properties')
            regex_validator = '^\d*\.\d+$'
            if p == 'name':
                regex_validator = '.*'
            if p == 'infection color':
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
            
        self.create_save_remove_button(form_layout)
        UiWidgetCreator.move_grid_widgets_right(self.network_editor.illness_content, 1, 4)
        self.network_editor.illness_content.layout().addWidget(form_layout, 0, 1)
        return line_edits
    
    def create_save_remove_button(self, form_layout):
        layout = UiWidgetCreator.create_layout_widget('handle_input_layout', QtWidgets.QHBoxLayout())
        save = UiWidgetCreator.create_push_button('save', 'save_illness_button')
        remove = UiWidgetCreator.create_push_button('remove', 'remove_illness_button')
        
        save.clicked.connect(lambda: self.save_input())
        remove.clicked.connect(lambda: self.remove_illness())
        
        layout.layout().addWidget(save)
        layout.layout().addWidget(remove)
        form_layout.layout().addWidget(layout)
        
    def save_input(self):
        pass
    
    def remove_illness(self):
        # TODO remove illness from list where it is saved
        UiWidgetCreator.pop_grid_widget_at(self.network_editor.illness_content, None)

    def insert_widget(self, widget, widget_to_insert):
        total_widgets = widget.layout().count()
        for i in range(total_widgets - 1, 0, -1):
            row, col, _, _ = widget.layout().getItemPosition(i)
            if col == 3:
                row += 1
                col = 0
            else:
                col += 1
            widget.layout().addWidget(widget.layout().itemAt(i).widget(), row, col)
        widget.layout().addWidget(widget_to_insert, 0, 1)
    def add_new_illness(self):
        default_dict = {'name': '', 'transmission rate': '', 'treatment time': '', 'immunity': '', 'infection color': ''}
        self.open_properties_input(default_dict)
        
        