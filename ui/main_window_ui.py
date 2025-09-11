# ui/main_window_ui.py

from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 700)
        MainWindow.setWindowTitle("File Converter v1.5")

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, parent=self.centralwidget)
        self.splitter.setObjectName("splitter")

        self.leftPaneWidget = QtWidgets.QWidget(parent=self.splitter)
        self.leftPaneLayout = QtWidgets.QVBoxLayout(self.leftPaneWidget)
        self.leftPaneLayout.setContentsMargins(0, 0, 0, 0)
        self.leftPaneLayout.setObjectName("leftPaneLayout")
        
        self.fileListTableWidget = QtWidgets.QTableWidget(parent=self.leftPaneWidget)
        self.fileListTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.fileListTableWidget.setObjectName("fileListTableWidget")
        
        self.fileListTableWidget.setColumnCount(6)
        self.fileListTableWidget.setRowCount(0)
        
        headers = ["Source Path", "Target Format", "Status", "Progress", "Action", "Output"]
        for i, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem()
            item.setText(header)
            self.fileListTableWidget.setHorizontalHeaderItem(i, item)
            
        self.leftPaneLayout.addWidget(self.fileListTableWidget)

        # --- RIGHT PANE (UPDATED with Preset controls) ---
        self.rightPaneWidget = QtWidgets.QWidget(parent=self.splitter)
        self.rightPaneLayout = QtWidgets.QVBoxLayout(self.rightPaneWidget)
        self.rightPaneLayout.setObjectName("rightPaneLayout")
        self.rightPaneLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        # --- NEW: Preset Management Section ---
        self.presetGroupBox = QtWidgets.QGroupBox("Presets")
        self.presetLayout = QtWidgets.QHBoxLayout(self.presetGroupBox)
        
        self.presetComboBox = QtWidgets.QComboBox()
        self.presetComboBox.setPlaceholderText("Apply a Preset...")
        self.presetLayout.addWidget(self.presetComboBox)
        
        self.savePresetButton = QtWidgets.QPushButton("Save")
        self.savePresetButton.setToolTip("Save current settings as a new preset")
        self.presetLayout.addWidget(self.savePresetButton)
        
        self.deletePresetButton = QtWidgets.QPushButton("Delete")
        self.deletePresetButton.setToolTip("Delete the selected preset")
        self.presetLayout.addWidget(self.deletePresetButton)
        
        self.rightPaneLayout.addWidget(self.presetGroupBox)
        # --- END NEW ---

        self.settingsStack = QtWidgets.QStackedWidget(parent=self.rightPaneWidget)
        self.rightPaneLayout.addWidget(self.settingsStack)
        
        self.placeholderSettingsPage = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.placeholderSettingsPage)
        label = QtWidgets.QLabel("Select a file to see conversion settings.")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.settingsStack.addWidget(self.placeholderSettingsPage)

        self.horizontalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1100, 22))
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuHelp = QtWidgets.QMenu(parent=self.menubar)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(parent=MainWindow)
        MainWindow.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, self.toolBar)
        
        self.actionAdd_Files = QtGui.QAction(parent=MainWindow)
        self.actionRemove_Selected = QtGui.QAction(parent=MainWindow)
        self.actionMerge_Selected = QtGui.QAction(parent=MainWindow)
        self.actionConvert_All = QtGui.QAction(parent=MainWindow)
        self.actionCancel_All = QtGui.QAction(parent=MainWindow)
        self.actionPreferences = QtGui.QAction(parent=MainWindow)
        self.actionExit = QtGui.QAction(parent=MainWindow)
        self.actionAbout = QtGui.QAction(parent=MainWindow)
        self.actionSetup_Guide = QtGui.QAction(parent=MainWindow)
        self.actionDependency_Checker = QtGui.QAction(parent=MainWindow)

        self.menuFile.addAction(self.actionAdd_Files); self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionPreferences); self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        
        self.menuHelp.addAction(self.actionDependency_Checker)
        self.menuHelp.addAction(self.actionSetup_Guide)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout)
        
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
        self.toolBar.addAction(self.actionAdd_Files); self.toolBar.addAction(self.actionRemove_Selected)
        self.toolBar.addSeparator(); self.toolBar.addAction(self.actionMerge_Selected)
        self.toolBar.addSeparator(); self.toolBar.addAction(self.actionConvert_All)
        self.toolBar.addAction(self.actionCancel_All)

        self.retranslateUi(MainWindow)
        self.splitter.setSizes([700, 400])
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "File Converter v1.5"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionAdd_Files.setText(_translate("MainWindow", "Add Files..."))
        self.actionRemove_Selected.setText(_translate("MainWindow", "Remove Selected"))
        self.actionMerge_Selected.setText(_translate("MainWindow", "Merge Selected"))
        self.actionConvert_All.setText(_translate("MainWindow", "Convert All"))
        self.actionCancel_All.setText(_translate("MainWindow", "Cancel All"))
        self.actionPreferences.setText(_translate("MainWindow", "Preferences..."))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionAbout.setText(_translate("MainWindow", "About..."))
        self.actionSetup_Guide.setText(_translate("MainWindow", "Setup Guide..."))
        self.actionDependency_Checker.setText(_translate("MainWindow", "Dependency Checker..."))