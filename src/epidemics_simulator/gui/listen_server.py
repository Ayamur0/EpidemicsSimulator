from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from threading import Thread
from urllib.parse import urlparse, parse_qs
from PyQt5.QtCore import QThreadPool, QRunnable, QThread, Qt, QSize, pyqtSignal, QObject
import requests
from flask import Flask, request

app = Flask(__name__)
class WebServer(QObject):
    signal_update_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def run_server(self):
        app.run(host='localhost', port=8051)

    def start_server(self):
        self.server_thread = QThread()
        self.moveToThread(self.server_thread)
        self.server_thread.started.connect(self.run_server)
        self.server_thread.start()

        @app.route('/stat-update', methods=['POST'])
        def stat_update():
            data = request.get_json()
            if data:
                self.signal_update_received.emit(data)
                return 'Update received'
            else:
                return 'Invalid JSON data', 400
    def stop(self):
        self.server_thread.quit()
    