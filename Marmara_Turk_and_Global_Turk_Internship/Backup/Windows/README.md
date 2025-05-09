# Backup Application Installation Guide

## Requirements

Before installation, ensure that the following software is installed on your computer:

1. Python 3.8 or higher
   - [Download Python here](https://www.python.org/downloads/)
   - Make sure to check the "Add Python to PATH" option during installation

2. Required Python packages:
   ```bash
   pip install pyinstaller
   pip install pywin32
   ```

## Installation Steps

1. Download the files to your computer
   - `installer.py`
   - `main.py`
   - `icon_backup.ico` (optional)
   - Ensure all files are in the same folder

2. Start the installation
   - Right-click on the `installer.py` file
   - Select "Run as administrator"
   - Or open the command prompt as administrator and run the following command:
     ```bash
     python installer.py
     ```

3. Follow the installation wizard
   - Enter the default backup password
   - Set the master password for USB drives
   - Choose the option to start automatically on Windows startup

## Post-Installation

Once the installation is complete:
- The program will be installed in the `%APPDATA%\BackupApp` folder
- Shortcuts will be created on the Desktop and in the Start menu
- A `.key` file for USB drives will be saved in your Downloads folder

## Troubleshooting

1. If you receive an "Administrator rights required" error:
   - Ensure you are running the program as an administrator

2. For PyInstaller errors:
   - Ensure Python is added to PATH
   - Check that the required packages are installed correctly

3. If you encounter errors during installation:
   - Verify all files are in the same folder
   - Ensure your antivirus program is not blocking the installation
   - Try removing the old installation and attempt again

## Contact

If you encounter any issues or need assistance:
- [devrimtuncer@gmail.com]
- [Devrim Tuncer](https://www.linkedin.com/in/devrim-tun%C3%A7er-218a55320/)

## License

[MIT License](LICENSE)

---

# Backup Uygulaması Kurulum Kılavuzu

## Gereksinimler

Kurulum yapmadan önce aşağıdaki yazılımların bilgisayarınızda yüklü olduğundan emin olun:

1. Python 3.8 veya daha yüksek bir sürüm
   - [Python'u buradan indirebilirsiniz](https://www.python.org/downloads/)
   - Kurulum sırasında "Add Python to PATH" seçeneğini işaretlemeyi unutmayın

2. Gerekli Python paketleri:
   ```bash
   pip install pyinstaller
   pip install pywin32
   ```

## Kurulum Adımları

1. Dosyaları bilgisayarınıza indirin
   - `installer.py`
   - `main.py`
   - `icon_backup.ico` (isteğe bağlı)
   - Tüm dosyaların aynı klasörde olduğundan emin olun

2. Kurulumu başlatın
   - `installer.py` dosyasına sağ tıklayın
   - "Yönetici olarak çalıştır" seçeneğini seçin
   - Veya komut istemini yönetici olarak açıp şu komutu çalıştırın:
     ```bash
     python installer.py
     ```

3. Kurulum sihirbazını takip edin
   - Varsayılan yedekleme şifresini girin
   - USB sürücüler için anahtar şifresini belirleyin
   - Windows başlangıcında otomatik başlatma seçeneğini belirleyin

## Kurulum Sonrası

Kurulum tamamlandığında:
- Program `%APPDATA%\BackupApp` klasörüne kurulacak
- Masaüstünde ve Başlat menüsünde kısayollar oluşturulacak
- USB sürücüler için `.key` dosyası İndirilenler klasörünüze kaydedilecek

## Sorun Giderme

1. "Administrator rights required" hatası alırsanız:
   - Programı yönetici olarak çalıştırdığınızdan emin olun

2. PyInstaller hataları için:
   - Python'un PATH'e eklendiğinden emin olun
   - Gerekli paketlerin doğru şekilde yüklendiğini kontrol edin

3. Kurulum sırasında hata alırsanız:
   - Tüm dosyaların aynı klasörde olduğunu kontrol edin
   - Antivirüs programınızın kurulumu engellemediğinden emin olun
   - Eski kurulumu kaldırıp tekrar deneyin

## İletişim

Herhangi bir sorun yaşarsanız veya yardıma ihtiyacınız olursa:
- [devrimtuncer@gmail.com]
- [Devrim Tuncer](https://www.linkedin.com/in/devrim-tun%C3%A7er-218a55320/)

## Lisans

[MIT Lisansı](LICENSE) 