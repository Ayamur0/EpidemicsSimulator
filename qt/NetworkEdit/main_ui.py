# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\Users\sasch\Downloads\EpidemicsSimulator\qt\NetworkEdit\main.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        MainWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.network_edit = QtWidgets.QWidget()
        self.network_edit.setObjectName("network_edit")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.network_edit)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_3 = QtWidgets.QFrame(self.network_edit)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.network_img = QtWidgets.QGraphicsView(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(18)
        sizePolicy.setHeightForWidth(self.network_img.sizePolicy().hasHeightForWidth())
        self.network_img.setSizePolicy(sizePolicy)
        self.network_img.setObjectName("network_img")
        self.verticalLayout_2.addWidget(self.network_img)
        self.frame = QtWidgets.QFrame(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(500, 10, 93, 28))
        self.pushButton.setStyleSheet("")
        self.pushButton.setAutoDefault(False)
        self.pushButton.setDefault(False)
        self.pushButton.setFlat(False)
        self.pushButton.setObjectName("pushButton")
        self.comboBox = QtWidgets.QComboBox(self.frame)
        self.comboBox.setGeometry(QtCore.QRect(360, 10, 131, 31))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.network_stats = QtWidgets.QLabel(self.frame)
        self.network_stats.setGeometry(QtCore.QRect(0, 10, 201, 61))
        self.network_stats.setObjectName("network_stats")
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout.addWidget(self.frame_3)
        self.frame_2 = QtWidgets.QFrame(self.network_edit)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout.setObjectName("gridLayout")
        self.group_list = QtWidgets.QScrollArea(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.group_list.sizePolicy().hasHeightForWidth())
        self.group_list.setSizePolicy(sizePolicy)
        self.group_list.setStyleSheet("")
        self.group_list.setWidgetResizable(True)
        self.group_list.setObjectName("group_list")
        self.group_list_content = QtWidgets.QWidget()
        self.group_list_content.setGeometry(QtCore.QRect(0, 0, 238, 302))
        self.group_list_content.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.group_list_content.setStyleSheet("")
        self.group_list_content.setObjectName("group_list_content")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.group_list_content)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.group_list_layout = QtWidgets.QVBoxLayout()
        self.group_list_layout.setContentsMargins(0, -1, 0, -1)
        self.group_list_layout.setObjectName("group_list_layout")
        self.verticalLayout_3.addLayout(self.group_list_layout)
        self.group_list.setWidget(self.group_list_content)
        self.gridLayout.addWidget(self.group_list, 0, 0, 1, 1)
        self.connection_list = QtWidgets.QScrollArea(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connection_list.sizePolicy().hasHeightForWidth())
        self.connection_list.setSizePolicy(sizePolicy)
        self.connection_list.setStyleSheet("")
        self.connection_list.setWidgetResizable(True)
        self.connection_list.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.connection_list.setObjectName("connection_list")
        self.connection_list_content = QtWidgets.QWidget()
        self.connection_list_content.setGeometry(QtCore.QRect(0, 0, 238, 301))
        self.connection_list_content.setObjectName("connection_list_content")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.connection_list_content)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.con_list_layout = QtWidgets.QVBoxLayout()
        self.con_list_layout.setObjectName("con_list_layout")
        self.verticalLayout_6.addLayout(self.con_list_layout)
        self.connection_list.setWidget(self.connection_list_content)
        self.gridLayout.addWidget(self.connection_list, 1, 0, 1, 1)
        self.group_properties = QtWidgets.QScrollArea(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.group_properties.sizePolicy().hasHeightForWidth())
        self.group_properties.setSizePolicy(sizePolicy)
        self.group_properties.setWidgetResizable(True)
        self.group_properties.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.group_properties.setObjectName("group_properties")
        self.group_properties_content = QtWidgets.QWidget()
        self.group_properties_content.setGeometry(QtCore.QRect(0, 0, 357, 302))
        self.group_properties_content.setObjectName("group_properties_content")
        self.formLayout = QtWidgets.QFormLayout(self.group_properties_content)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout.setObjectName("formLayout")
        self.group_properties.setWidget(self.group_properties_content)
        self.gridLayout.addWidget(self.group_properties, 0, 1, 1, 1)
        self.connection_properties = QtWidgets.QScrollArea(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connection_properties.sizePolicy().hasHeightForWidth())
        self.connection_properties.setSizePolicy(sizePolicy)
        self.connection_properties.setStyleSheet("")
        self.connection_properties.setWidgetResizable(True)
        self.connection_properties.setObjectName("connection_properties")
        self.connection_properties_content = QtWidgets.QWidget()
        self.connection_properties_content.setGeometry(QtCore.QRect(0, 0, 357, 301))
        self.connection_properties_content.setObjectName("connection_properties_content")
        self.formLayout_2 = QtWidgets.QFormLayout(self.connection_properties_content)
        self.formLayout_2.setObjectName("formLayout_2")
        self.connection_properties.setWidget(self.connection_properties_content)
        self.gridLayout.addWidget(self.connection_properties, 1, 1, 1, 1)
        self.horizontalLayout.addWidget(self.frame_2)
        self.tabWidget.addTab(self.network_edit, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout_4.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 22))
        self.menubar.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionSave_STRG_S = QtWidgets.QAction(MainWindow)
        self.actionSave_STRG_S.setObjectName("actionSave_STRG_S")
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionImport = QtWidgets.QAction(MainWindow)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setObjectName("actionExport")
        self.actionExport_Image = QtWidgets.QAction(MainWindow)
        self.actionExport_Image.setObjectName("actionExport_Image")
        self.actionNew = QtWidgets.QAction(MainWindow)
        self.actionNew.setObjectName("actionNew")
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionSave_STRG_S)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionExport_Image)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.network_img.setToolTip(_translate("MainWindow", "<html><head/><body><p>test</p></body></html>"))
        self.pushButton.setToolTip(_translate("MainWindow", "<html><head/><body><p>(Re-)Generate the network image</p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Generate"))
        self.comboBox.setToolTip(_translate("MainWindow", "<html><head/><body><p>Select network representation style</p></body></html>"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Representation 1"))
        self.comboBox.setItemText(1, _translate("MainWindow", "2"))
        self.comboBox.setItemText(2, _translate("MainWindow", "3"))
        self.network_stats.setText(_translate("MainWindow", "Some stats about graph creation\n"
"Total nodes 1000\n"
"Total connections 10000\n"
"Generation time 20.5s"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.network_edit), _translate("MainWindow", "Network Editor"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave_STRG_S.setText(_translate("MainWindow", "Save STRG+S"))
        self.actionOpen.setText(_translate("MainWindow", "Open"))
        self.actionImport.setText(_translate("MainWindow", "Import Network"))
        self.actionExport.setText(_translate("MainWindow", "Export Network"))
        self.actionExport_Image.setText(_translate("MainWindow", "Export Image"))
        self.actionNew.setText(_translate("MainWindow", "New"))
