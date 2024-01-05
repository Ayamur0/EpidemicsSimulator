import time
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from src.epidemics_simulator.simulation import Simulation
from src.epidemics_simulator.storage.networks import Network
class Worker(QThread):
    finished = pyqtSignal()
    max_speed = 256.0
    min_speed = 0.125
    def __init__(self, simulation: Simulation, ui_sim) -> None:
        super().__init__()
        self.simulation = simulation
        self.ui_sim = ui_sim
        self.simulation_speed = 0
        self.current_step = 0
        self.stopped = False
        
    def run(self):
        self.simulation.init_simulation()
        while not self.stopped:
            if self.simulation_speed == 0:
                time.sleep(0.2)
                continue
            time_interval = 1 / self.simulation_speed
            start_time = time.time()
            self.simulation.simulate_step()
            self.current_step += 1
            
            self.ui_sim.update_stat_labels(self.simulation.stats.group_stats, self.current_step)
            elapsed_time = time.time() - start_time
            if elapsed_time < time_interval:
                time.sleep(time_interval - elapsed_time)
        self.finished.emit()
    
        
    def update_stat_widget(self, widgets, properties: dict):
        for key, prop in widgets.items():
            prop.setText(str(properties[key]))
            
    def stop_simulation(self):
        self.simulation_speed = 0
        self.update_control_labels()
        
    def start_stop(self):
        self.simulation_speed = 1 if self.simulation_speed == 0 else 0
        self.update_control_labels()
        
    def increase_speed(self):
        self.simulation_speed *= 2 if self.simulation_speed < Worker.max_speed else 1
        self.update_control_labels()
        
    def decrease_speed(self):
        self.simulation_speed /= 2 if self.simulation_speed > Worker.min_speed else 1
        self.update_control_labels()
        
    def update_control_labels(self):
        if self.simulation_speed >= 1:
            self.ui_sim.network_editor.speed_label.setText(f'Simulation speed: {int(self.simulation_speed)}')
        else:
            self.ui_sim.network_editor.speed_label.setText(f'Simulation speed: {self.simulation_speed}')
        if self.simulation_speed == 0:
            self.ui_sim.network_editor.start_stop_button.setText('Start')
        else:
            self.ui_sim.network_editor.start_stop_button.setText('Stop')
        
        
        
    def stop(self):
        self.stopped = True
        self.quit()
        self.wait()


class UiSimulationStats:
    
    def __init__(self, network_editor) -> None:
        self.network_editor = network_editor
        self.network_editor.start_stop_button.clicked.connect(lambda: self.start_stop_simulation())
        self.network_editor.reset_button.clicked.connect(lambda: self.reset_simulation())
        self.network_editor.decrease_button.clicked.connect(lambda: self.decrease_simulation_speed())
        self.network_editor.increase_button.clicked.connect(lambda: self.increase_simulation_speed())
        self.stat_labels = {}
        
    def create_worker(self):
        self.simulation = Simulation(self.network_editor.current_network)
        self.worker = Worker(self.simulation, self)
            
    def load_info(self):
        self.create_worker()
        self.update_stat_labels(self.worker.simulation.stats.group_stats, self.worker.current_step)
        self.worker.start()  
        
    def get_row_col(self, grid):
        row = grid.layout().count() // 4
        col = grid.layout().count() % 4
        return row, col
        
    def add_info_widget(self, properties: dict):
        #info_widget = UiWidgetCreator.create_layout_widget('info_widget', QtWidgets.QVBoxLayout())
        #info_widget.layout().stretch(0)
        #info_widget.layout().setContentsMargins(0, 0, 0, 0)
        #info_widget.layout().setSpacing(0)
        form_layout = UiWidgetCreator.create_layout_widget('stat_form', QtWidgets.QFormLayout())
        #form_layout.layout().setSpacing(0)
        widget_dict = {}
        for p, v in properties.items():
            #if p == 'Name':
            #    label = UiWidgetCreator.create_label(v, 'group_name')
            #    label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
            #    info_widget.layout().addWidget(label)
            #    continue
            prop_name = UiWidgetCreator.create_label(p, 'stat_label')
            prop_value = UiWidgetCreator.create_label(v, 'stat_label')
            widget_dict[p] = prop_value
            form_layout.layout().addRow(prop_name, prop_value)
        row, col = self.get_row_col(self.network_editor.stats_content)
        #info_widget.layout().addWidget(form_layout) # comment was for trying to use the group name as a caption (did not work (had spacing and so what))
        self.network_editor.stats_content.layout().addWidget(form_layout, row, col)
        return widget_dict
    
    def update_widgets(self, widgets: dict, properties: dict):
        for key, widget in widgets.items():
            widget.setText(str(properties[key]))
        
    def update_stat_labels(self, group_stats: dict, current_step):
        self.network_editor.step_label.setText(f'Step: {current_step}')
        for group, stat in group_stats.items():
            json_stat = self.convert_log_text_to_json(stat.get_log_text())
            if group not in self.stat_labels.keys():
                self.stat_labels[group] = self.add_info_widget(json_stat)
            self.update_widgets(self.stat_labels[group], json_stat)
            
    def convert_log_text_to_json(self, log_text: str):
        stat = {}
        for line in log_text.split('\n'):
            line = line.strip()
            if not line:
                continue
            split_line = line.split(':')
            if len(split_line) != 2:
                continue
            stat[split_line[0].strip()] = split_line[1].strip()
        return stat
        
    def stop_simulation(self):
        self.worker.stop_simulation()
    def start_stop_simulation(self):
        self.worker.start_stop()
    def increase_simulation_speed(self):
        self.worker.increase_speed()
    def decrease_simulation_speed(self):
        self.worker.decrease_speed()
    def reset_simulation(self):
        self.unload()
        self.load_info()
        
        
    def stop_worker(self):
        try:
            self.worker.stop()
            self.worker.deleteLater()  # Explicitly delete the worker
        except AttributeError:
            pass
        except RuntimeError:
            pass
    
    def unload(self):
        self.stop_worker()
        self.stat_labels = {}
        self.network_editor.unload_items_from_layout(self.network_editor.stats_content.layout())
        