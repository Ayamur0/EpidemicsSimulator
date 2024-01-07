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
app.exec_()
#server_thread.join()