from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from PyQt5 import QtWidgets



class UiSimulationStats:
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.simulation_speed = 0
        self.network_editor.start_stop_button.clicked.connect(lambda: self.start_simulation())
        self.network_editor.reset_button.clicked.connect(lambda: self.reset_simulation())
        self.network_editor.decrease_button.clicked.connect(lambda: self.decrease_simulation_speed())
        self.network_editor.increase_button.clicked.connect(lambda: self.increase_simulation_speed())
            
    def load_info(self):
        test = {'name': 'Test', 'idk': 10, 'dddd': 1.2, 'other': 'other'}
        
        for i in range(0, 10):
            self.add_info_widget(test)
        
    def get_row_col(self, grid):
        row = grid.layout().count() // 4
        col = grid.layout().count() % 4
        return row, col
        
    def add_info_widget(self, properties: dict):
        form_layout = UiWidgetCreator.create_layout_widget('stat_form', QtWidgets.QFormLayout())
        for p, v in properties.items():
            prop_name = UiWidgetCreator.create_label(p, 'stat_label')
            prop_value = UiWidgetCreator.create_label(v, 'stat_label')
            form_layout.layout().addRow(prop_name, prop_value)
        row, col = self.get_row_col(self.network_editor.stats_content)
        self.network_editor.stats_content.layout().addWidget(form_layout, row, col)
        
    def update_simulation_label(self):
        pass
        
    def start_simulation(self):
        pass
    def stop_simulation(self):
        pass
    def increase_simulation_speed(self):
        pass
    def decrease_simulation_speed(self):
        pass
    def reset_simulation(self):
        pass
    
    def unload(self):
        self.network_editor.unload_items_from_layout(self.network_editor.stats_content.layout())