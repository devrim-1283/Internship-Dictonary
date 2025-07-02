from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1000, 750)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Dosya seçimi bölümü
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        # Dosya Seç butonu (sol taraf)
        self.pushButton = QtWidgets.QPushButton(parent=Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        
        # Dosya yolu etiketi (ortada, genişleyebilir)
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        
        # Spacer (sağa itmek için)
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacer)
        
        # Web Sitemiz butonu (sağ köşe)
        self.pushButton_website = QtWidgets.QPushButton(parent=Form)
        sizePolicy_website = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy_website.setHorizontalStretch(0)
        sizePolicy_website.setVerticalStretch(0)
        sizePolicy_website.setHeightForWidth(self.pushButton_website.sizePolicy().hasHeightForWidth())
        self.pushButton_website.setSizePolicy(sizePolicy_website)
        self.pushButton_website.setObjectName("pushButton_website")
        self.horizontalLayout.addWidget(self.pushButton_website)
        
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        # Mod seçimi bölümü
        self.modeGroupBox = QtWidgets.QGroupBox(parent=Form)
        self.modeGroupBox.setObjectName("modeGroupBox")
        self.modeHorizontalLayout = QtWidgets.QHBoxLayout(self.modeGroupBox)
        self.modeHorizontalLayout.setObjectName("modeHorizontalLayout")
        
        self.radioButton_basit = QtWidgets.QRadioButton(parent=self.modeGroupBox)
        self.radioButton_basit.setObjectName("radioButton_basit")
        self.radioButton_basit.setChecked(True)
        self.modeHorizontalLayout.addWidget(self.radioButton_basit)
        
        self.radioButton_gelismis = QtWidgets.QRadioButton(parent=self.modeGroupBox)
        self.radioButton_gelismis.setObjectName("radioButton_gelismis")
        self.modeHorizontalLayout.addWidget(self.radioButton_gelismis)
        
        self.verticalLayout.addWidget(self.modeGroupBox)
        
        # Combobox bölümü
        self.comboGroupBox = QtWidgets.QGroupBox(parent=Form)
        self.comboGroupBox.setObjectName("comboGroupBox")
        self.comboVerticalLayout = QtWidgets.QVBoxLayout(self.comboGroupBox)
        self.comboVerticalLayout.setObjectName("comboVerticalLayout")
        
        # Toplanacak sütun
        self.horizontalLayout_sum = QtWidgets.QHBoxLayout()
        self.horizontalLayout_sum.setObjectName("horizontalLayout_sum")
        self.label_sum = QtWidgets.QLabel(parent=self.comboGroupBox)
        self.label_sum.setObjectName("label_sum")
        self.label_sum.setMinimumWidth(150)
        self.horizontalLayout_sum.addWidget(self.label_sum)
        self.comboBox_sum = QtWidgets.QComboBox(parent=self.comboGroupBox)
        self.comboBox_sum.setObjectName("comboBox_sum")
        self.horizontalLayout_sum.addWidget(self.comboBox_sum)
        self.comboVerticalLayout.addLayout(self.horizontalLayout_sum)
        
        # Birinci değişken
        self.horizontalLayout_var1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_var1.setObjectName("horizontalLayout_var1")
        self.label_var1 = QtWidgets.QLabel(parent=self.comboGroupBox)
        self.label_var1.setObjectName("label_var1")
        self.label_var1.setMinimumWidth(150)
        self.horizontalLayout_var1.addWidget(self.label_var1)
        self.comboBox_var1 = QtWidgets.QComboBox(parent=self.comboGroupBox)
        self.comboBox_var1.setObjectName("comboBox_var1")
        self.horizontalLayout_var1.addWidget(self.comboBox_var1)
        self.comboVerticalLayout.addLayout(self.horizontalLayout_var1)
        
        # İkinci değişken
        self.horizontalLayout_var2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_var2.setObjectName("horizontalLayout_var2")
        self.label_var2 = QtWidgets.QLabel(parent=self.comboGroupBox)
        self.label_var2.setObjectName("label_var2")
        self.label_var2.setMinimumWidth(150)
        self.horizontalLayout_var2.addWidget(self.label_var2)
        self.comboBox_var2 = QtWidgets.QComboBox(parent=self.comboGroupBox)
        self.comboBox_var2.setObjectName("comboBox_var2")
        self.comboBox_var2.setEnabled(False)  # Başlangıçta deaktif
        self.horizontalLayout_var2.addWidget(self.comboBox_var2)
        self.comboVerticalLayout.addLayout(self.horizontalLayout_var2)
        
        self.verticalLayout.addWidget(self.comboGroupBox)
        
        # Buton bölümü
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton_3 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout_2.addWidget(self.pushButton_3)
        self.pushButton_4 = QtWidgets.QPushButton(parent=Form)
        self.pushButton_4.setObjectName("pushButton_4")
        self.horizontalLayout_2.addWidget(self.pushButton_4)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        
        # Ana tablo ve sağ panel bölümü
        self.mainHorizontalLayout = QtWidgets.QHBoxLayout()
        self.mainHorizontalLayout.setObjectName("mainHorizontalLayout")
        
        # Sol taraf - Tablo (yarı genişlik)
        self.tableView = QtWidgets.QTableView(parent=Form)
        self.tableView.setObjectName("tableView")
        self.tableView.setMaximumWidth(450)  # Biraz daha geniş
        self.mainHorizontalLayout.addWidget(self.tableView)
        
        # Sağ taraf - Grafik Panel
        self.rightPanel = QtWidgets.QVBoxLayout()
        self.rightPanel.setObjectName("rightPanel")
        
        # Grafik türü seçimi
        self.chartTypeGroupBox = QtWidgets.QGroupBox(parent=Form)
        self.chartTypeGroupBox.setObjectName("chartTypeGroupBox")
        self.chartTypeGroupBox.setMinimumWidth(300)
        self.chartTypeGroupBox.setMaximumHeight(80)
        
        self.chartTypeHorizontalLayout = QtWidgets.QHBoxLayout(self.chartTypeGroupBox)
        self.chartTypeHorizontalLayout.setObjectName("chartTypeHorizontalLayout")
        
        self.radioButton_line = QtWidgets.QRadioButton(parent=self.chartTypeGroupBox)
        self.radioButton_line.setObjectName("radioButton_line")
        self.radioButton_line.setChecked(True)  # Default çizgi grafik
        self.chartTypeHorizontalLayout.addWidget(self.radioButton_line)
        
        self.radioButton_bar = QtWidgets.QRadioButton(parent=self.chartTypeGroupBox)
        self.radioButton_bar.setObjectName("radioButton_bar")
        self.chartTypeHorizontalLayout.addWidget(self.radioButton_bar)
        
        self.radioButton_area = QtWidgets.QRadioButton(parent=self.chartTypeGroupBox)
        self.radioButton_area.setObjectName("radioButton_area")
        self.chartTypeHorizontalLayout.addWidget(self.radioButton_area)
        
        # Grafik indirme butonu ekle
        self.pushButton_download_chart = QtWidgets.QPushButton(parent=self.chartTypeGroupBox)
        self.pushButton_download_chart.setObjectName("pushButton_download_chart")
        self.pushButton_download_chart.setEnabled(False)  # Başlangıçta deaktif
        self.chartTypeHorizontalLayout.addWidget(self.pushButton_download_chart)
        
        self.rightPanel.addWidget(self.chartTypeGroupBox)
        
        # Grafik gösterim alanı - placeholder
        self.chartWidget = QtWidgets.QLabel(parent=Form)
        self.chartWidget.setObjectName("chartWidget")
        self.chartWidget.setMinimumWidth(300)
        self.chartWidget.setMinimumHeight(400)
        self.chartWidget.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.chartWidget.setStyleSheet("QLabel { border: 2px dashed #cccccc; border-radius: 10px; background-color: #f9f9f9; }")
        self.rightPanel.addWidget(self.chartWidget)
        
        # Sağ paneli ana layout'a ekle
        self.rightWidget = QtWidgets.QWidget(parent=Form)
        self.rightWidget.setLayout(self.rightPanel)
        self.mainHorizontalLayout.addWidget(self.rightWidget)
        
        # Ana horizontal layout'u vertical layout'a ekle
        self.verticalLayout.addLayout(self.mainHorizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Muhasebe Basit Veri Analizi Developed by Devrim Tunçer www.devrimtuncer.com"))
        self.pushButton.setText(_translate("Form", "Dosyayı Seç"))
        self.pushButton_website.setText(_translate("Form", "🌐 Web Sitemiz"))
        self.label.setText(_translate("Form", " "))
        self.modeGroupBox.setTitle(_translate("Form", "Analiz Modu"))
        self.radioButton_basit.setText(_translate("Form", "Basit"))
        self.radioButton_gelismis.setText(_translate("Form", "Gelişmiş"))
        self.comboGroupBox.setTitle(_translate("Form", "Sütun Seçimi"))
        self.label_sum.setText(_translate("Form", "Toplanacak Sütun:"))
        self.label_var1.setText(_translate("Form", "Birinci Değişken:"))
        self.label_var2.setText(_translate("Form", "İkinci Değişken:"))
        self.pushButton_3.setText(_translate("Form", "📊 Analiz Et"))
        self.pushButton_4.setText(_translate("Form", "📁 Excel İndir"))
        self.chartTypeGroupBox.setTitle(_translate("Form", "Grafik Türü"))
        self.radioButton_line.setText(_translate("Form", "📈 Çizgi"))
        self.radioButton_bar.setText(_translate("Form", "📊 Sütun"))
        self.radioButton_area.setText(_translate("Form", "📈 Alan"))
        self.pushButton_download_chart.setText(_translate("Form", "💾 İndir"))
        self.chartWidget.setText(_translate("Form", "📊\n\nGrafik burada gösterilecek\n\nAnaliz Et butonuna basın"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec())
