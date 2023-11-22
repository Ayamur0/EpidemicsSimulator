from PyQt5 import QtWidgets, uic
import sys
from storage import Network, NodeGroup


class UiNetworkEditor(QtWidgets.QMainWindow):
    def __init__(self):
        super(UiNetworkEditor, self).__init__()
        uic.loadUi("qt/NetworkEdit/main.ui", self)
        self.group_widgets: dict = {}
        self.show()

    def load_groups(self, network: Network):
        all_groups = network.groups
        for group in all_groups:
            self.add_group(group)

    def add_group(self, group: NodeGroup):
        ui_group = QtWidgets.QWidget()
        ui_group.setLayout(QtWidgets.QHBoxLayout())
        radio_btn = QtWidgets.QRadioButton()
        radio_btn.setChecked(True)
        radio_btn.sizePolicy().setHorizontalStretch(1)
        ui_group.layout().addWidget(radio_btn)
        btn = QtWidgets.QPushButton(group.name)
        btn.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
        btn.sizePolicy().setHorizontalStretch(8)
        btn.clicked.connect(lambda: self.load_properties(group))
        ui_group.layout().addWidget(btn)
        self.group_widgets[group.name] = ui_group
        self.group_list_content.layout().addWidget(ui_group)

    def load_properties(self, group: NodeGroup):
        self.unload_properties()
        self.unload_connection_properties()

        properties = group.get_properties_dict()

        for p, v in properties.items():
            label = QtWidgets.QLabel(p)
            label.sizePolicy().setHorizontalStretch(2)
            label.sizePolicy().setHorizontalPolicy(
                QtWidgets.QSizePolicy.Policy.Preferred
            )
            input = QtWidgets.QLineEdit()
            input.setText(str(v))
            input.sizePolicy().setHorizontalStretch(3)
            input.sizePolicy().setHorizontalPolicy(
                QtWidgets.QSizePolicy.Policy.Expanding
            )
            self.group_properties_content.layout().addRow(label, input)
            self.load_connections(group)

    def load_connections(self, group: NodeGroup):
        self.unload_connections()

        other_groups = [g for g in group.network.groups if g.id != group.id]

        for g in other_groups:
            btn = QtWidgets.QPushButton(g.name)
            btn.sizePolicy().setHorizontalPolicy(QtWidgets.QSizePolicy.Policy.Expanding)
            btn.clicked.connect(lambda: self.load_connection_properties(group, g.id))
            self.connection_list_content.layout().addWidget(btn)

    def load_connection_properties(self, group_from: NodeGroup, group_to: str):
        self.unload_connection_properties()

        for p, v in [
            ("connection average", group_from.avrg_ext_con.get(group_to, 0)),
            ("connection delta", group_from.delta_ext_con.get(group_to, 0)),
        ]:
            label = QtWidgets.QLabel(p)
            label.sizePolicy().setHorizontalStretch(2)
            label.sizePolicy().setHorizontalPolicy(
                QtWidgets.QSizePolicy.Policy.Preferred
            )
            self.connection_properties_content.layout().addWidget(label)
            input = QtWidgets.QLineEdit()
            input.setText(str(v))
            input.sizePolicy().setHorizontalStretch(3)
            input.sizePolicy().setHorizontalPolicy(
                QtWidgets.QSizePolicy.Policy.Expanding
            )
            self.connection_properties_content.layout().addWidget(input)

    def unload_connection_properties(self):
        for i in reversed(range(self.connection_properties_content.layout().count())):
            self.connection_properties_content.layout().itemAt(i).widget().setParent(
                None
            )

    def unload_connections(self):
        for i in reversed(range(self.connection_list_content.layout().count())):
            self.connection_list_content.layout().itemAt(i).widget().setParent(None)

    def unload_properties(self):
        for i in reversed(range(self.group_properties_content.layout().count())):
            self.group_properties_content.layout().itemAt(i).widget().setParent(None)
