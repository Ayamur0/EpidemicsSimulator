from functools import partial
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot, QSize
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.gui.templates import templates

class UiStartup(QtWidgets.QDialog):
    launch_startup: pyqtSignal = pyqtSignal()
    close_startup: pyqtSignal = pyqtSignal()
    def __init__(self, parent):
        super(UiStartup, self).__init__()
        self.parent = parent
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("Epidemic Simulator")
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet(parent.styleSheet())
        self.setFixedSize(300, 450)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)
        
        self.font = QFont()
        self.font.setPointSize(15)
        
        self.default_alignment = self.layout().alignment()
        # Icon Sources: https://www.flaticon.com/
        self.window_icon = self.parent.window_icon
        self.new_icon = self.parent.new_icon
        self.template_icon = self.parent.template_icon
        self.open_icon = self.parent.open_icon
        self.back_icon = self.parent.back_icon
        
        self.icon_size = QSize(48, 48)
        
        self.setWindowIcon(self.window_icon)
        
        self.button_style = "border-radius: 0px;text-align: left;padding-left: 10px;"
        
        self.button_size_policy = (QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding) 
        
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
        new_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(" New", "new_network_button", style_sheet=self.button_style, icon=self.new_icon)
        new_from_template_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(" New from template", "new_template_button", style_sheet=self.button_style, icon=self.template_icon)
        open_button: QtWidgets.QPushButton = UiWidgetCreator.create_qpush_button(" Open", "open_network_button", style_sheet=self.button_style, icon=self.open_icon)
        
        new_button.setIconSize(self.icon_size)
        new_from_template_button.setIconSize(self.icon_size)
        open_button.setIconSize(self.icon_size)
        
        new_button.setFont(self.font)
        new_from_template_button.setFont(self.font)
        open_button.setFont(self.font)
        
        new_button.setSizePolicy(*self.button_size_policy) 
        new_from_template_button.setSizePolicy(*self.button_size_policy) 
        open_button.setSizePolicy(*self.button_size_policy) 
        
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
        back = UiWidgetCreator.create_qpush_button(None, "back_button", style_sheet=self.button_style, icon=self.back_icon)
        back.setFont(self.font)
        back.setIconSize(QSize(32, 32))
        back.setSizePolicy(*self.button_size_policy) 
        back.clicked.connect(lambda: self.main_buttons())
        self.layout().addWidget(back)
        for i in range(0, len(templates)):
            template = templates[i]
            template = UiWidgetCreator.create_qpush_button(template.name, "new_network", style_sheet=self.button_style)
            template.setFont(self.font)
            template.setSizePolicy(*self.button_size_policy) 
            template.clicked.connect(partial(self.parent.new_project.emit, i))
            self.layout().addWidget(template)
        
    @pyqtSlot()
    def startup_finished(self):
        self.continue_to_main_window = True
        self.parent.show()
        self.close()

    def closeEvent(self, event):
        if not self.continue_to_main_window:
            self.parent.closeEvent(event)
            # self.parent.website_handler.kill.emit()
        event.accept()
