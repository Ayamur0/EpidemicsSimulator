import time
from urllib.parse import urljoin
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QObject
import subprocess
import psutil
import requests
import os
import sys

import urllib3


class WorkerSignals(QObject):
    server_startet: pyqtSignal = pyqtSignal(subprocess.Popen)
    server_connected: pyqtSignal = pyqtSignal()
    server_updated: pyqtSignal = pyqtSignal()
    server_not_responding: pyqtSignal = pyqtSignal()


class StartServer(QRunnable):
    def __init__(self, url: str, signal):
        super(StartServer, self).__init__()
        self.server_url = url
        self.signal = signal
        
        self.exe_path = os.path.join(os.getcwd(), 'webview', 'launch_webview.exe')
        print(self.exe_path)
        
        

    def run(self):
        try:
            response = requests.head(self.server_url, timeout=1)
            # Check if the response status code is in the 2xx range (success)
            if response.status_code // 100 == 2:
                self.signal.server_connected.emit()
                print("Server already running.")
                return
        except requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout:
            pass
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            
            if os.path.exists(self.exe_path):
                print('Starting server from .exe')
                execution_command = self.exe_path
            else:
                print('Starting server from .py')
                activate_script = os.path.join(
                "venv", "Scripts" if sys.platform == "win32" else "bin", "activate"
                )
                execution_command = [activate_script, "&&", "python", "launch_webview.py"]

            process = subprocess.Popen(
                execution_command,
                stdout=subprocess.PIPE,
                shell=True,
                executable=os.environ.get("SHELL"),
                creationflags=creation_flags,
            )

            self.signal.server_startet.emit(process)
        except Exception as e:
            print(f"Error starting server: {e}")
            return None


class CheckConnection(QRunnable):
    def __init__(self, url, signal):
        super(CheckConnection, self).__init__()
        self.url = url
        self.signal = signal
        self.stopped = False

    def run(self):
        connected = False
        while not connected:
            if self.stopped:
                return
            try:
                response = requests.head(self.url, timeout=5)
                # Check if the response status code is in the 2xx range (success)
                if response.status_code // 100 == 2:
                    connected = True
            except (
                requests.exceptions.ConnectionError or requests.exceptions.ReadTimeout
            ):  # or urllib3.exceptions.ReadTimeoutError:
                print("Error Connecting")
                time.sleep(1)
        
        self.signal.server_connected.emit()
        
    def stop(self):
        self.stopped = True

class PushToDash(QRunnable):
    def __init__(self, data: dict, url: str, signal):
        super(PushToDash, self).__init__()
        self.url = url
        self.data = data
        self.signal = signal

    def run(self):
        try:
            response = requests.post(self.url, json=self.data)

            # Check the response
            if response.status_code == 200:
                print("POST request successful")
            else:
                print(f"POST request failed with status code {response.status_code}")
                print(response.json())
                print(self.data)
        except requests.ConnectionError:
            self.signal.server_not_responding.emit()
            pass
        except Exception as e:
            print(f"An error occurred: {e}")
        self.signal.server_updated.emit()


class WebsiteHandler(QObject):
    start_server: pyqtSignal = pyqtSignal()
    check_connection: pyqtSignal = pyqtSignal()
    push_to_dash: pyqtSignal = pyqtSignal(str, dict)
    kill: pyqtSignal = pyqtSignal()

    def __init__(
        self,
        parent,
        base_url: str,
    ):
        super(WebsiteHandler, self).__init__()
        self.parent = parent
        self.base_url = base_url
        self.is_connected = False
        self.is_checking_connection = False
        self.server_process = None
        self.thread_pool = self.parent.thread_pool
        self.worker_signals = WorkerSignals()

        self.connect_signals()

    def connect_signals(self):
        self.start_server.connect(self.start_server_thread)
        self.check_connection.connect(self.check_server_connection_thread)
        self.push_to_dash.connect(self.update_server_data_thread)
        self.kill.connect(self.kill_server)

        self.worker_signals.server_startet.connect(self.set_process)
        self.worker_signals.server_connected.connect(self.connection_established)
        self.worker_signals.server_updated.connect(self.data_updated)
        self.worker_signals.server_not_responding.connect(self.check_server_connection_thread)

    @pyqtSlot()
    def start_server_thread(self):
        if self.is_connected:
            return
        print("Starting Sever.")
        thread = StartServer(self.base_url, self.worker_signals)
        self.thread_pool.start(thread)
        self.check_server_connection_thread()

    @pyqtSlot(subprocess.Popen)
    def set_process(self, process: subprocess.Popen):
        self.server_process = process
        print(f"Server process started: {self.server_process.pid}.")

    @pyqtSlot()
    def check_server_connection_thread(self):
        if (
            self.is_checking_connection
            or self.parent.network_edit_tab.group_display.generation_in_progress
        ):
            return
        self.parent.show_webviews.emit(False)
        print("Checking server connection.")
        self.is_checking_connection = True
        self.is_connected = False
        thread = CheckConnection(self.base_url, self.worker_signals)
        self.thread_pool.start(thread)
        self.parent.threads.append(thread)

    @pyqtSlot()
    def connection_established(self):
        print("Connection established.")
        self.is_checking_connection = False
        self.is_connected = True
        self.parent.push_to_dash()
        self.parent.show_webviews.emit(True)
        self.parent.remove_sender_from_threads(self.sender())

    @pyqtSlot(str, dict)
    def update_server_data_thread(self, sub_url: str, data: dict):
        if not self.is_connected:
            return
        url = urljoin(self.base_url, sub_url)
        print("Starting to push data to dash.")
        thread = PushToDash(data, url, self.worker_signals)
        self.thread_pool.start(thread)

    @pyqtSlot()
    def data_updated(self):
        print("Data pushed to dash.")

    @pyqtSlot()
    def kill_server(self):
        if not self.server_process:
            return
        print("Stopping server.")
        proc_pid = self.server_process.pid
        # Source: https://stackoverflow.com/a/25134985
        try:
            process = psutil.Process(proc_pid)  #
        except psutil.NoSuchProcess:
            return
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()
