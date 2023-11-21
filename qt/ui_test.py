from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
import sys


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi("qt/NetworkEdit/main.ui", self)  # Load the .ui file
        self.pushButton.clicked.connect(self.add_dummy_data)
        self.show()  # Show the GUI

    def add_dummy_data(self):
        groups = {
            "Group 1": True,
            "Group 2": False,
            "More Groups": True,
            "Red": False,
            "Old": False,
            "More": True,
        }
        properties = {
            "Age": 54,
            "Member amount": 87,
            "Internal Connections": 10,
            "Internal delta": 4,
            "More stuff": 4,
            "Something else": 8,
        }
        # vbox = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        for s, b in groups.items():
            item = QtWidgets.QWidget()
            item.setLayout(QtWidgets.QHBoxLayout())
            radio_btn = QtWidgets.QRadioButton()
            radio_btn.setChecked(b)
            item.layout().addWidget(radio_btn)
            item.layout().addWidget(QtWidgets.QLabel(s))
            self.group_list_content.layout().addWidget(item)

        for p, v in properties.items():
            item = QtWidgets.QWidget()
            item.setLayout(QtWidgets.QHBoxLayout())
            label = QtWidgets.QLabel(p)
            label.sizePolicy().setHorizontalStretch(2)
            label.sizePolicy().setHorizontalPolicy(
                QtWidgets.QSizePolicy.Policy.Preferred
            )
            item.layout().addWidget(label)
            input = QtWidgets.QLineEdit()
            input.setText(str(v))
            # input.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding))
            input.sizePolicy().setHorizontalStretch(3)
            input.sizePolicy().setHorizontalPolicy(
                QtWidgets.QSizePolicy.Policy.Expanding
            )
            item.layout().addWidget(input)
            self.group_properties_content.layout().addWidget(item)


app = QtWidgets.QApplication(sys.argv)
window = Ui()
window.add_dummy_data()
app.exec_()
