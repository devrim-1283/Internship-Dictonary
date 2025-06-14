import sys
import pandas as pd
import os
from datetime import datetime
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from gui import Ui_Form


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
       
        self.ui.pushButton.clicked.connect(self.select_file)
        self.ui.pushButton_3.clicked.connect(self.analyze_data)
        self.ui.pushButton_4.clicked.connect(self.export_to_excel)
        
        self.selected_file_path = None
        self.analysis_results = {}  # Store analysis results
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Dosya Seç", 
            "",  
            "Excel Dosyaları (*.xlsx)" 
        )
        if file_path:
            self.selected_file_path = file_path
            self.ui.label.setText(file_path)
        else:
            self.ui.label.setText(" ")
            self.selected_file_path = None

    
    def analyze_data(self):
        """Analyze Excel file and group transactions by date"""
        if not self.selected_file_path:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir dosya seçin!")
            return
        
        try:
            df = pd.read_excel(self.selected_file_path)
            
            date_column = None
            amount_column = None
            
    
            for col in df.columns:
                if col == 'İşlem Tarihi':
                    date_column = col
                    continue
            
                if col == 'Tutar':
                    amount_column = col
                    continue
            
            if date_column is None:
                QMessageBox.warning(self, "Hata", "Tarih sütunu bulunamadı!")
                return
            
            if amount_column is None:
                QMessageBox.warning(self, "Hata", "Tutar sütunu bulunamadı!")
                return
            
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            

            df[amount_column] = pd.to_numeric(df[amount_column], errors='coerce')

            df = df.dropna(subset=[date_column, amount_column])

            grouped = df.groupby(df[date_column].dt.date)[amount_column].sum()
            

            self.analysis_results = {}
            for date, total in grouped.items():
                date_str = date.strftime('%d.%m.%Y')
                self.analysis_results[date_str] = total
            
            # Create table model and populate table view
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(['Tarih', 'Toplam Tutar'])
            
            # Sort dates and add to table
            sorted_dates = sorted(self.analysis_results.keys(), key=lambda x: pd.to_datetime(x, format='%d.%m.%Y'))
            
            for date_str in sorted_dates:
                total = self.analysis_results[date_str]
                
                date_item = QStandardItem(date_str)
                amount_item = QStandardItem(f"{total:,.2f}")
                
                model.appendRow([date_item, amount_item])
            
            # Set model to table view
            self.ui.tableView.setModel(model)
            
            # Adjust column widths
            self.ui.tableView.resizeColumnsToContents()
            
            QMessageBox.information(self, "Başarılı", f"Analiz tamamlandı! {len(self.analysis_results)} günlük veri tabloya yüklendi.")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya analizi sırasında hata oluştu:\n{str(e)}")

    def export_to_excel(self):
        """Export analysis results to Excel file in application directory"""
        if not self.analysis_results:
            QMessageBox.warning(self, "Uyarı", "Excel'e aktarmak için önce analiz yapınız!")
            return
        
        try:
            # Get desktop directory
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            
            # Create filename with current timestamp
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ciro_analizi_{current_time}.xlsx"
            file_path = os.path.join(desktop_dir, filename)
            
            # Prepare data for Excel
            data = []
            sorted_dates = sorted(self.analysis_results.keys(), key=lambda x: pd.to_datetime(x, format='%d.%m.%Y'))
            
            for date_str in sorted_dates:
                data.append({
                    'Tarih': date_str,
                    'Toplam Tutar': self.analysis_results[date_str]
                })
            
            # Create DataFrame and save to Excel
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            # Show success message
            QMessageBox.information(
                self, 
                "Başarılı", 
                f"Excel dosyası başarıyla oluşturuldu!\n\n"
                f"Dosya adı: {filename}\n"
                f"Konum: {desktop_dir}\n\n"
                f"Toplam {len(data)} günlük veri aktarıldı."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel dosyası oluşturulurken hata oluştu:\n{str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
