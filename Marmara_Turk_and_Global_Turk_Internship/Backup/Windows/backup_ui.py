from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime
import os

class Ui_Form(object):
    def setupUi(self, Form):
        # Main form setup
        Form.setObjectName("Form")
        Form.resize(704, 362)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        
        # Drive selection label
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setMaximumSize(QtCore.QSize(60, 29))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        
        # Drive selection combobox
        self.comboBox_2 = QtWidgets.QComboBox(Form)
        self.comboBox_2.setEnabled(True)
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout_2.addWidget(self.comboBox_2)
        
        # Delete drive button
        self.pushButton_5 = QtWidgets.QPushButton(Form)
        self.pushButton_5.setMaximumSize(QtCore.QSize(135, 24))
        self.pushButton_5.setObjectName("pushButton_5")
        self.horizontalLayout_2.addWidget(self.pushButton_5)
        
        # Refresh button
        self.pushButton_6 = QtWidgets.QPushButton(Form)
        self.pushButton_6.setMaximumSize(QtCore.QSize(135, 24))
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_2.addWidget(self.pushButton_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        
        # Password section layout
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        
        # Password label
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        
        # Password input field
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit.setText("112.st!?")
        self.lineEdit.setEnabled(False)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_3.addWidget(self.lineEdit)
        
        # Save password button
        self.pushButton_7 = QtWidgets.QPushButton(Form)
        self.pushButton_7.setEnabled(False)
        self.pushButton_7.setObjectName("pushButton_7")
        self.horizontalLayout_3.addWidget(self.pushButton_7)
        
        # Encrypt checkbox
        self.checkBox = QtWidgets.QCheckBox(Form)
        self.checkBox.setChecked(False)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_3.addWidget(self.checkBox)
        
        # Compress checkbox
        self.checkBox_2 = QtWidgets.QCheckBox(Form)
        self.checkBox_2.setChecked(False)
        self.checkBox_2.setObjectName("checkBox_2")
        self.horizontalLayout_3.addWidget(self.checkBox_2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        
        # Computer name section layout
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        
        # Computer name label
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_4.addWidget(self.label_7)
        
        # Computer name input field
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setText(os.getenv('USERNAME') or os.getenv('USER'))  # Get Windows or Linux username
        self.horizontalLayout_4.addWidget(self.lineEdit_2)
        
        # Edit folders checkbox
        self.checkBox_4 = QtWidgets.QCheckBox(Form)
        self.checkBox_4.setObjectName("checkBox_4")
        self.horizontalLayout_4.addWidget(self.checkBox_4)
        
        # Reset changes button
        self.pushButton_8 = QtWidgets.QPushButton(Form)
        self.pushButton_8.setObjectName("pushButton_8")
        self.horizontalLayout_4.addWidget(self.pushButton_8)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        
        # Folder list section layout
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        # Folder list view
        self.listView = QtWidgets.QListView(Form)
        self.listView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listView.setObjectName("listView")
        self.horizontalLayout.addWidget(self.listView)
        
        # Folder control buttons layout
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Add folder button
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        
        # Delete folder button
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setEnabled(False)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        
        # Ignore folder button
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setEnabled(False)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        
        # Status section layout
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        
        # Backup button
        self.pushButton_11 = QtWidgets.QPushButton(Form)
        self.pushButton_11.setObjectName("pushButton_11")
        self.horizontalLayout_6.addWidget(self.pushButton_11)
        
        # Time label
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_6.addWidget(self.label_4)
        
        # Start time label
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_6.addWidget(self.label_5)
        
        # Duration label
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_6.addWidget(self.label_6)
        self.verticalLayout_2.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7.addLayout(self.verticalLayout_2)

        # Setup UI text
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        """Sets up all UI text elements"""
        _translate = QtCore.QCoreApplication.translate
        current_date = datetime.now().strftime('%d/%m/%Y')
        Form.setWindowTitle(_translate("Form", f"Backup - {current_date} - Developed by Devrim Tunçer and Esma Tanşa"))
        self.label_2.setText(_translate("Form", "Disks :"))
        self.pushButton_5.setText(_translate("Form", "Disk Delete"))
        self.pushButton_6.setText(_translate("Form", "Refresh"))
        self.label_3.setText(_translate("Form", "Password : "))
        self.pushButton_7.setText(_translate("Form", "Save Password"))
        self.checkBox.setText(_translate("Form", "Encrypt"))
        self.checkBox_2.setText(_translate("Form", "Compress"))
        self.label_7.setText(_translate("Form", "Computer Name :"))
        self.checkBox_4.setText(_translate("Form", "Edit Folders"))
        self.pushButton_8.setText(_translate("Form", "Reset Changes"))
        self.pushButton.setText(_translate("Form", "Add"))
        self.pushButton_2.setText(_translate("Form", "Delete"))
        self.pushButton_3.setText(_translate("Form", "Ignore"))
        self.pushButton_11.setText(_translate("Form", "Backup"))
        self.label_4.setText(_translate("Form", "Hour:"))
        self.label_5.setText(_translate("Form", "Start Time:"))
        self.label_6.setText(_translate("Form", "Duration: "))
