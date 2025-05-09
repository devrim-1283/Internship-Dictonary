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
import subprocess
import json
import pyzipper

class BackupThread(QThread):
    finished = pyqtSignal(int, int)  
    error = pyqtSignal(str)
    progress = pyqtSignal(str) 
    def __init__(self, source_paths, backup_path, compress=False, encrypt=False, password=None):
        super().__init__()
        self.source_paths = source_paths
        self.backup_path = backup_path
        self.compress = compress
        self.encrypt = encrypt
        self.password = password  
        self._is_running = True

    def stop(self):
        
        self._is_running = False
        self.progress.emit("Stopping backup process...")
        
        
        if self.isRunning():
            self.wait(2000)  
            if self.isRunning():  
                self.terminate()  
                self.wait()  
        
        try:
            if os.path.exists(self.backup_path):
                shutil.rmtree(self.backup_path, ignore_errors=True)
            
            zip_path = f"{self.backup_path}.zip"
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except:
            pass

    def run(self):
        try:
            total_copied = 0
            total_skipped = 0
            
            # 1. AŞAMA: Normal Yedekleme
            for source_path in self.source_paths:
                # Durdurma kontrolü
                if not self._is_running:
                    self.progress.emit("Stopping backup process...")
                    if os.path.exists(self.backup_path):
                        shutil.rmtree(self.backup_path, ignore_errors=True)
                    self.finished.emit(total_copied, total_skipped)
                    return

                if source_path.endswith('*'):
                    self.progress.emit(f"Folder ignored: {source_path}")
                    total_skipped += 1
                    continue
                
                folder_name = os.path.basename(source_path)
                target_path = os.path.join(self.backup_path, folder_name)
                
                try:
                    if os.path.exists(target_path):
                        shutil.rmtree(target_path, ignore_errors=True)
                    
                    self.progress.emit(f"Backing up: {source_path}")
                    
                    
                    def copy_with_retry(src, dst):
                        try:
                            if os.path.exists(dst):
                                shutil.rmtree(dst, ignore_errors=True)
                            
                            os.makedirs(dst, exist_ok=True)
                            
                            for root, dirs, files in os.walk(src):
                                if not self._is_running:
                                    return False
                                
                                for dir_name in dirs:
                                    if not self._is_running:  
                                        return False
                                        
                                    src_dir = os.path.join(root, dir_name)
                                    dst_dir = os.path.join(dst, os.path.relpath(src_dir, src))
                                    try:
                                        os.makedirs(dst_dir, exist_ok=True)
                                    except:
                                        self.progress.emit(f"Could not create folder: {dst_dir}")
                                
                                for file_name in files:
                                    if not self._is_running:  
                                        return False
                                        
                                    src_file = os.path.join(root, file_name)
                                    dst_file = os.path.join(dst, os.path.relpath(src_file, src))
                                    try:
                                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                                        shutil.copy2(src_file, dst_file)
                                    except Exception as e:
                                        self.progress.emit(f"Could not copy file: {src_file}")
                                        continue
                            return True
                        except Exception as e:
                            self.progress.emit(f"Copy error: {str(e)}")
                            return False

                    if copy_with_retry(source_path, target_path):
                        total_copied += 1
                        self.progress.emit(f"Folder backed up: {source_path}")
                    else:
                        if not self._is_running:
                            self.progress.emit("Stopping backup process...")
                            if os.path.exists(self.backup_path):
                                shutil.rmtree(self.backup_path, ignore_errors=True)
                            self.finished.emit(total_copied, total_skipped)
                            return
                        
                        self.progress.emit(f"Could not backup folder: {source_path}")
                        total_skipped += 1
                    
                except Exception as e:
                    self.progress.emit(f"Error while backing up folder: {source_path} - {str(e)}")
                    total_skipped += 1
                    continue

                if not self._is_running:
                    self.progress.emit("Stopping backup process...")
                    if os.path.exists(self.backup_path):
                        shutil.rmtree(self.backup_path, ignore_errors=True)
                    self.finished.emit(total_copied, total_skipped)
                    return


            if self.compress and total_copied > 0 and self._is_running:  
                try:
                    self.progress.emit("Compressing files...")
                    
                    zip_path = f"{self.backup_path}.zip"
                    
                    if os.path.exists(zip_path):
                        try:
                            os.remove(zip_path)
                        except:
                            pass
                    
                    if self.encrypt and self.password:
                        self.progress.emit("Creating encrypted zip file...")
                        with pyzipper.AESZipFile(zip_path,
                                               'w',
                                               compression=pyzipper.ZIP_DEFLATED,
                                               encryption=pyzipper.WZ_AES) as zf:
                            zf.setpassword(self.password.encode())
                            for root, dirs, files in os.walk(self.backup_path):
                                for file in files:
                                    try:
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_path, os.path.dirname(self.backup_path))
                                        self.progress.emit(f"Compressing: {arcname}")
                                        zf.write(file_path, arcname)
                                    except:
                                        continue
                        self.progress.emit("Encrypted zip file created")
                    else:
                        with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as zipf:
                            for root, dirs, files in os.walk(self.backup_path):
                                if not self._is_running:
                                    break
                                    
                                for file in files:
                                    if not self._is_running:
                                        break
                                    
                                    try:
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_path, os.path.dirname(self.backup_path))
                                        self.progress.emit(f"Compressing: {arcname}")
                                        zipf.write(file_path, arcname)
                                    except:
                                        continue
                        self.progress.emit("Zip file created")
                    
                    if not self._is_running:
                        if os.path.exists(zip_path):
                            os.remove(zip_path)
                        self.progress.emit("Stopping backup process...")
                        self.finished.emit(total_copied, total_skipped)
                        return
                    
                    self.progress.emit("Original folder deleted")
                    
                    if os.path.exists(self.backup_path):
                        shutil.rmtree(self.backup_path, ignore_errors=True)
                    
                except Exception as e:
                    self.error.emit(f"Error while compressing files: {str(e)}")
                    return
            
            self.finished.emit(total_copied, total_skipped)
            
        except Exception as e:
            self.error.emit(str(e))

class BackupApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        if hasattr(sys, 'frozen'):
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        self.list_model = QtCore.QStringListModel()
        self.ui.listView.setModel(self.list_model)
        
        self.ui.listView.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        self.ui.pushButton_2.clicked.connect(self.delete_selected_item)
        
        self.ui.pushButton_3.clicked.connect(self.ignore_selected_item)
        
        self.ui.pushButton.clicked.connect(self.add_folder)
        
        self.ui.pushButton_11.clicked.connect(self.toggle_backup)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) 
        
        self.update_time()
        
        self.setup_logging()
        
        self.list_removable_drives()
        
        self.set_initial_states()
        
        self.add_default_folders()
        
        self.ui.pushButton_6.clicked.connect(self.refresh_drives)  # Yenile butonu
        self.ui.pushButton_5.clicked.connect(self.delete_key_file)  # Diski Sil butonu
        self.ui.checkBox_4.stateChanged.connect(self.toggle_folder_controls)  # Klasör düzenleme kontrolü
        self.ui.checkBox.stateChanged.connect(self.on_encrypt_changed)  # Şifrele
        self.ui.checkBox_2.stateChanged.connect(self.on_compress_changed)  # Sıkıştır
        
        self.backup_timer = QtCore.QTimer()
        self.backup_timer.timeout.connect(self.update_backup_duration)
        self.backup_start_time = None
        
        self.backup_thread = None  
        
        self.ui.pushButton_7.clicked.connect(self.save_default_password)
        
        self.load_default_password()
        
        self.is_backup_running = False
        
        # Reset Changes butonuna tıklama olayını bağla
        self.ui.pushButton_8.clicked.connect(self.reset_to_defaults)

    def update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S') 
        self.ui.label_4.setText(f"Time: {current_time}")

    def setup_logging(self):
        log_file = 'backup_log.txt'
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def check_key_file(self, mount_point):
        try:
            key_path = os.path.join(mount_point, '.key')
            if os.path.exists(key_path):
                with open(key_path, 'r') as key_file:
                    key_content = key_file.read().strip()
                    return key_content == "92047758821781743658436587323"
            return False
        except Exception as e:
            logging.error(f"Error checking key file: {str(e)}")
            return False

    def list_removable_drives(self):
        self.ui.comboBox_2.clear()
        
        try:
            for partition in psutil.disk_partitions(all=True):
                try:
                    if 'removable' in partition.opts.lower():
                        drive_path = partition.mountpoint
                        try:
                            usage = psutil.disk_usage(drive_path)
                            total_size = usage.total / (1024 * 1024 * 1024)
                            disk_info = f"{drive_path} ({total_size:.1f} GB)"
                            
                            if self.check_key_file(drive_path):
                                self.ui.comboBox_2.addItem(disk_info, drive_path)
                                logging.info(f"Valid disk found: {disk_info}")
                            else:
                                logging.warning(f"Invalid key file: {disk_info}")
                        except Exception as e:
                            logging.error(f"Could not get disk info: {drive_path} - {str(e)}")
                            continue
                except Exception as e:
                    continue
                    
        except Exception as e:
            logging.error(f"Disk scanning error: {str(e)}")

            try:
                for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    drive = f"{letter}:\\"
                    try:
                        if os.path.exists(drive):
                            usage = psutil.disk_usage(drive)
                            if usage.total < 64 * 1024 * 1024 * 1024:  # 64GB'dan küçük diskleri çıkarılabilir kabul et
                                total_size = usage.total / (1024 * 1024 * 1024)
                                disk_info = f"{drive} ({total_size:.1f} GB)"
                                
                                if self.check_key_file(drive):
                                    self.ui.comboBox_2.addItem(disk_info, drive)
                                    logging.info(f"Valid disk found: {disk_info}")
                                else:
                                    logging.warning(f"Invalid key file: {disk_info}")
                    except:
                        continue
            except Exception as e:
                logging.error(f"Alternative disk scanning error: {str(e)}")

    def delete_key_file(self):
        try:
            current_index = self.ui.comboBox_2.currentIndex()
            if current_index == -1:
                logging.warning("No disk selected")
                return

            mount_point = self.ui.comboBox_2.currentData()
            key_path = os.path.join(mount_point, '.key')

            if os.path.exists(key_path):
                os.remove(key_path)
                logging.info(f"Key file deleted: {key_path}")
            else:
                logging.warning("Key file not found")

            self.list_removable_drives()

        except Exception as e:
            logging.error(f"Error deleting key file: {str(e)}")

    def refresh_drives(self):
        try:
            logging.info("Disk scan started")
            self.list_removable_drives()
            logging.info("Disk scan completed")
        except Exception as e:
            logging.error(f"Disk refresh error: {str(e)}")

    def set_initial_states(self):
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.listView.setEnabled(False)
        
        self.ui.checkBox_4.setChecked(False)
        
        logging.info("Initial states set")

    def toggle_folder_controls(self, state):
        try:
            is_enabled = state == 2  
            
            self.ui.pushButton.setEnabled(is_enabled)
            self.ui.listView.setEnabled(is_enabled)
            
            if is_enabled:
                has_selection = len(self.ui.listView.selectedIndexes()) > 0
                self.ui.pushButton_2.setEnabled(has_selection)
                self.ui.pushButton_3.setEnabled(has_selection)
            else:
                self.ui.pushButton_2.setEnabled(False)
                self.ui.pushButton_3.setEnabled(False)
            
            status = "enabled" if is_enabled else "disabled"
            logging.info(f"Folder editing controls {status}")
            
        except Exception as e:
            logging.error(f"Error while changing folder editing controls: {str(e)}")

    def add_default_folders(self):
        try:
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            documents = os.path.join(os.path.expanduser('~'), 'Documents')
            
            default_paths = [desktop, documents]
            
            valid_paths = [path for path in default_paths if os.path.exists(path)]
            
            self.list_model.setStringList(valid_paths)
            
            logging.info("Default folders added")
            
        except Exception as e:
            logging.error(f"Error adding folder: {str(e)}")

    def on_selection_changed(self, selected, deselected):
        try:
            has_selection = len(self.ui.listView.selectedIndexes()) > 0
            if self.ui.checkBox_4.isChecked():  # Klasörleri düzenle işaretli ise
                self.ui.pushButton_2.setEnabled(has_selection)
                self.ui.pushButton_3.setEnabled(has_selection)
                
                if has_selection:
                    selected_index = self.ui.listView.selectedIndexes()[0]
                    current_text = self.list_model.data(selected_index, QtCore.Qt.DisplayRole)
                    if current_text.endswith('*'):
                        self.ui.pushButton_3.setText("Ignore")
                    else:
                        self.ui.pushButton_3.setText("Ignore")
            
            if has_selection:
                logging.info("Item selected from list")
            else:
                logging.info("List selection removed")
                
        except Exception as e:
            logging.error(f"Error in selection control: {str(e)}")

    def delete_selected_item(self):
        try:
            selected_indexes = self.ui.listView.selectedIndexes()
            if not selected_indexes:
                return
                
            selected_index = selected_indexes[0]
            selected_item = self.list_model.data(selected_index, QtCore.Qt.DisplayRole)
            
            self.list_model.removeRow(selected_index.row())
            
            logging.info(f"Item deleted from list: {selected_item}")

        except Exception as e:
            logging.error(f"Error while deleting item: {str(e)}")

    def ignore_selected_item(self):
        try:
            selected_indexes = self.ui.listView.selectedIndexes()
            if not selected_indexes:
                return
                
            selected_index = selected_indexes[0]
            current_text = self.list_model.data(selected_index, QtCore.Qt.DisplayRole)
            
            if current_text.endswith('*'):
                new_text = current_text[:-1]  
                self.ui.pushButton_3.setText("Ignore")
            else:
                new_text = f"{current_text}*"
                self.ui.pushButton_3.setText("Ignore")
            
            self.list_model.setData(selected_index, new_text)
            
            action = "ignore removed" if current_text.endswith('*') else "ignored"
            logging.info(f"Item {action}: {current_text}")
            
        except Exception as e:
            logging.error(f"Error in ignore item operation: {str(e)}")

    def add_folder(self):
        try:
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Folder Select",
                os.path.expanduser('~'),  
                QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks
            )
            
            if folder_path:
                current_items = []
                for i in range(self.list_model.rowCount()):
                    item = self.list_model.data(self.list_model.index(i, 0), QtCore.Qt.DisplayRole)
                    current_items.append(item)
                
                if folder_path not in current_items:
                    current_items.append(folder_path)
                    self.list_model.setStringList(current_items)
                    logging.info(f"New folder added: {folder_path}")
                else:
                    logging.warning(f"Folder already exists in list: {folder_path}")
            else:
                logging.info("Folder selection cancelled")
                
        except Exception as e:
            logging.error(f"Error adding folder: {str(e)}")

    def toggle_password_controls(self, state):
        try:
            is_enabled = state == 2  
            
            self.ui.lineEdit.setEnabled(is_enabled)
            self.ui.pushButton_7.setEnabled(is_enabled)
            
            status = "enabled" if is_enabled else "disabled"
            logging.info(f"Password controls {status}")
            
        except Exception as e:
            logging.error(f"Error while changing password controls: {str(e)}")

    def disable_all_controls(self):
        self.ui.comboBox_2.setEnabled(False)
        
        self.ui.checkBox.setEnabled(False)
        self.ui.checkBox_2.setEnabled(False)
        self.ui.checkBox_4.setEnabled(False)
        
        self.ui.lineEdit.setEnabled(False)
        self.ui.lineEdit_2.setEnabled(False)
        
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False)
        self.ui.pushButton_7.setEnabled(False)
        self.ui.pushButton_8.setEnabled(False)
        
        self.ui.pushButton_11.setText("Stop Backup")
        
        self.ui.listView.setEnabled(False)

    def enable_all_controls(self):
        self.ui.comboBox_2.setEnabled(True)
        
        self.ui.checkBox.setEnabled(True)
        self.ui.checkBox_2.setEnabled(True)
        self.ui.checkBox_4.setEnabled(True)
        
        self.ui.lineEdit.setEnabled(self.ui.checkBox.isChecked())  
        self.ui.lineEdit_2.setEnabled(True)
        
        self.ui.pushButton_5.setEnabled(True)
        self.ui.pushButton_6.setEnabled(True)
        self.ui.pushButton_7.setEnabled(self.ui.checkBox.isChecked())  
        self.ui.pushButton_8.setEnabled(True)
        self.ui.pushButton_11.setEnabled(True)
        
        self.toggle_folder_controls(2 if self.ui.checkBox_4.isChecked() else 0)

    def update_backup_duration(self):
        if self.backup_start_time:
            elapsed = datetime.now() - self.backup_start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.ui.label_6.setText(f"Duration: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def on_encrypt_changed(self, state):
        try:
            is_checked = state == 2  
            
            if is_checked:
                self.ui.checkBox_2.setChecked(True)
            
            self.toggle_password_controls(state)
            
            logging.info(f"Encryption {'enabled' if is_checked else 'disabled'}")
            
        except Exception as e:
            logging.error(f"Error while changing encryption status: {str(e)}")

    def on_compress_changed(self, state):
        try:
            is_checked = state == 2  
            
            if not is_checked and self.ui.checkBox.isChecked():
                self.ui.checkBox.setChecked(False)
            
            logging.info(f"Compression {'enabled' if is_checked else 'disabled'}")
            
        except Exception as e:
            logging.error(f"Error while changing compression status: {str(e)}")

    def toggle_backup(self):
        if not self.is_backup_running:
            self.start_backup()
        else:
            self.stop_backup()

    def start_backup(self):
        try:
            current_disk_index = self.ui.comboBox_2.currentIndex()
            if current_disk_index == -1:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Warning",
                    "Please select a disk!"
                )
                return

            is_compress = self.ui.checkBox_2.isChecked()
            is_encrypt = self.ui.checkBox.isChecked()
            
            if is_encrypt:
                password = self.ui.lineEdit.text()
                if not password:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Warning",
                        "Password cannot be empty when encryption is selected!"
                    )
                    return

            target_disk = self.ui.comboBox_2.currentData()
            
            backup_folder = os.path.join(target_disk, "Backup")
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            current_date = datetime.now().strftime('%d.%m.%Y')
            date_folder = os.path.join(backup_folder, current_date)
            if not os.path.exists(date_folder):
                os.makedirs(date_folder)

            pc_name = self.ui.lineEdit_2.text()
            backup_path = os.path.join(date_folder, pc_name)

            source_paths = []
            for i in range(self.list_model.rowCount()):
                path = self.list_model.data(self.list_model.index(i, 0), QtCore.Qt.DisplayRole)
                source_paths.append(path)

            self.backup_thread = BackupThread(
                source_paths=source_paths,
                backup_path=backup_path,
                compress=is_compress,
                encrypt=is_encrypt,
                password=self.ui.lineEdit.text() if is_encrypt else None
            )
            
            self.backup_thread.finished.connect(self.on_backup_finished)
            self.backup_thread.error.connect(self.on_backup_error)
            self.backup_thread.progress.connect(self.on_backup_progress)
            
            self.backup_thread.start()
            
            self.disable_all_controls()
            
            self.is_backup_running = True
            self.ui.pushButton_11.setText("Stop Backup")
            
            self.backup_start_time = datetime.now()
            self.ui.label_5.setText(f"Start Time: {self.backup_start_time.strftime('%H:%M:%S')}")
            
            self.backup_timer.start(1000)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error starting backup: {str(e)}"
            )

    def stop_backup(self):
        try:
            if self.backup_thread and self.backup_thread.isRunning():
                reply = QtWidgets.QMessageBox.question(
                    self,
                    'Stop Backup',
                    'Backup process will be stopped. Are you sure?',
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                
                if reply == QtWidgets.QMessageBox.Yes:
                    self.backup_thread.stop()
                    self.is_backup_running = False
                    self.ui.pushButton_11.setText("Backup")
                    self.enable_all_controls()
                    self.backup_timer.stop()
                    logging.info("Backup stopped by user")
        except Exception as e:
            logging.error(f"Error while stopping backup: {str(e)}")

    def on_backup_finished(self, total_copied, total_skipped):
        self.backup_timer.stop()
        self.backup_start_time = None
        self.update_backup_duration()
        self.enable_all_controls()
        self.ui.pushButton_11.setText("Backup")
        self.is_backup_running = False
        logging.info(f"Backup completed. Copied: {total_copied}, Skipped: {total_skipped}")

    def on_backup_error(self, error_message):
        self.backup_timer.stop()
        self.backup_start_time = None
        self.enable_all_controls()
        self.ui.pushButton_11.setText("Backup")
        self.is_backup_running = False
        logging.error(f"Error in backup process: {error_message}")

    def on_backup_progress(self, message):
        logging.info(message)

    def save_default_password(self):
        try:
            new_password = self.ui.lineEdit.text()
            
            if not new_password:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Password Error",
                    "Empty password cannot be saved!"
                )
                return
            
            config = {
                'default_password': new_password
            }
            
            config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            config_file = os.path.join(config_dir, 'backup_config.json')
            with open(config_file, 'w', encoding='utf-8') as f:
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
            logging.error(f"Error saving password: {str(e)}")

    def load_default_password(self):
        try:
            config_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                'config', 
                'backup_config.json'
            )
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_password = config.get('default_password', '112.st!?')
            else:
                default_password = '112.st!?'  # Varsayılan şifre
            
            self.ui.lineEdit.setText(default_password)
            logging.info("Default password loaded")
            
        except Exception as e:
            logging.error(f"Error loading default password: {str(e)}")
            self.ui.lineEdit.setText('123456')

    def reset_to_defaults(self):
        """Reset the list view to default folders (Desktop and Documents)"""
        try:
            # Get default paths
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            documents = os.path.join(os.path.expanduser('~'), 'Documents')
            
            default_paths = [path for path in [desktop, documents] if os.path.exists(path)]
            
            # Clear current list and add default paths
            self.list_model.setStringList(default_paths)
            
            logging.info("List view reset to default folders")
            
        except Exception as e:
            logging.error(f"Error resetting to defaults: {str(e)}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Error resetting to default folders: {str(e)}"
            )

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 