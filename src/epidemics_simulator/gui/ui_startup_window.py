from functools import partial
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from src.epidemics_simulator.gui.ui_widget_creator import UiWidgetCreator
from src.epidemics_simulator.gui.templates import templates

class UiStartupWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.resize(300, 600)
        
        layout = UiWidgetCreator.create_layout_widget('startup_layout', QtWidgets.QVBoxLayout())
        self.setLayout(layout.layout())
        self.create_startup_buttons()
        
        
    def create_startup_buttons(self):
        self.parent.unload_items_from_layout(self.layout())
        new = UiWidgetCreator.create_push_button('New', 'new_network')
        new_from_template = UiWidgetCreator.create_push_button('New from Template', 'new_network')
        open_network = UiWidgetCreator.create_push_button('Open', 'open_network')
        
        new.clicked.connect(lambda: self.new_network())
        new_from_template.clicked.connect(lambda: self.new_from_template())
        open_network.clicked.connect(lambda: self.open_network())
        
        self.layout().addWidget(new)
        self.layout().addWidget(new_from_template)
        self.layout().addWidget(open_network)
        
        
   
    def new_from_template(self):
        self.parent.unload_items_from_layout(self.layout())
           
        for i in range(0, len(templates)):
            template = templates[i]
            template = UiWidgetCreator.create_push_button(template.name, 'new_network')
            template.clicked.connect(partial(self.new_template_network, i))
            self.layout().addWidget(template)
        back = UiWidgetCreator.create_push_button('Back', 'back_button')
        back.clicked.connect(lambda: self.create_startup_buttons())
        self.layout().addWidget(back)
        
    def new_network(self):
        if not self.parent.new_network(self):
            return
        self.close_startup()
        
    def new_template_network(self, template_id):
        if not self.parent.new_network(self, template_id):
            return
        self.close_startup()
        
    def open_network(self):
        if not self.parent.open_network(self):
            return
        self.close_startup()
        
            
    def close_startup(self):
        self.parent.show()
        self.close()
