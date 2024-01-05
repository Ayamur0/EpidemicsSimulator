import os
import subprocess
from threading import Thread
import threading
import atexit
from PyQt5 import QtWidgets
import sys
from gui import UiNetworkEditor
from storage import Network, NodeGroup
from src.epidemics_simulator.storage.disease import Disease

from src.epidemics_simulator.visualization.dash_server import DashServer
from src.epidemics_simulator.storage import Network, Project
test_data = Network()
g1 = NodeGroup(test_data, "Group1", 53, 58, 0.54, 0.3, 14, 2, '#ff3541')
g2 = NodeGroup(test_data, "Group2", 87, 12, 0.62, 0.4, 12, 7,'#115577')
g3 = NodeGroup(test_data, "Group3", 69, 7, 0.78, 0.7, 15, 3,'#acde75')
g4 = NodeGroup(test_data, "Group4", 27, 3, 0.34, 1, 11, 5, '#ffffff')
g5 = NodeGroup(test_data, "Group5", 71, 24, 0.55, 0.4, 13, 4, '#f74532')



test_data.add_group(g1)
test_data.add_group(g2)
test_data.add_group(g3)
test_data.add_group(g4)
test_data.add_group(g5)

g1.add_external_connection(g2.id, 5, 3)

#test_data.diseases.append(Disease('D1'))
#test_data.diseases.append(Disease('D2'))
#test_data.diseases.append(Disease('D3'))
#test_data.diseases.append(Disease('D4'))
#test_data.diseases.append(Disease('D5'))

def execute_file_in_process():
    try:
        # Activate the virtual environment in the subprocess
        activate_script = os.path.join('venv', 'Scripts' if sys.platform == 'win32' else 'bin', 'activate')
        activate_command = f'"{activate_script}" && python test/test_visualization.py'
        
        subprocess.run(activate_command, shell=True, check=True, executable=os.environ.get('SHELL'))
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        
#server_thread = threading.Thread(target=execute_file_in_process)# Register a function to terminate the subprocess when the main program exits
#atexit.register(lambda: server_thread.terminate() if server_thread.is_alive() else None)
#server_thread.start()
app = QtWidgets.QApplication(sys.argv)
window = UiNetworkEditor()
#window.load_network(test_data)
app.exec_()
#server_thread.join()