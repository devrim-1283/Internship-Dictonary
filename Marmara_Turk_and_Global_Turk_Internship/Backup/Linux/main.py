import sys
import psutil
import os
import platform
import logging
from datetime import datetime
from PyQt5 import QtWidgets, QtCore, QtGui
from backup_ui import Ui_Form
from PyQt5.QtCore import QThread, pyqtSignal
import shutil
from zipfile import ZipFile, ZIP_DEFLATED
import pyminizip
import json  # En üste ekleyin
from pathlib import Path

class BackupThread(QThread):
    """Yedekleme işlemini ayrı bir thread'de yapar"""
    finished = pyqtSignal(int, int)  # total_copied, total_skipped
    error = pyqtSignal(str)
    progress = pyqtSignal(str)  # İlerleme durumu için

    def __init__(self, source_paths, backup_path, compress=False, encrypt=False, password=None):
        super().__init__()
        self.source_paths = source_paths
        self.backup_path = backup_path
        self.compress = compress
        self.encrypt = encrypt
        self.password = password  # password'ü encode etmeye gerek yok
        self._is_running = True

    def stop(self):
        """Thread'i durdur"""
        self._is_running = False
        self.wait(1000)  # 1 saniye bekle
        if self.isRunning():
            self.terminate()  # Hala çalışıyorsa zorla sonlandır
            self.wait()  # Sonlanmasını bekle
            # Yarım kalan dosyaları temizle
            if os.path.exists(self.backup_path):
                try:
                    shutil.rmtree(self.backup_path)
                except:
                    pass
            # Yarım kalan arşivi temizle
            archive_path = f"{self.backup_path}.7z"
            if os.path.exists(archive_path):
                try:
                    os.remove(archive_path)
                except:
                    pass

    def run(self):
        try:
            total_copied = 0
            total_skipped = 0
            
            # 1. AŞAMA: Normal Yedekleme
            for source_path in self.source_paths:
                if not self._is_running:
                    self.progress.emit("Yedekleme işlemi durduruluyor...")
                    if os.path.exists(self.backup_path):
                        shutil.rmtree(self.backup_path)
                    self.finished.emit(total_copied, total_skipped)
                    return

                if source_path.endswith('*'):
                    self.progress.emit(f"Klasör görmezden gelindi: {source_path}")
                    total_skipped += 1
                    continue
                
                folder_name = os.path.basename(source_path)
                target_path = os.path.join(self.backup_path, folder_name)
                
                try:
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path)
                    
                    self.progress.emit(f"Yedekleniyor: {source_path}")
                    shutil.copytree(source_path, target_path, symlinks=False, ignore=None)
                    total_copied += 1
                    self.progress.emit(f"Klasör yedeklendi: {source_path}")
                except Exception as e:
                    self.error.emit(f"Klasör yedeklenirken hata: {source_path} - {str(e)}")
                    return

            # 2. AŞAMA: Sıkıştırma ve Şifreleme
            if self.compress and self._is_running:
                try:
                    zip_path = f"{self.backup_path}.zip"
                    self.progress.emit("Dosyalar sıkıştırılıyor...")

                    if self.encrypt:
                        # Şifreli zip oluştur
                        self.progress.emit("Şifreli zip dosyası oluşturuluyor...")
                        
                        # Yedeklenen dosyaları listele
                        files_to_zip = []
                        arc_names = []
                        for root, dirs, files in os.walk(self.backup_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, os.path.dirname(self.backup_path))
                                files_to_zip.append(file_path)
                                arc_names.append(arc_name)
                        
                        # Şifreli zip oluştur
                        pyminizip.compress_multiple(
                            files_to_zip,  # Dosya yolları
                            arc_names,     # Zip içindeki yolları
                            zip_path,      # Hedef zip dosyası
                            self.password, # Şifre
                            5             # Sıkıştırma seviyesi (1-9)
                        )
                        self.progress.emit("Zip dosyası şifrelendi")
                    else:
                        # Normal zip oluştur
                        with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as zf:
                            for root, dirs, files in os.walk(self.backup_path):
                                for file in files:
                                    if not self._is_running:
                                        break
                                    file_path = os.path.join(root, file)
                                    arc_name = os.path.relpath(file_path, os.path.dirname(self.backup_path))
                                    zf.write(file_path, arc_name)
                        self.progress.emit("Zip dosyası oluşturuldu")

                    # Orijinal klasörü sil
                    if os.path.exists(self.backup_path) and self._is_running:
                        shutil.rmtree(self.backup_path)
                        self.progress.emit("Orijinal klasör silindi")

                except Exception as e:
                    self.error.emit(f"Zip oluşturma hatası: {str(e)}")
                    return

            if not self._is_running:
                self.progress.emit("Yedekleme işlemi kullanıcı tarafından durduruldu")
            
            self.finished.emit(total_copied, total_skipped)
            
        except Exception as e:
            self.error.emit(str(e))

class BackupApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Get application directory first
        self.app_dir = Path.home() / '.local/share/backup-app'
        self.app_dir.mkdir(parents=True, exist_ok=True)  # Create if not exists
        
        self.config_dir = self.app_dir / 'config'
        self.config_dir.mkdir(exist_ok=True)  # Create if not exists
        
        self.config_file = self.config_dir / 'backup_config.json'
        
        # Then setup logging
        self.setup_logging()
        
        # Model oluştur
        self.list_model = QtCore.QStringListModel()
        self.ui.listView.setModel(self.list_model)
        
        # ListView seçim değişikliğini izle
        self.ui.listView.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Sil butonuna tıklama olayını bağla
        self.ui.pushButton_2.clicked.connect(self.delete_selected_item)
        
        # Görmezden Gel butonuna tıklama olayını bağla
        self.ui.pushButton_3.clicked.connect(self.ignore_selected_item)
        
        # Ekle butonuna tıklama olayını bağla
        self.ui.pushButton.clicked.connect(self.add_folder)
        
        # Yedekle butonuna tıklama olayını bağla
        self.ui.pushButton_11.clicked.connect(self.start_backup)
        
        # Saat için timer oluştur
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Her 1 saniyede bir güncelle
        
        # Başlangıçta saati güncelle
        self.update_time()
        
        # Başlangıçta diskleri listele
        self.list_removable_drives()
        
        # Başlangıç durumlarını ayarla
        self.set_initial_states()
        
        # Varsayılan klasörleri ekle
        self.add_default_folders()
        
        # Buton bağlantıları
        self.ui.pushButton_6.clicked.connect(self.refresh_drives)  # Yenile butonu
        self.ui.pushButton_5.clicked.connect(self.delete_key_file)  # Diski Sil butonu
        self.ui.checkBox_4.stateChanged.connect(self.toggle_folder_controls)  # Klasör düzenleme kontrolü
        self.ui.checkBox.stateChanged.connect(self.on_encrypt_changed)  # Şifrele
        self.ui.checkBox_2.stateChanged.connect(self.on_compress_changed)  # Sıkıştır
        
        # Yedekleme süresi için timer
        self.backup_timer = QtCore.QTimer()
        self.backup_timer.timeout.connect(self.update_backup_duration)
        self.backup_start_time = None
        
        self.backup_thread = None  # Yedekleme thread'i için değişken
        
        # Şifre kaydetme butonuna tıklama olayını bağla
        self.ui.pushButton_7.clicked.connect(self.save_default_password)
        
        # Başlangıçta varsayılan şifreyi yükle
        self.load_default_password()

    def update_time(self):
        """Anlık saati günceller"""
        current_time = datetime.now().strftime('%H:%M:%S') # Salise için son 4 haneyi al
        self.ui.label_4.setText(f"Saat: {current_time}")

    def setup_logging(self):
        """Configure logging to save in application directory"""
        log_file = self.app_dir / 'backup_log.txt'
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def check_key_file(self, mount_point):
        """Disk içinde .key dosyasını kontrol eder"""
        try:
            key_path = os.path.join(mount_point, '.key')
            if os.path.exists(key_path):
                with open(key_path, 'r') as key_file:
                    key_content = key_file.read().strip()
                    return key_content == "92047758821781743658436587323"
            return False
        except Exception as e:
            logging.error(f"Key dosyası kontrolünde hata: {str(e)}")
            return False

    def list_removable_drives(self):
        """Çıkarılabilir diskleri tespit edip combobox'a ekler"""
        self.ui.comboBox_2.clear()
        
        for partition in psutil.disk_partitions(all=True):
            try:
                system = platform.system().lower()
                is_removable = False
                disk_info = ""
                
                if system == "windows":
                    if partition.opts.startswith('rw,') and 'fixed' not in partition.opts:
                        is_removable = True
                        drive_letter = partition.mountpoint.split(':')[0] + ":\\"
                        usage = psutil.disk_usage(partition.mountpoint)
                        total_size = usage.total / (1024 * 1024 * 1024)
                        disk_info = f"{drive_letter} ({total_size:.1f} GB)"
                
                elif system == "linux":
                    if ("/media/" in partition.mountpoint or 
                        "/mnt/" in partition.mountpoint or 
                        "removable" in partition.opts.lower()):
                        is_removable = True
                        usage = psutil.disk_usage(partition.mountpoint)
                        total_size = usage.total / (1024 * 1024 * 1024)
                        disk_info = f"{partition.device} ({total_size:.1f} GB)"
                
                if is_removable and self.check_key_file(partition.mountpoint):
                    self.ui.comboBox_2.addItem(disk_info, partition.mountpoint)
                    logging.info(f"Geçerli disk bulundu: {disk_info}")
                elif is_removable:
                    logging.warning(f"Geçersiz key dosyası: {disk_info}")
                    
            except Exception as e:
                logging.error(f"Disk tarama hatası: {str(e)}")
                continue

    def delete_key_file(self):
        """Seçili diskteki .key dosyasını siler"""
        try:
            current_index = self.ui.comboBox_2.currentIndex()
            if current_index == -1:
                logging.warning("Disk seçilmedi")
                return

            mount_point = self.ui.comboBox_2.currentData()
            key_path = os.path.join(mount_point, '.key')

            if os.path.exists(key_path):
                os.remove(key_path)
                logging.info(f"Key dosyası silindi: {key_path}")
            else:
                logging.warning("Key dosyası bulunamadı")

            self.list_removable_drives()

        except Exception as e:
            logging.error(f"Key dosyası silinirken hata oluştu: {str(e)}")

    def refresh_drives(self):
        """Diskleri yeniden tarar ve listeler"""
        try:
            logging.info("Disk taraması başlatıldı")
            self.list_removable_drives()
            logging.info("Disk taraması tamamlandı")
        except Exception as e:
            logging.error(f"Disk yenileme hatası: {str(e)}")

    def set_initial_states(self):
        """Başlangıç durumlarını ayarlar"""
        # Butonları ve ListView'i devre dışı bırak
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.listView.setEnabled(False)
        
        # CheckBox'ı işaretsiz yap
        self.ui.checkBox_4.setChecked(False)
        
        logging.info("Başlangıç durumları ayarlandı")

    def toggle_folder_controls(self, state):
        """Klasör düzenleme kontrollerinin durumunu değiştirir"""
        try:
            # CheckBox işaretli ise kontrolleri etkinleştir
            is_enabled = state == 2  # Qt.Checked = 2
            
            self.ui.pushButton.setEnabled(is_enabled)
            self.ui.listView.setEnabled(is_enabled)
            
            # Sil ve Görmezden Gel butonları için ListView'de seçim kontrolü yap
            if is_enabled:
                has_selection = len(self.ui.listView.selectedIndexes()) > 0
                self.ui.pushButton_2.setEnabled(has_selection)
                self.ui.pushButton_3.setEnabled(has_selection)
            else:
                self.ui.pushButton_2.setEnabled(False)
                self.ui.pushButton_3.setEnabled(False)
            
            status = "etkinleştirildi" if is_enabled else "devre dışı bırakıldı"
            logging.info(f"Klasör düzenleme kontrolleri {status}")
            
        except Exception as e:
            logging.error(f"Klasör düzenleme kontrolleri değiştirilirken hata: {str(e)}")

    def add_default_folders(self):
        """İşletim sistemine göre varsayılan klasörleri ekler"""
        try:
            system = platform.system().lower()
            default_paths = []

            if system == "windows":
                # Windows için özel klasör yolları
                import winreg
                
                # Desktop yolu
                desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
                # Belgeler yolu
                documents = os.path.join(os.path.expanduser('~'), 'Documents')
                
                default_paths.extend([desktop, documents])
                
            elif system == "linux":
                # Linux için özel klasör yolları
                home = os.path.expanduser('~')
                desktop = os.path.join(home, 'Desktop')
                documents = os.path.join(home, 'Documents')
                
                # XDG kullanıyorsa farklı isimler olabilir
                if not os.path.exists(desktop):
                    desktop = os.path.join(home, 'Masaüstü')
                if not os.path.exists(documents):
                    documents = os.path.join(home, 'Belgeler')
                
                default_paths.extend([desktop, documents])

            # Var olan yolları kontrol et ve listeye ekle
            valid_paths = [path for path in default_paths if os.path.exists(path)]
            
            # Model'e ekle
            self.list_model.setStringList(valid_paths)
            
            logging.info(f"Varsayılan klasörler eklendi: {valid_paths}")
            
        except Exception as e:
            logging.error(f"Varsayılan klasörler eklenirken hata: {str(e)}")

    def on_selection_changed(self, selected, deselected):
        """ListView'de seçim değiştiğinde çalışır"""
        try:
            # Seçili öğe varsa butonları aktif et
            has_selection = len(self.ui.listView.selectedIndexes()) > 0
            if self.ui.checkBox_4.isChecked():  # Klasörleri düzenle işaretli ise
                self.ui.pushButton_2.setEnabled(has_selection)
                self.ui.pushButton_3.setEnabled(has_selection)
                
                # Seçili öğenin durumuna göre buton metnini güncelle
                if has_selection:
                    selected_index = self.ui.listView.selectedIndexes()[0]
                    current_text = self.list_model.data(selected_index, QtCore.Qt.DisplayRole)
                    if current_text.endswith('*'):
                        self.ui.pushButton_3.setText("Görmezden Gelme")
                    else:
                        self.ui.pushButton_3.setText("Görmezden Gel")
            
            if has_selection:
                logging.info("Listeden öğe seçildi")
            else:
                logging.info("Liste seçimi kaldırıldı")
                
        except Exception as e:
            logging.error(f"Seçim kontrolünde hata: {str(e)}")

    def delete_selected_item(self):
        """Listeden seçili öğeyi siler"""
        try:
            # Seçili indeksi al
            selected_indexes = self.ui.listView.selectedIndexes()
            if not selected_indexes:
                return
                
            # Seçili öğeyi al
            selected_index = selected_indexes[0]
            selected_item = self.list_model.data(selected_index, QtCore.Qt.DisplayRole)
            
            # Modelden öğeyi sil
            self.list_model.removeRow(selected_index.row())
            
            logging.info(f"Listeden silinen öğe: {selected_item}")
            
            # Seçim kaldırıldığında sil butonu otomatik olarak disable olacak
            
        except Exception as e:
            logging.error(f"Öğe silinirken hata: {str(e)}")

    def ignore_selected_item(self):
        """Seçili öğeyi görmezden gelir veya görmezden gelmeyi kaldırır"""
        try:
            # Seçili indeksi al
            selected_indexes = self.ui.listView.selectedIndexes()
            if not selected_indexes:
                return
                
            # Seçili öğeyi al
            selected_index = selected_indexes[0]
            current_text = self.list_model.data(selected_index, QtCore.Qt.DisplayRole)
            
            # Yıldız durumuna göre işlem yap
            if current_text.endswith('*'):
                # Yıldızı kaldır
                new_text = current_text[:-1]  # Son karakteri (*) kaldır
                self.ui.pushButton_3.setText("Görmezden Gel")
            else:
                # Yıldız ekle
                new_text = f"{current_text}*"
                self.ui.pushButton_3.setText("Görmezden Gelme")
            
            # Öğeyi güncelle
            self.list_model.setData(selected_index, new_text)
            
            action = "görmezden gelme kaldırıldı" if current_text.endswith('*') else "görmezden gelindi"
            logging.info(f"Öğe {action}: {current_text}")
            
        except Exception as e:
            logging.error(f"Öğe görmezden gelme işleminde hata: {str(e)}")

    def add_folder(self):
        """Klasör seçme dialogu açar ve seçilen klasörü listeye ekler"""
        try:
            # Klasör seçme dialogunu aç
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Klasör Seç",
                os.path.expanduser('~'),  # Başlangıç dizini olarak home klasörü
                QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
            )
            
            # Eğer klasör seçilmişse
            if folder_path:
                # Mevcut liste öğelerini al
                current_items = []
                for i in range(self.list_model.rowCount()):
                    item = self.list_model.data(self.list_model.index(i, 0), QtCore.Qt.DisplayRole)
                    current_items.append(item)
                
                # Eğer klasör zaten listede yoksa ekle
                if folder_path not in current_items:
                    current_items.append(folder_path)
                    self.list_model.setStringList(current_items)
                    logging.info(f"Yeni klasör eklendi: {folder_path}")
                else:
                    logging.warning(f"Klasör zaten listede mevcut: {folder_path}")
            else:
                logging.info("Klasör seçimi iptal edildi")
                
        except Exception as e:
            logging.error(f"Klasör ekleme hatası: {str(e)}")

    def toggle_password_controls(self, state):
        """Şifre kontrollerinin durumunu değiştirir"""
        try:
            # CheckBox işaretli ise kontrolleri etkinleştir
            is_enabled = state == 2  # Qt.Checked = 2
            
            self.ui.lineEdit.setEnabled(is_enabled)
            self.ui.pushButton_7.setEnabled(is_enabled)
            
            status = "etkinleştirildi" if is_enabled else "devre dışı bırakıldı"
            logging.info(f"Şifre kontrolleri {status}")
            
        except Exception as e:
            logging.error(f"Şifre kontrolleri değiştirilirken hata: {str(e)}")

    def disable_all_controls(self):
        """Tüm kontrolleri devre dışı bırakır"""
        # ComboBox'lar
        self.ui.comboBox_2.setEnabled(False)
        
        # CheckBox'lar
        self.ui.checkBox.setEnabled(False)
        self.ui.checkBox_2.setEnabled(False)
        self.ui.checkBox_4.setEnabled(False)
        
        # LineEdit'ler
        self.ui.lineEdit.setEnabled(False)
        self.ui.lineEdit_2.setEnabled(False)
        
        # Butonlar
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_8.setEnabled(False)
        
        # Yedekle butonunun metnini değiştir
        self.ui.pushButton_11.setText("Yedeklemeyi Durdur")
        
        # ListView
        self.ui.listView.setEnabled(False)

    def enable_all_controls(self):
        """Tüm kontrolleri tekrar etkinleştirir"""
        # ComboBox'lar
        self.ui.comboBox_2.setEnabled(True)
        
        # CheckBox'lar
        self.ui.checkBox.setEnabled(True)
        self.ui.checkBox_2.setEnabled(True)
        self.ui.checkBox_4.setEnabled(True)
        
        # LineEdit'ler
        self.ui.lineEdit.setEnabled(self.ui.checkBox.isChecked())  # Şifreleme durumuna göre
        self.ui.lineEdit_2.setEnabled(True)
        
        # Butonlar
        self.ui.pushButton_5.setEnabled(True)
        self.ui.pushButton_6.setEnabled(True)
        self.ui.pushButton_7.setEnabled(self.ui.checkBox.isChecked())  # Şifreleme durumuna göre
        self.ui.pushButton_8.setEnabled(True)
        self.ui.pushButton_11.setEnabled(True)
        
        # Klasör düzenleme durumuna göre kontrolleri ayarla
        self.toggle_folder_controls(2 if self.ui.checkBox_4.isChecked() else 0)

    def update_backup_duration(self):
        """Yedekleme süresini günceller"""
        if self.backup_start_time:
            elapsed = datetime.now() - self.backup_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.ui.label_6.setText(f"Süre: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def on_encrypt_changed(self, state):
        """Şifrele checkbox'ı değiştiğinde çalışır"""
        try:
            is_checked = state == 2  # Qt.Checked = 2
            
            # Şifreleme seçilirse sıkıştırmayı da otomatik seç
            if is_checked:
                self.ui.checkBox_2.setChecked(True)
            
            # Şifre kontrollerini güncelle
            self.toggle_password_controls(state)
            
            logging.info(f"Şifreleme {'etkinleştirildi' if is_checked else 'devre dışı bırakıldı'}")
            
        except Exception as e:
            logging.error(f"Şifreleme durumu değiştirilirken hata: {str(e)}")

    def on_compress_changed(self, state):
        """Sıkıştır checkbox'ı değiştiğinde çalışır"""
        try:
            is_checked = state == 2  # Qt.Checked = 2
            
            # Sıkıştırma kaldırılırsa şifrelemeyi de kaldır
            if not is_checked and self.ui.checkBox.isChecked():
                self.ui.checkBox.setChecked(False)
            
            logging.info(f"Sıkıştırma {'etkinleştirildi' if is_checked else 'devre dışı bırakıldı'}")
            
        except Exception as e:
            logging.error(f"Sıkıştırma durumu değiştirilirken hata: {str(e)}")

    def start_backup(self):
        """Seçili klasörleri yedekler veya yedeklemeyi durdurur"""
        try:
            # Eğer yedekleme çalışıyorsa durdur
            if self.backup_thread and self.backup_thread.isRunning():
                self.ui.pushButton_11.setEnabled(False)  # Butonu geçici olarak devre dışı bırak
                self.progress.emit("Yedekleme durduruluyor, lütfen bekleyin...")
                self.backup_thread.stop()
                self.backup_timer.stop()
                self.backup_start_time = None
                self.enable_all_controls()
                self.ui.pushButton_11.setText("Yedekle")
                self.ui.pushButton_11.setEnabled(True)  # Butonu tekrar etkinleştir
                logging.info("Yedekleme kullanıcı tarafından durduruldu")
                return

            # Şifreleme ve sıkıştırma durumlarını kontrol et
            is_compress = self.ui.checkBox_2.isChecked()
            is_encrypt = self.ui.checkBox.isChecked()
            
            # Şifreleme seçili ise şifre kontrolü yap
            if is_encrypt:
                password = self.ui.lineEdit.text()
                if not password:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Şifre Hatası",
                        "Şifreleme seçili iken şifre boş olamaz!"
                    )
                    return
            else:
                password = None

            # Disk seçili mi kontrol et
            current_disk_index = self.ui.comboBox_2.currentIndex()
            if current_disk_index == -1:
                logging.warning("Yedekleme için disk seçilmedi")
                return

            # Kontrolleri devre dışı bırak
            self.disable_all_controls()
            
            # Yedekleme başlangıç zamanını ayarla
            self.backup_start_time = datetime.now()
            self.ui.label_5.setText(f"Başlangıç Saati: {self.backup_start_time.strftime('%H:%M:%S')}")
            
            # Süre sayacını başlat
            self.backup_timer.start(1000)

            # Hedef disk yolunu al
            target_disk = self.ui.comboBox_2.currentData()
            
            # Backup klasörünü kontrol et/oluştur
            backup_folder = os.path.join(target_disk, "Backup")
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
                logging.info(f"Backup klasörü oluşturuldu: {backup_folder}")

            # Bugünün tarihiyle klasör oluştur/kontrol et
            current_date = datetime.now().strftime('%d.%m.%Y')
            date_folder = os.path.join(backup_folder, current_date)
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)
                logging.info(f"Tarih klasörü oluşturuldu: {date_folder}")

            # Bilgisayar adıyla klasör oluştur
            pc_name = self.ui.lineEdit_2.text()
            backup_path = os.path.join(date_folder, pc_name)
            
            # Eğer klasör varsa sil
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
                logging.info(f"Eski yedekleme klasörü silindi: {backup_path}")
            
            # Yeni klasörü oluştur
            os.makedirs(backup_path)
            logging.info(f"Yedekleme klasörü oluşturuldu: {backup_path}")

            # Yedeklenecek klasörleri al
            source_paths = []
            for i in range(self.list_model.rowCount()):
                path = self.list_model.data(self.list_model.index(i, 0), QtCore.Qt.DisplayRole)
                source_paths.append(path)

            # Yedekleme thread'ini başlat
            self.backup_thread = BackupThread(
                source_paths, 
                backup_path,
                compress=is_compress,
                encrypt=is_encrypt,
                password=password
            )
            self.backup_thread.finished.connect(self.on_backup_finished)
            self.backup_thread.error.connect(self.on_backup_error)
            self.backup_thread.progress.connect(self.on_backup_progress)
            self.backup_thread.start()
            
        except Exception as e:
            self.on_backup_error(str(e))

    def on_backup_finished(self, total_copied, total_skipped):
        """Yedekleme tamamlandığında çalışır"""
        self.backup_timer.stop()
        self.backup_start_time = None
        self.update_backup_duration()
        self.enable_all_controls()
        self.ui.pushButton_11.setText("Yedekle")  # Butonu eski haline getir
        logging.info(f"Yedekleme tamamlandı. Kopyalanan: {total_copied}, Atlanan: {total_skipped}")

    def on_backup_error(self, error_message):
        """Yedekleme hatası olduğunda çalışır"""
        self.backup_timer.stop()
        self.backup_start_time = None
        self.enable_all_controls()
        self.ui.pushButton_11.setText("Yedekle")  # Butonu eski haline getir
        logging.error(f"Yedekleme işleminde hata: {error_message}")

    def on_backup_progress(self, message):
        """Yedekleme ilerlemesini loglar"""
        logging.info(message)

    def save_default_password(self):
        """Save the default password to config file"""
        try:
            # Get new password
            new_password = self.ui.lineEdit.text()
            
            if not new_password:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Password Error",
                    "Password cannot be empty!"
                )
                return
            
            # Create config
            config = {
                'default_password': new_password
            }
            
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to config file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "Default password saved!"
            )
            logging.info("Default password updated")
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error saving password: {str(e)}"
            )
            logging.error(f"Password save error: {str(e)}")

    def load_default_password(self):
        """Load the default password from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_password = config.get('default_password', '112.st!?')
            else:
                default_password = '112.st!?'  # Default password
            
            self.ui.lineEdit.setText(default_password)
            logging.info("Default password loaded")
            
        except Exception as e:
            logging.error(f"Default password load error: {str(e)}")
            self.ui.lineEdit.setText('112.st!?')

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 