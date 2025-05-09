# Backup Application

This application is a tool developed to back up your files. It can run on both Linux and Windows operating systems.

## Features

- **Cross-Platform Support**: The application can run on both Linux and Windows.
- **User-Friendly Interface**: A graphical user interface developed with PyQt5.
- **Backup and Compression**: Offers compression and encryption options while backing up your files.
- **Removable Disk Support**: Automatically detects removable disks like USB drives.
- **Logging**: Records events that occur during backup operations.

## Libraries Used

- **PyQt5**: For creating the user interface.
- **psutil**: To obtain system information.
- **shutil**: For file and directory operations.
- **zipfile** and **pyminizip**: For compressing and encrypting files.
- **json**: To read and write configuration files.
- **logging**: To record application events.

## Installation

### Windows

1. Install Python 3.8 or higher.
2. Install the required Python packages:
   ```bash
   pip install PyQt5 psutil pyminizip
   ```
3. Run the `installer.py` file to install the application.

### Linux

1. Install Python 3.6 or higher.
2. Install the required Python packages:
   ```bash
   pip install PyQt5 psutil pyminizip
   ```
3. Run the `install.py` file to install the application.

## Usage

After starting the application, you can select the folders you want to back up and set compression and encryption options. The progress and logs are displayed during the backup process.

## Contact

If you have any questions or feedback, please contact me:
- [devrimtuncer@gmail.com]
- [Devrim Tuncer](https://www.linkedin.com/in/devrim-tun%C3%A7er-218a55320/)

## License

This project is licensed under the [MIT License](LICENSE).

---

# Backup Uygulaması

Bu uygulama, dosyalarınızı yedeklemek için geliştirilmiş bir araçtır. Hem Linux hem de Windows işletim sistemlerinde çalışabilir.

## Özellikler

- **Çoklu Platform Desteği**: Uygulama hem Linux hem de Windows üzerinde çalışabilir.
- **Kullanıcı Dostu Arayüz**: PyQt5 ile geliştirilmiş grafiksel kullanıcı arayüzü.
- **Yedekleme ve Sıkıştırma**: Dosyalarınızı yedeklerken sıkıştırma ve şifreleme seçenekleri sunar.
- **Çıkarılabilir Disk Desteği**: USB bellekler gibi çıkarılabilir diskleri otomatik olarak algılar.
- **Loglama**: Yedekleme işlemleri sırasında oluşan olayları kaydeder.

## Kullanılan Kütüphaneler

- **PyQt5**: Kullanıcı arayüzü oluşturmak için.
- **psutil**: Sistem bilgilerini almak için.
- **shutil**: Dosya ve dizin işlemleri için.
- **zipfile** ve **pyminizip**: Dosyaları sıkıştırmak ve şifrelemek için.
- **json**: Yapılandırma dosyalarını okumak ve yazmak için.
- **logging**: Uygulama olaylarını kaydetmek için.

## Kurulum

### Windows

1. Python 3.8 veya daha yüksek bir sürümü yükleyin.
2. Gerekli Python paketlerini yükleyin:
   ```bash
   pip install PyQt5 psutil pyminizip
   ```
3. `installer.py` dosyasını çalıştırarak uygulamayı kurun.

### Linux

1. Python 3.6 veya daha yüksek bir sürümü yükleyin.
2. Gerekli Python paketlerini yükleyin:
   ```bash
   pip install PyQt5 psutil pyminizip
   ```
3. `install.py` dosyasını çalıştırarak uygulamayı kurun.

## Kullanım

Uygulamayı başlattıktan sonra, yedeklemek istediğiniz klasörleri seçebilir, sıkıştırma ve şifreleme seçeneklerini ayarlayabilirsiniz. Yedekleme işlemi sırasında ilerleme durumu ve loglar görüntülenir.

## İletişim

Herhangi bir sorunuz veya geri bildiriminiz varsa, lütfen benimle iletişime geçin:
- [devrimtuncer@gmail.com]
- [Devrim Tuncer](https://www.linkedin.com/in/devrim-tun%C3%A7er-218a55320/)
## Lisans

Bu proje, [MIT License](LICENSE) lisansı altında lisanslanmıştır. 