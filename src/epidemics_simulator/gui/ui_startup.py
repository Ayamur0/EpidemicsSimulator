from functools import partial
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.gui.templates import templates

class UiStartup(QtWidgets.QDialog):
    launch_startup: pyqtSignal = pyqtSignal()
    close_startup: pyqtSignal = pyqtSignal()
    def __init__(self, parent):
        super(UiStartup, self).__init__()
        self.parent = parent
        self.setWindowTitle('Network tool')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(parent.styleSheet())
        self.resize(250, 400)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.default_alignment = self.layout().alignment()
        # Icon Sourced: https://www.flaticon.com/
        self.back_icon = QIcon('assets/back.png')
        
        self.continue_to_main_window = False
        
        self.connect_signals()
        
    def connect_signals(self):
        self.launch_startup.connect(self.launch)
        self.close_startup.connect(self.startup_finished)
        
    @pyqtSlot()
    def launch(self):
        self.parent.hide()
        self.main_buttons()
        self.show()

    def main_buttons(self):
        self.parent.unload_items_from_layout(self.layout())
        self.layout().setAlignment(self.default_alignment)
        new_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button('New', 'new_network_button')
        new_from_template_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button('New from template', 'new_template_button')
        open_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button('Open', 'open_network_button')
        
        new_button.clicked.connect(lambda: self.parent.new_project.emit(-1))
        new_from_template_button.clicked.connect(lambda: self.new_from_template())
        open_button.clicked.connect(lambda: self.parent.open_project.emit())
        
        self.layout().addWidget(new_button)
        self.layout().addWidget(new_from_template_button)
        self.layout().addWidget(open_button)
        
    @pyqtSlot()
    def new_from_template(self):
        self.parent.unload_items_from_layout(self.layout())
        # self.layout().setAlignment(Qt.AlignTop)
        for i in range(0, len(templates)):
            template = templates[i]
            template = UiWidgetCreator.create_qpush_button(template.name, 'new_network')
            template.clicked.connect(partial(self.parent.new_project.emit, i))
            self.layout().addWidget(template)
        back = UiWidgetCreator.create_qpush_button(None, 'back_button')
        back.setIcon(self.back_icon)
        back.clicked.connect(lambda: self.main_buttons())
        self.layout().addWidget(back)
    @pyqtSlot()
    def startup_finished(self):
        self.continue_to_main_window = True
        self.parent.show()
        self.close()
        

    def closeEvent(self, event):
        if not self.continue_to_main_window:
            self.parent.website_handler.kill.emit()
        event.accept()
