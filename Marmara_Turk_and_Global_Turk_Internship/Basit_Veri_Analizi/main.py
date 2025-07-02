import sys
import os
import webbrowser
from datetime import datetime
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtCore import Qt  # Bu satır, Qt.ItemDataRole.UserRole kullanımı için eklendi

# Matplotlib imports
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
import matplotlib
matplotlib.use('Qt5Agg')

from gui import Ui_Form


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # İkonu ayarla
        icon_path = os.path.join(os.path.dirname(__file__), "muhasebe.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Bağlantılar
        self.ui.pushButton.clicked.connect(self.select_file)
        self.ui.pushButton_website.clicked.connect(self.open_website)
        self.ui.pushButton_3.clicked.connect(self.analyze_data)
        self.ui.pushButton_4.clicked.connect(self.export_to_excel)
        self.ui.radioButton_basit.toggled.connect(self.mode_changed)
        self.ui.radioButton_gelismis.toggled.connect(self.mode_changed)
        
        # Grafik türü radio button bağlantıları
        self.ui.radioButton_line.toggled.connect(self.chart_type_changed)
        self.ui.radioButton_bar.toggled.connect(self.chart_type_changed)
        self.ui.radioButton_area.toggled.connect(self.chart_type_changed)
        
        # Grafik indirme butonu bağlantısı
        self.ui.pushButton_download_chart.clicked.connect(self.download_chart)

        # Değişkenler
        self.selected_file_path = None
        self.df = None
        self.column_types = {}  # Sütun türlerini saklayacak sözlük
        self.analysis_results = {}  # Analiz sonuçlarını saklayacak
        self.chart_canvas = None  # Matplotlib canvas

        # Pandas lazy import için
        self.pd = None

        # Başlangıçta butonları deaktif yap
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        
        # Matplotlib canvas'ı başlat
        self.setup_chart_canvas()

    def _import_pandas(self):
        """Pandas'ı sadece gerektiğinde import et"""
        if self.pd is None:
            import pandas as pd
            self.pd = pd
        return self.pd
    
    def open_website(self):
        """Web sitesini aç"""
        try:
            webbrowser.open("https://www.devrimtuncer.com")
        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Web sitesi açılırken hata oluştu:\n{str(e)}")
    
    def select_file(self):
        """Dosya seçme ve sütun analizi"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Dosya Seç", 
            "",  
            "Excel Dosyaları (*.xlsx)" 
        )
        if file_path:
            self.selected_file_path = file_path
            self.ui.label.setText(file_path)
            self.load_and_analyze_columns()
        else:
            self.ui.label.setText(" ")
            self.selected_file_path = None
            self.clear_comboboxes()

    def load_and_analyze_columns(self):
        """Excel dosyasını yükle ve sütunları analiz et"""
        try:
            pd = self._import_pandas()
            self.df = pd.read_excel(self.selected_file_path)
            self.column_types = {}

            # Her sütunun türünü analiz et
            for col in self.df.columns:
                col_data = self.df[col].dropna()  # NaN değerleri çıkar

                if len(col_data) == 0:
                    self.column_types[col] = 'empty'
                    continue

                # İlk 10 değeri kontrol et (daha hızlı)
                sample_size = min(10, len(col_data))
                sample_data = col_data.head(sample_size)

                # Sayı, tarih, saat, para, string sayaçları
                numeric_count = 0
                date_count = 0
                time_count = 0
                currency_count = 0

                import re

                for value in sample_data:
                    value_str = str(value).strip()

                    # Para birimi kontrolü (1,234.56 veya 1.234,56 formatları)
                    currency_patterns = [
                        r'^\d{1,3}(,\d{3})*\.\d{2}$',  # 1,234.56
                        r'^\d{1,3}(\.\d{3})*,\d{2}$',  # 1.234,56
                        r'^\d+\.\d{2}$',              # 123.45
                        r'^\d+,\d{2}$',               # 123,45
                        r'^\d{1,3}(,\d{3})*$',        # 1,234 (tam sayı para)
                    ]

                    is_currency = False
                    for pattern in currency_patterns:
                        if re.match(pattern, value_str):
                            currency_count += 1
                            is_currency = True
                            break

                    if is_currency:
                        continue

                    # Basit sayı kontrolü
                    try:
                        pd.to_numeric(value)
                        numeric_count += 1
                        continue
                    except (ValueError, TypeError):
                        pass

                    # Tarih kontrolü
                    try:
                        parsed_date = pd.to_datetime(value)
                        # Sadece tarih mi yoksa saat de var mı kontrol et
                        if parsed_date.time() == parsed_date.time().replace(hour=0, minute=0, second=0, microsecond=0):
                            date_count += 1
                        else:
                            time_count += 1
                        continue
                    except (ValueError, TypeError):
                        pass

                    # Saat formatı kontrolü (HH:MM veya HH:MM:SS)
                    if isinstance(value, str):
                        # Saat formatları: 14:30, 14:30:45, 2:30 PM, vs.
                        time_patterns = [
                            r'^\d{1,2}:\d{2}$',  # 14:30
                            r'^\d{1,2}:\d{2}:\d{2}$',  # 14:30:45
                            r'^\d{1,2}:\d{2}\s?(AM|PM)$',  # 2:30 PM
                            r'^\d{1,2}:\d{2}:\d{2}\s?(AM|PM)$'  # 2:30:45 PM
                        ]
                        for pattern in time_patterns:
                            if re.match(pattern, value_str, re.IGNORECASE):
                                time_count += 1
                                break

                # Türü belirle (en yüksek orana sahip olanı seç)
                if currency_count / sample_size > 0.7:
                    self.column_types[col] = 'currency'
                elif numeric_count / sample_size > 0.7:
                    self.column_types[col] = 'numeric'
                elif date_count / sample_size > 0.7:
                    self.column_types[col] = 'date'
                elif time_count / sample_size > 0.7:
                    self.column_types[col] = 'time'
                else:
                    self.column_types[col] = 'string'

            self.populate_comboboxes()
            self.ui.pushButton_3.setEnabled(True)

            # Sütun türlerini göster
            type_summary = {}
            for col_type in ['numeric', 'currency', 'date', 'time', 'string']:
                count = list(self.column_types.values()).count(col_type)
                if count > 0:
                    type_summary[col_type] = count

            summary_text = ", ".join([f"{count} {col_type}" for col_type, count in type_summary.items()])
            QMessageBox.information(self, "Başarılı", f"Dosya yüklendi! {len(self.df.columns)} sütun analiz edildi.\n\nBulunan türler: {summary_text}")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya yüklenirken hata oluştu:\n{str(e)}")
            self.clear_comboboxes()

    def populate_comboboxes(self):
        """Comboboxları doldur"""
        # Comboboxları temizle
        self.ui.comboBox_sum.clear()
        self.ui.comboBox_var1.clear()
        self.ui.comboBox_var2.clear()

        # Emoji ikonları
        type_icons = {
            'numeric': '🔢',
            'currency': '💰',
            'date': '📅',
            'time': '🕐',
            'string': '📝'
        }

        # Toplanacak sütun combobox'ı - sadece sayısal ve para sütunları (emoji ile)
        summable_columns = []
        for col, col_type in self.column_types.items():
            if col_type in ['numeric', 'currency']:
                icon = type_icons.get(col_type, '❓')
                summable_columns.append(f"{icon} {col}")
        self.ui.comboBox_sum.addItems(summable_columns)

        # Değişken comboboxları - tüm sütunlar (türü ile birlikte göster)
        all_columns = []
        for col, col_type in self.column_types.items():
            icon = type_icons.get(col_type, '❓')
            all_columns.append(f"{icon} {col}")

        self.ui.comboBox_var1.addItems(all_columns)
        self.ui.comboBox_var2.addItems(all_columns)

    def clear_comboboxes(self):
        """Comboboxları temizle"""
        self.ui.comboBox_sum.clear()
        self.ui.comboBox_var1.clear()
        self.ui.comboBox_var2.clear()
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)

    def mode_changed(self):
        """Mod değişimini handle et"""
        if self.ui.radioButton_basit.isChecked():
            self.ui.comboBox_var2.setEnabled(False)
        else:
            self.ui.comboBox_var2.setEnabled(True)

    def _extract_column_name(self, combo_text):
        """Combobox metninden sütun adını çıkar (emoji'yi kaldır)"""
        if " " in combo_text:
            return combo_text.split(" ", 1)[1]  # İlk boşluktan sonraki kısmı al
        return combo_text
    
    def analyze_data(self):
        """Analiz fonksiyonu"""
        if not self.selected_file_path or self.df is None:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir dosya seçin!")
            return
        
        if self.ui.comboBox_sum.currentText() == "":
            QMessageBox.warning(self, "Uyarı", "Lütfen toplanacak sütunu seçin!")
            return

        if self.ui.comboBox_var1.currentText() == "":
            QMessageBox.warning(self, "Uyarı", "Lütfen birinci değişkeni seçin!")
            return

        sum_column = self._extract_column_name(self.ui.comboBox_sum.currentText())
        var1_column = self._extract_column_name(self.ui.comboBox_var1.currentText())

        try:
            if self.ui.radioButton_basit.isChecked():
                self.analyze_simple(sum_column, var1_column)
            else:
                if self.ui.comboBox_var2.currentText() == "":
                    QMessageBox.warning(self, "Uyarı", "Gelişmiş modda ikinci değişkeni de seçin!")
                    return
                var2_column = self._extract_column_name(self.ui.comboBox_var2.currentText())
                self.analyze_advanced(sum_column, var1_column, var2_column)

            self.ui.pushButton_4.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Analiz sırasında hata oluştu:\n{str(e)}")

    def analyze_simple(self, sum_column, var1_column):
        """Basit analiz - tek değişkene göre toplama"""
        if self.df is None:
                return
            
        pd = self._import_pandas()

        # DataFrame'i kopyala ve temizle
        df_work = self.df[[sum_column, var1_column]].copy()
        df_work = df_work.dropna()

        # Sayısal sütunu numeric yap
        df_work[sum_column] = pd.to_numeric(df_work[sum_column], errors='coerce')

        # Sütun türüne göre işlem
        col_type = self.column_types[var1_column]

        if col_type == 'date':
            df_work[var1_column] = pd.to_datetime(df_work[var1_column], errors='coerce')
            df_work = df_work.dropna()
            # Tarihi string formatına çevir (gösterim için)
            df_work[var1_column] = df_work[var1_column].dt.strftime('%d.%m.%Y')

        elif col_type == 'time':
            # Saat verisini standart formata çevir
            try:
                df_work[var1_column] = pd.to_datetime(df_work[var1_column], errors='coerce')
                df_work = df_work.dropna()
                df_work[var1_column] = df_work[var1_column].dt.strftime('%H:%M')
            except:
                # Eğer datetime'a çevrilemezse string olarak bırak
                df_work[var1_column] = df_work[var1_column].astype(str)

        # Gruplama ve toplama
        grouped = df_work.groupby(var1_column)[sum_column].sum().reset_index()

        # Sonuçları kaydet
        self.analysis_results = {}
        for _, row in grouped.iterrows():
            self.analysis_results[str(row[var1_column])] = row[sum_column]

        # Tabloyu güncelle
        self.update_table_simple(var1_column, sum_column)

    def analyze_advanced(self, sum_column, var1_column, var2_column):
        """Gelişmiş analiz - iki değişkene göre toplama"""
        if self.df is None:
                return
            
        pd = self._import_pandas()

        # DataFrame'i kopyala ve temizle
        df_work = self.df[[sum_column, var1_column, var2_column]].copy()
        df_work = df_work.dropna()

        # Sayısal sütunu numeric yap
        df_work[sum_column] = pd.to_numeric(df_work[sum_column], errors='coerce')

        # Her değişken için türüne göre işlem
        for col in [var1_column, var2_column]:
            col_type = self.column_types[col]

            if col_type == 'date':
                df_work[col] = pd.to_datetime(df_work[col], errors='coerce')
                df_work[col] = df_work[col].dt.strftime('%d.%m.%Y')

            elif col_type == 'time':
                try:
                    df_work[col] = pd.to_datetime(df_work[col], errors='coerce')
                    df_work[col] = df_work[col].dt.strftime('%H:%M')
                except:
                    df_work[col] = df_work[col].astype(str)

        df_work = df_work.dropna()

        # Gruplama ve toplama
        grouped = df_work.groupby([var1_column, var2_column])[sum_column].sum().reset_index()

        # Sonuçları kaydet
        self.analysis_results = {}
        for _, row in grouped.iterrows():
            key = f"{row[var1_column]} - {row[var2_column]}"
            self.analysis_results[key] = row[sum_column]

        # Tabloyu güncelle
        self.update_table_advanced(var1_column, var2_column, sum_column)

    def update_table_simple(self, var1_column, sum_column):
        """Basit analiz için tabloyu güncelle"""
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([var1_column, sum_column])

        # Önce toplam hesapla
        total = sum(self.analysis_results.values())
        
        # TOPLAM satırını en başa ekle
        total_key_item = QStandardItem("🔢 TOPLAM")
        total_key_item.setEditable(False)
        font = total_key_item.font()
        font.setBold(True)
        total_key_item.setFont(font)
        
        total_value_item = QStandardItem(f"{total:,.2f}")
        total_value_item.setEditable(False)
        total_value_item.setFont(font)
        total_value_item.setData(float(total), role=Qt.ItemDataRole.UserRole)
        
        model.appendRow([total_key_item, total_value_item])
        
        # Sonra diğer verileri ekle
        for key, value in sorted(self.analysis_results.items()): 
            # Birinci sütun (değişken)
            key_item = QStandardItem(str(key))
            key_item.setEditable(False)  # Değiştirilemez yap

            # Tarih sütunuysa özel sıralama için datetime değeri sakla
            if self.column_types.get(var1_column) == 'date':
                try:
                    pd = self._import_pandas()
                    # Tarih formatını kontrol edin ve to_datetime'a uygun hale getirin
                    date_val = pd.to_datetime(key, format='%d.%m.%Y', errors='coerce')
                    if pd.notnull(date_val):
                        # Özel sıralama için datetime nesnesini ata
                        key_item.setData(date_val, role=Qt.ItemDataRole.UserRole)
                except Exception as e:
                    # print(f"Hata: Tarih dönüşümünde sorun (basit analiz, key_item): {e} - Değer: {key}")
                    pass

            # İkinci sütun (sayısal değerler)
            value_item = QStandardItem(f"{value:,.2f}") # Ekranda gösterilecek format
            value_item.setEditable(False)  # Değiştirilemez yap

            try:
                # Sayısal sıralama için doğrudan float değerini ata
                value_item.setData(float(value), role=Qt.ItemDataRole.UserRole)
                # Debugging için: print(f"DEBUG (Simple): Setting {value_item.text()} (Display) -> {float(value)} (UserRole) for sorting")
            except ValueError:
                # print(f"DEBUG (Simple): Failed to convert value to float for sorting: {value}")
                value_item.setData(0.0, role=Qt.ItemDataRole.UserRole) # Dönüşüm hatası olursa 0.0 ata

            model.appendRow([key_item, value_item])
            total += value

        # Modeli tabloya ata
        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()

        # Sıralama özelliğini devre dışı bırak
        self.ui.tableView.setSortingEnabled(False)
        
        # Grafiği güncelle
        self.update_chart()
        
        # Grafik indirme butonunu aktifleştir
        self.ui.pushButton_download_chart.setEnabled(True)

        total_rows = len(self.df) if self.df is not None else 0
        QMessageBox.information(self, "✅ Muhasebe Basit Veri Analizi", f"Basit analiz başarıyla tamamlandı!\n\n📊 {len(self.analysis_results)} farklı grup bulundu\n🔢 {total_rows} satır veri analiz edildi")

    def update_table_advanced(self, var1_column, var2_column, sum_column):
        """Gelişmiş analiz için tabloyu güncelle"""
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([var1_column, var2_column, sum_column])

        # Önce toplam hesapla
        total = sum(self.analysis_results.values())
        
        # TOPLAM satırını en başa ekle
        total_var1_item = QStandardItem("🔢 TOPLAM")
        total_var1_item.setEditable(False)
        font = total_var1_item.font()
        font.setBold(True)
        total_var1_item.setFont(font)
        
        total_var2_item = QStandardItem("")
        total_var2_item.setEditable(False)
        
        total_value_item = QStandardItem(f"{total:,.2f}")
        total_value_item.setEditable(False)
        total_value_item.setFont(font)
        total_value_item.setData(float(total), role=Qt.ItemDataRole.UserRole)
        
        model.appendRow([total_var1_item, total_var2_item, total_value_item])
        
        # Sonra diğer verileri ekle
        for key, value in sorted(self.analysis_results.items()):
            parts = key.split(' - ')

            # Birinci sütun (değişken 1)
            var1_item = QStandardItem(parts[0])
            var1_item.setEditable(False)  # Değiştirilemez yap

            # Tarih sütunuysa özel sıralama için datetime değeri sakla
            if self.column_types.get(var1_column) == 'date':
                try:
                    pd = self._import_pandas()
                    date_val = pd.to_datetime(parts[0], format='%d.%m.%Y', errors='coerce')
                    if pd.notnull(date_val):
                        var1_item.setData(date_val, role=Qt.ItemDataRole.UserRole)
                except Exception as e:
                    # print(f"Hata: Tarih dönüşümünde sorun (gelişmiş, var1_item): {e} - Değer: {parts[0]}")
                    pass

            # İkinci sütun (değişken 2)
            var2_item = QStandardItem(parts[1] if len(parts) > 1 else "")
            var2_item.setEditable(False)  # Değiştirilemez yap

            # İkinci değişken tarih/saat sütunuysa özel sıralama
            if len(parts) > 1:
                if self.column_types.get(var2_column) == 'date':
                    try:
                        pd = self._import_pandas()
                        date_val = pd.to_datetime(parts[1], format='%d.%m.%Y', errors='coerce')
                        if pd.notnull(date_val):
                            var2_item.setData(date_val, role=Qt.ItemDataRole.UserRole)
                    except Exception as e:
                        # print(f"Hata: Tarih dönüşümünde sorun (gelişmiş, var2_item): {e} - Değer: {parts[1]}")
                        pass
                elif self.column_types.get(var2_column) == 'time':
                    try:
                        pd = self._import_pandas()
                        time_val = pd.to_datetime(parts[1], format='%H:%M', errors='coerce')
                        if pd.notnull(time_val):
                            var2_item.setData(time_val, role=Qt.ItemDataRole.UserRole)
                    except Exception as e:
                        # print(f"Hata: Zaman dönüşümünde sorun (gelişmiş, var2_item): {e} - Değer: {parts[1]}")
                        pass

            # Üçüncü sütun (sayısal değerler)
            value_item = QStandardItem(f"{value:,.2f}") # Ekranda gösterilecek format
            value_item.setEditable(False)  # Değiştirilemez yap

            try:
                # Sayısal sıralama için doğrudan float değerini ata
                value_item.setData(float(value), role=Qt.ItemDataRole.UserRole)
                # Debugging için: print(f"DEBUG (Advanced): Setting {value_item.text()} (Display) -> {float(value)} (UserRole) for sorting")
            except ValueError:
                # print(f"DEBUG (Advanced): Failed to convert value to float for sorting: {value}")
                value_item.setData(0.0, role=Qt.ItemDataRole.UserRole) # Dönüşüm hatası olursa 0.0 ata

            model.appendRow([var1_item, var2_item, value_item])

        # Modeli tabloya ata
        self.ui.tableView.setModel(model)
        self.ui.tableView.resizeColumnsToContents()
        
        # Sıralama özelliğini devre dışı bırak
        self.ui.tableView.setSortingEnabled(False)
        
        # Grafiği güncelle
        self.update_chart()
        
        # Grafik indirme butonunu aktifleştir
        self.ui.pushButton_download_chart.setEnabled(True)

        total_rows = len(self.df) if self.df is not None else 0
        QMessageBox.information(self, "✅ Muhasebe Basit Veri Analizi", f"Gelişmiş analiz başarıyla tamamlandı!\n\n📊 {len(self.analysis_results)} farklı grup bulundu\n🔢 {total_rows} satır veri analiz edildi")

    def export_to_excel(self):
        """Excel'e aktar"""
        if not self.analysis_results:
            QMessageBox.warning(self, "Uyarı", "Excel'e aktarmak için önce analiz yapınız!")
            return
        
        try:
            pd = self._import_pandas()

            # Desktop klasörü
            desktop_dir = os.path.join(os.path.expanduser("~"), "OneDrive/Desktop") 
            
            # Eğer OneDrive/Desktop yolu yoksa veya hata veriyorsa sadece Desktop'a kaydedebiliriz:
            if not os.path.exists(desktop_dir):
                desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")

            # Dosya adı
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = "basit" if self.ui.radioButton_basit.isChecked() else "gelismis"
            filename = f"muhasebe_{mode}_{current_time}.xlsx"
            file_path = os.path.join(desktop_dir, filename)
            
            # Veri hazırlama
            data = []

            if self.ui.radioButton_basit.isChecked():
                var1_column = self._extract_column_name(self.ui.comboBox_var1.currentText())
                sum_column = self._extract_column_name(self.ui.comboBox_sum.currentText())

                for key, value in sorted(self.analysis_results.items()):
                    data.append({
                        var1_column: key,
                        sum_column: value
                    })
            else:
                var1_column = self._extract_column_name(self.ui.comboBox_var1.currentText())
                var2_column = self._extract_column_name(self.ui.comboBox_var2.currentText())
                sum_column = self._extract_column_name(self.ui.comboBox_sum.currentText())

                for key, value in sorted(self.analysis_results.items()):
                    parts = key.split(' - ')
                    data.append({
                        var1_column: parts[0],
                        var2_column: parts[1] if len(parts) > 1 else "",
                        sum_column: value
                    })

            # Excel'e kaydet
            df_export = pd.DataFrame(data)
            df_export.to_excel(file_path, index=False, engine='openpyxl')

            # Başarı mesajı
            QMessageBox.information(
                self, 
                "✅ Muhasebe Basit Veri Analizi", 
                f"📁 Excel dosyası başarıyla kaydedildi!\n\n"
                f"📝 Dosya: {filename}\n"
                f"📂 Konum: OneDrive/Desktop\n\n"
                f"📊 {len(data)} kayıt aktarıldı"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel dosyası oluşturulurken hata oluştu:\n{str(e)}")


    def setup_chart_canvas(self):
        """Matplotlib canvas'ını kurulum"""
        try:
            # Create figure and canvas
            fig = Figure(figsize=(6, 4), dpi=80)
            self.chart_canvas = FigureCanvas(fig)
            
            # Replace the placeholder widget with the canvas
            layout = QVBoxLayout()
            layout.addWidget(self.chart_canvas)
            
            # Clear any existing layout from chartWidget
            if self.ui.chartWidget.layout():
                QtWidgets.QWidget().setLayout(self.ui.chartWidget.layout())
            
            self.ui.chartWidget.setLayout(layout)
            
            # Initial empty plot
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, '📊\n\nGrafik burada gösterilecek\n\nAnaliz Et butonuna basın', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_xticks([])
            ax.set_yticks([])
            self.chart_canvas.draw()
            
        except ImportError:
            # Eğer matplotlib yüklü değilse, placeholder'ı koru
            pass
    
    def chart_type_changed(self):
        """Grafik türü değiştiğinde grafiği güncelle"""
        if hasattr(self, 'analysis_results') and self.analysis_results:
            self.update_chart()
    
    def update_chart(self):
        """Analiz sonuçlarına göre grafiği güncelle"""
        if not hasattr(self, 'chart_canvas') or self.chart_canvas is None:
            return
            
        try:
            # Figürü temizle
            fig = self.chart_canvas.figure
            fig.clear()
            
            if not self.analysis_results:
                return
                
            # Veriyi hazırla - sadece ilk 31 değeri al
            all_labels = list(self.analysis_results.keys())
            all_values = list(self.analysis_results.values())
            
            # İlk 31 değeri al
            labels = all_labels[:31]
            values = all_values[:31]
            
            # Çok uzun etiketleri kısalt
            short_labels = []
            for label in labels:
                if len(str(label)) > 20:
                    short_labels.append(str(label)[:17] + "...")
                else:
                    short_labels.append(str(label))
            
            ax = fig.add_subplot(111)
            
            # Grafik başlığında kaç veri gösterildiği bilgisi
            total_data_count = len(all_labels)
            shown_data_count = len(labels)
            title_info = f"({shown_data_count}/{total_data_count} veri)" if total_data_count > 31 else f"({total_data_count} veri)"
            
            # Hangi grafik türü seçili?
            if self.ui.radioButton_line.isChecked():
                ax.plot(short_labels, values, marker='o', linewidth=2, markersize=6)
                ax.set_title(f'📈 Çizgi Grafik {title_info}')
            elif self.ui.radioButton_bar.isChecked():
                bars = ax.bar(short_labels, values, alpha=0.7)
                ax.set_title(f'📊 Sütun Grafik {title_info}')
                # Her bara değer yaz
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{value:,.0f}', ha='center', va='bottom', fontsize=8)
            elif self.ui.radioButton_area.isChecked():
                ax.fill_between(range(len(values)), values, alpha=0.6)
                ax.plot(range(len(values)), values, marker='o', linewidth=2)
                ax.set_xticks(range(len(short_labels)))
                ax.set_xticklabels(short_labels)
                ax.set_title(f'📈 Alan Grafik {title_info}')
            
            # Eksenleri biçimlendir
            ax.set_xlabel('Değişkenler')
            ax.set_ylabel('Toplam Değer')
            
            # Y ekseni formatı
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            # X ekseni etiketlerini döndür
            if len(short_labels) > 5:
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Layout'u ayarla
            fig.tight_layout()
            
            # Çiz
            self.chart_canvas.draw()
            
        except Exception as e:
            print(f"Grafik çizme hatası: {e}")
    
    def download_chart(self):
        """Grafiği OneDrive/Desktop'a PNG olarak indir"""
        try:
            if not hasattr(self, 'chart_canvas') or self.chart_canvas is None:
                QMessageBox.warning(self, "Uyarı", "Henüz bir grafik oluşturulmamış!")
                return
                
            if not self.analysis_results:
                QMessageBox.warning(self, "Uyarı", "Henüz analiz yapılmamış!")
                return
            
            # OneDrive/Desktop yolu
            desktop_path = os.path.expanduser("~/OneDrive/Desktop")
            
            # Eğer OneDrive/Desktop yoksa normal Desktop'u kullan
            if not os.path.exists(desktop_path):
                desktop_path = os.path.expanduser("~/Desktop")
            
            # Dosya adını oluştur (tarih-saat ile)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Hangi grafik türü aktif?
            chart_type = "grafik"
            if self.ui.radioButton_line.isChecked():
                chart_type = "cizgi_grafik"
            elif self.ui.radioButton_bar.isChecked():
                chart_type = "sutun_grafik"
            elif self.ui.radioButton_area.isChecked():
                chart_type = "alan_grafik"
            
            filename = f"muhasebe_analiz_{chart_type}_{timestamp}.png"
            file_path = os.path.join(desktop_path, filename)
            
            # Grafiği kaydet
            self.chart_canvas.figure.savefig(
                file_path, 
                dpi=300, 
                bbox_inches='tight', 
                facecolor='white', 
                edgecolor='none'
            )
            
            QMessageBox.information(
                self, 
                "✅ Muhasebe Basit Veri Analizi", 
                f"🖼️ Grafik başarıyla kaydedildi!\n\n"
                f"📝 Dosya: {filename}\n"
                f"📂 Konum: OneDrive/Desktop\n\n"
                f"🎨 {chart_type.replace('_', ' ').title()} formatında"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Grafik kaydedilirken hata oluştu:\n{str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())