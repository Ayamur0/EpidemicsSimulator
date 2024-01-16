import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import *
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network
from src.epidemics_simulator.simulation import Simulation
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDesktopServices
from src.epidemics_simulator.gui.flowlayout import FlowLayout


class GenerateNetwork(QThread):
    finished = pyqtSignal()
    update_label_signal = pyqtSignal(dict, int)
    update_control_label_signal = pyqtSignal(float)
    max_speed = 256.0
    min_speed = 0.125
    def __init__(self, simulation: Simulation) -> None:
        super().__init__()
        self.simulation = simulation
        self.simulation_speed: float = 0.0
        self.current_step = 0
        self.stopped = False
        self.restart = False
        
    def run(self):
        self.simulation.init_simulation()  
        self.update_label_signal.emit(self.simulation.stats.group_stats, self.current_step)
        while not self.stopped:
            if self.restart: # Doing this so after a restart an extra step cant occure
                self.restart = False   
                self.current_step = 0
                self.stop_simulation()
                self.simulation.init_simulation()
                
                self.update_label_signal.emit(self.simulation.stats.group_stats, self.current_step)
            if self.simulation_speed == 0:
                time.sleep(0.2)
                continue
            time_interval = 1 / self.simulation_speed
            start_time = time.time()
            self.simulation.simulate_step()
            self.current_step += 1
            self.update_label_signal.emit(self.simulation.stats.group_stats, self.current_step)
            elapsed_time = time.time() - start_time
            if elapsed_time < time_interval:
                time.sleep(time_interval - elapsed_time)
        self.finished.emit()
        
    def stop_simulation(self):
        self.simulation_speed = 0
        self.update_control_label_signal.emit(self.simulation_speed)
        
    def start_stop(self):
        self.simulation_speed = 1 if self.simulation_speed == 0 else 0
        self.update_control_label_signal.emit(self.simulation_speed)
        
    def increase_speed(self):
        self.simulation_speed *= 2 if self.simulation_speed < GenerateNetwork.max_speed else 1
        self.update_control_label_signal.emit(self.simulation_speed)
        
    def decrease_speed(self):
        self.simulation_speed /= 2  if self.simulation_speed > GenerateNetwork.min_speed else 1
        self.update_control_label_signal.emit(self.simulation_speed)
        
    def restart_simulation(self):
        self.restart = True
        
    def stop(self):
        self.stopped = True
        self.quit()
        self.wait()

class UiTextSimulationTab:
    def __init__(self, main_window: QtWidgets.QMainWindow):
        self.main_window = main_window
                
        self.start_stop_button = self.main_window.start_stop_button
        #self.start_stop_button.setText(None)
        #self.start_stop_button.setIcon(self.main_window.start_icon)
        self.increase_button = self.main_window.increase_button
        #self.increase_button.setText(None)
        #self.increase_button.setIcon(self.main_window.forward_icon)
        self.decrease_button = self.main_window.decrease_button
        #self.decrease_button.setText(None)
        #self.decrease_button.setIcon(self.main_window.rewind_icon)
        self.reset_button = self.main_window.reset_button
        #self.reset_button.setText(None)
        #self.reset_button.setIcon(self.main_window.restart_icon)
        self.save_button = self.main_window.save_button
        #self.save_button.setText(None)
        #self.save_button.setIcon(self.main_window.save_icon)
        
        self.tab_widget = self.main_window.simulation_stats
        
        self.save_button.clicked.connect(lambda: self.save_simulation())
        self.start_stop_button.clicked.connect(lambda: self.start_stop_simulation())
        self.increase_button.clicked.connect(lambda: self.increase_simulation_speed())
        self.decrease_button.clicked.connect(lambda: self.decrease_simulation_speed())
        self.reset_button.clicked.connect(lambda: self.reset_simulation())
        
        self.speed_label = self.main_window.speed_label
        
        self.stats_content = self.main_window.stats_content
        flow = FlowLayout(self.stats_content)
        self.stats_content.setLayout(flow)
        self.disease_layout_list = []
        self.min_frame_size = (290, 320)  
        self.step_label = self.main_window.step_label   
        
        self.simuilation_started = False
        self.stat_labels = {}
        
    def init_ui(self, network: Network):
        self.network = network
        self.create_simulation_worker(self.network)
        self.start_worker()
    
    def create_simulation_worker(self, network: Network):
        self.simulation = Simulation(network)
        self.worker = GenerateNetwork(self.simulation)
        self.worker.update_label_signal.connect(self.update_stat_labels)
        self.worker.update_control_label_signal.connect(self.update_control_labels)
        
    def start_worker(self):
        if len(self.network.groups) == 0:
            return # TODO message that no network exists
        self.simuilation_started = True
        self.worker.start()
        
    def update_stat_labels(self, group_stats: dict, current_step: int):
        self.step_label.setText(f'Step: {current_step}')
        for group, stat in group_stats.items():
            properties = self.log_text_to_json(stat.get_log_text())
            if group not in self.stat_labels.keys():
                self.stat_labels[group] = self.add_properties(properties)
            self.update_widgets(self.stat_labels[group], properties)

    def add_properties(self, properties: dict):
        base_widget, _, _, label_widget, input_widget = UiWidgetCreator.create_input_layout_widgets()
        #form_widget = UiWidgetCreator.create_qwidget('stat_form', QtWidgets.QFormLayout)
        widget_dict = {}
        i = 0
        for key, value in properties.items():
            if i % 2 == 0:
                color = 'rgb(65, 65, 65)'
            else:
                color = 'rgb(80, 80, 80)'
            i += 1
            prop_name = UiWidgetCreator.create_input_label(key, color)
            prop_value = UiWidgetCreator.create_input_label(value, color)
            widget_dict[key] = prop_value
            label_widget.layout().addWidget(prop_name)
            input_widget.layout().addWidget(prop_value)
        self.stats_content.layout().addWidget(base_widget)
        #for key, value in properties.items():
        #    prop_name = UiWidgetCreator.create_qlabel(key, 'stat_label')
        #    prop_value = UiWidgetCreator.create_qlabel(value, 'stat_label')
        #    widget_dict[key] = prop_value
        #    form_widget.layout().addRow(prop_name, prop_value)
        #row, col = self.get_row_col(self.stats_content)
        #form_widget.setMinimumSize(*self.min_frame_size)
        #self.stats_content.layout().addWidget(form_widget)
        #self.stats_content.layout().addWidget(form_widget, row, col)
        return widget_dict
    def update_widgets(self, widgets: dict, properties: dict):
        for key, widget in widgets.items():
            widget.setText(str(properties[key]))

    def get_row_col(self, grid):
        row = grid.layout().count() // 4
        col = grid.layout().count() % 4
        return row, col

    def update_control_labels(self, simulation_speed: float):
        if simulation_speed >= 1 or simulation_speed == 0:
            self.speed_label.setText(f'Simulation speed: {int(simulation_speed)}t/s')
        else:
            self.speed_label.setText(f'Simulation speed: {simulation_speed}t/s')
        if simulation_speed == 0:
            self.start_stop_button.setIcon(self.main_window.start_icon)
            #self.start_stop_button.setText('Start')
        else:
            self.start_stop_button.setIcon(self.main_window.stop_icon)
            #self.start_stop_button.setText('Stop')
            
    def log_text_to_json(self, log_text: str):
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
    
    def start_stop_simulation(self):
        if not self.simuilation_started:
            return
        self.worker.start_stop()
        pass
    def increase_simulation_speed(self):
        if not self.simuilation_started:
            return
        self.worker.increase_speed()
    def decrease_simulation_speed(self):
        if not self.simuilation_started:
            return
        self.worker.decrease_speed()
    def reset_simulation(self):
        if not self.simuilation_started:
            self.start_worker()
        self.clear_stats_widgets()
        self.worker.restart_simulation()
        self.main_window.changed_disease = False
        
    def stop_simulation(self):
        try:
            self.worker.stop_simulation()
        except AttributeError:
            pass
        
    def stop_worker(self):
        try:
            self.worker.stop_simulation()
            self.worker.stop()
            self.worker.deleteLater()  # Explicitly delete the worker
        except AttributeError:
            pass
        except RuntimeError:
            pass
        
    def ask_for_regeneration(self):
        if len(self.network.groups) == 0:
            return
        msg_box  = UiWidgetCreator.show_message(f'Network has not been generated. Do you want to generate the network', 'Regenerate network', default_button=0)
        result = msg_box.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return 
        
        #self.main_window.network_edit_tab.group_display.start_generating(self.network)
        self.main_window.network_edit_tab.group_display.generate_button.click()
        self.reset_simulation()
    
    def ask_for_reset(self):
        if len(self.network.groups) == 0:
            return
        msg_box  = UiWidgetCreator.show_message(f'Diseases chagned do you want to restart the simulation?', 'Restart simulation', default_button=0)
        result = msg_box.exec_()
        if result != QtWidgets.QMessageBox.AcceptRole:
            return 
        self.main_window.network_edit_tab.group_display.start_generating(self.network, generate_local=True)
        # self.main_window.network_edit_tab.group_display.generate_button.click()
        self.reset_simulation()
        
    def save_simulation(self):
        name = UiWidgetCreator.open_save_sim_popup()
        if not name:
            return
        simulation_stats = self.simulation.stats
        data = {'filename': name, 'stats': simulation_stats.to_dict()}
        
        self.main_window.stats_update(data)
        self.main_window.push_to_dash(data=data, sub_url='update-stats')
        
    def clear_stats_widgets(self):
        self.stat_labels.clear()
        self.main_window.unload_items_from_layout(self.stats_content.layout())
        
    def unload(self):
        self.clear_stats_widgets()
        self.simuilation_started = False
        self.stop_worker()
