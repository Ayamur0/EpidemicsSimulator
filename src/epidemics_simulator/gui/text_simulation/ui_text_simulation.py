import os
import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, QRunnable
from PyQt5.QtWebEngineWidgets import *
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.storage import Network
from src.epidemics_simulator.simulation import Simulation
from src.epidemics_simulator.storage.sim_stats import SimStats
from src.epidemics_simulator.gui.flowlayout import FlowLayout

INCREASE_SPEED = "+"
START_STOP_SIMULATION = "s"
DECREASE_SPEED = "-"
RESET_SIMULATION = "r"
STOP_SIMULATION = "p"

class WorkerSignals(QObject):
    simulation_finished: pyqtSignal = pyqtSignal()
    update_speed: pyqtSignal = pyqtSignal(str)
    update_control_label_signal: pyqtSignal = pyqtSignal(float)
    update_label_signal: pyqtSignal = pyqtSignal(dict, int)
    no_network_groups: pyqtSignal = pyqtSignal()
    save_finished: pyqtSignal = pyqtSignal()
    simulation_started: pyqtSignal = pyqtSignal()
class SaveStats(QRunnable):
    def __init__(self, path: str, filename: str, stats, signals: WorkerSignals):
        super(SaveStats, self).__init__()
        self.path = path
        self.filename = filename
        self.stats = stats
        self.signals = signals
    def run(self):
        self.stats.to_csv(self.path, self.filename)
        self.signals.save_finished.emit()
        return

class SimulationWorker(QThread):
    max_speed = 256.0
    min_speed = 0.125
    def __init__(self, simulation: Simulation, signals = WorkerSignals) -> None:
        super(SimulationWorker, self).__init__()
        self.simulation = simulation
        self.signals = signals
        self.simulation_speed: float = 0.0
        self.current_step = 0
        self.stopped = False
        self.restart = False
        self.connect_signals()
        
    def connect_signals(self):
        self.signals.update_speed.connect(self.change_speed)
    
    def run(self):
        self.simulation.init_simulation()
        self.signals.update_label_signal.emit(self.simulation.stats.group_stats, self.current_step)
        while not self.stopped:
            if self.restart: # Doing this so after a restart an extra step cant occure
                self.restart = False   
                self.current_step = 0
                self.stop_simulation()
                self.simulation.init_simulation()
                self.signals.update_control_label_signal.emit(self.simulation_speed)
                self.signals.update_label_signal.emit(self.simulation.stats.group_stats, self.current_step)
                
            if self.simulation_speed == 0:
                time.sleep(0.2)
                continue
            time_interval = 1 / self.simulation_speed
            start_time = time.time()
            self.simulation.simulate_step()
            self.current_step += 1
            self.signals.update_label_signal.emit(self.simulation.stats.group_stats, self.current_step)
            elapsed_time = time.time() - start_time
            if elapsed_time < time_interval:
                time.sleep(time_interval - elapsed_time)
        self.signals.simulation_finished.emit()
    @pyqtSlot(str)
    def change_speed(self, action: str):
        if action == STOP_SIMULATION:
            self.stop_simulation()
            
        elif len(self.simulation.network.groups) == 0:
            self.signals.no_network_groups.emit()
            return
        elif action == INCREASE_SPEED:
            self.increase_speed()
        elif action == DECREASE_SPEED:
            self.decrease_speed()
        elif action == START_STOP_SIMULATION:
            self.start_stop_simulation()
        elif action == RESET_SIMULATION:
            self.reset()
        else:
            print("Wrong simulation action")
            return
        self.signals.update_control_label_signal.emit(self.simulation_speed)

    def increase_speed(self):
        self.simulation_speed *= 2 if self.simulation_speed < self.max_speed else 1
    def decrease_speed(self):
        self.simulation_speed /= 2  if self.simulation_speed > self.min_speed else 1
    def start_stop_simulation(self):
        if self.simulation_speed == 0:
            self.simulation_speed = 1
            self.signals.simulation_started.emit()
        else:
            self.simulation_speed = 0
        
    def stop_simulation(self):
        self.simulation_speed = 0
        
    def reset(self):
        self.restart = True
        
    def stop(self):
        self.stopped = True
        self.quit()
        self.wait()

class UiTextSimulationTab:
    def __init__(self, parent: QtWidgets.QMainWindow):
        self.parent = parent
        self.start_stop_button = self.parent.start_stop_button
        self.increase_button = self.parent.increase_button
        self.decrease_button = self.parent.decrease_button
        self.reset_button = self.parent.reset_button
        self.save_button = self.parent.save_button
        self.speed_label = self.parent.speed_label
        
        self.stats_content = self.parent.stats_content
        flow = FlowLayout(self.stats_content)
        self.stats_content.setLayout(flow)
        self.min_frame_size = (290, 320)  
        self.step_label = self.parent.step_label   
        self.worker_signals = WorkerSignals()
        
        self.stat_labels = {}
        self.thread_pool = self.parent.thread_pool
        self.simulation_started = False
        
        self.connect_signals()
        
    def connect_signals(self):  
        self.save_button.clicked.connect(lambda: self.save_simulation())
        self.start_stop_button.clicked.connect(lambda: self.worker_signals.update_speed.emit(START_STOP_SIMULATION))#self.start_stop_simulation())
        self.increase_button.clicked.connect(lambda: self.worker_signals.update_speed.emit(INCREASE_SPEED))#self.increase_simulation_speed())
        self.decrease_button.clicked.connect(lambda: self.worker_signals.update_speed.emit(DECREASE_SPEED))#self.decrease_simulation_speed())
        self.reset_button.clicked.connect(lambda: self.worker_signals.update_speed.emit(RESET_SIMULATION))#self.reset_simulation())
        
        self.worker_signals.update_label_signal.connect(self.update_stat_labels)
        self.worker_signals.update_control_label_signal.connect(self.update_control_labels)
        self.worker_signals.no_network_groups.connect(self.no_network_group)
        self.worker_signals.save_finished.connect(self.save_finsihed)
        self.worker_signals.simulation_started.connect(self.simulation_was_run)
        
        
    def init_ui(self, network: Network):
        self.network = network
        self.create_simulation_worker()
        
    def create_simulation_worker(self):
        self.simulation = Simulation(self.network)
        self.worker = SimulationWorker(self.simulation, self.worker_signals)
        self.worker.start()
        
    def restart_simulation(self):
        self.worker_signals.update_speed.emit(RESET_SIMULATION)
        
    def stop_simulation(self):
        self.worker_signals.update_speed.emit(STOP_SIMULATION)
        
    def no_network_group(self):
        message = UiWidgetCreator.show_qmessagebox(f"The network has no groups.\nCreate network groups to start a simulation.", "No Network Groups", only_ok=True)
        _ = message.exec_()
        return
    def simulation_was_run(self):
        self.simulation_started = True
        
    def update_stat_labels(self, group_stats: dict, current_step: int):
        self.step_label.setText(f"Step: {current_step}")
        for group, stat in group_stats.items():
            properties = self.log_text_to_json(stat.get_log_text())
            if group not in self.stat_labels.keys():
                self.stat_labels[group] = self.add_properties(properties)
            self.update_widgets(self.stat_labels[group], properties)
        
    def add_properties(self, properties: dict):
        base_widget, _, _, label_widget, input_widget = UiWidgetCreator.create_input_layout_widgets()
        widget_dict = {}
        i = 0
        for key, value in properties.items():
            color = self.parent.create_alternate_line_color(i)
            i += 1
            prop_name = UiWidgetCreator.create_input_label(key, color)
            prop_value = UiWidgetCreator.create_input_label(value, color)
            widget_dict[key] = prop_value
            label_widget.layout().addWidget(prop_name)
            input_widget.layout().addWidget(prop_value)
        self.stats_content.layout().addWidget(base_widget)
        return widget_dict
    
    def update_widgets(self, widgets: dict, properties: dict):
        for key, widget in widgets.items():
            widget.setText(str(properties[key]))
            
    def update_control_labels(self, simulation_speed: float):
        if simulation_speed >= 1 or simulation_speed == 0:
            self.speed_label.setText(f"Simulation speed: {int(simulation_speed)} t/s")
        else:
            self.speed_label.setText(f"Simulation speed: {simulation_speed} t/s")
        if simulation_speed == 0:
            self.start_stop_button.setIcon(self.parent.start_icon)
        else:
            self.start_stop_button.setIcon(self.parent.stop_icon)
            
    def log_text_to_json(self, log_text: str):
        stat = {}
        for line in log_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            split_line = line.split(":")
            if len(split_line) != 2:
                continue
            stat[split_line[0].strip()] = split_line[1].strip()
        return stat
    
    def save_simulation(self):
        if not self.simulation_started:
            return
        self.worker_signals.update_speed.emit(STOP_SIMULATION)
        name = UiWidgetCreator.open_save_sim_popup(self.parent)
        if not name:
            return
        is_valid, reason = SimStats.is_valid_file_name(name)
        if not is_valid:
            msg_box = UiWidgetCreator.show_qmessagebox(reason, "Invalid Filename", only_ok=True)
            msg_box.exec_()
            return
            
        simulation_stats = self.simulation.stats
        self.stats_update(name, simulation_stats)
        
    def stats_update(self, filename, stats):
        self.popup = UiWidgetCreator.create_generate_popup(self.parent, content="Saving...")
        thread = SaveStats(os.path.join(self.parent.project.file_location, "stats"), filename, stats, self.worker_signals)
        self.thread_pool.start(thread)
        self.popup.exec_()
    
    def save_finsihed(self):
        self.parent.push_to_dash(reset_view=True)
        print("Saving finished")
        self.popup.deleteLater()
        
    def kill_worker(self):
        try:
            self.worker_signals.update_speed.emit(STOP_SIMULATION)
            self.worker.stop()
            self.worker.deleteLater()  # Explicitly delete the worker
        except AttributeError:
            pass
        except RuntimeError:
            pass
        
    def clear_stats_widgets(self):
        self.stat_labels.clear()
        self.parent.unload_items_from_layout(self.stats_content.layout())
        
    def unload(self):
        self.clear_stats_widgets()
        self.simulation_started = False
        self.kill_worker()