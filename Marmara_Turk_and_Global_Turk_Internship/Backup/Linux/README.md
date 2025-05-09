# Backup Application Installation Guide (Linux)

## Requirements

Before installation, ensure the following software is installed on your computer:

1. Python 3.6 or higher
   - Python is usually pre-installed on most Linux distributions

## Installation Steps

1. Download the files to your computer
   - `install.py`
   - `main.py`
   - `backup_ui.py`
   - `icon_backup.png` (optional)
   - Ensure all files are in the same folder

2. Start the installation
   - Open the terminal and navigate to the directory where the files are located
   - Run the following command to start the installation:
     ```bash
     python3 install.py
     ```

3. Follow the installation wizard
   - Necessary files will be copied and configuration files will be created automatically

## Post-Installation

Once the installation is complete:
- The program will be installed in the `~/.local/share/backup-app` directory
- An executable file will be created in the `~/.local/bin` directory
- An entry will be created in the application menu

## Troubleshooting

1. If you receive an "Error: Required file not found" message:
   - Ensure all necessary files are in the same folder

2. If the icon does not appear in the application menu:
   - Try logging out and logging back in

3. If you encounter errors during installation:
   - Check the error messages in the terminal
   - Ensure the necessary permissions are granted

## Contact

If you encounter any issues or need assistance:
- [devrimtuncer@gmail.com]
- [Devrim Tuncer](https://www.linkedin.com/in/devrim-tun%C3%A7er-218a55320/)

## License

[MIT License](LICENSE)

---

# Backup Uygulaması Kurulum Kılavuzu (Linux)

## Gereksinimler

Kurulum yapmadan önce aşağıdaki yazılımların bilgisayarınızda yüklü olduğundan emin olun:

1. Python 3.6 veya daha yüksek bir sürüm
   - Python genellikle çoğu Linux dağıtımında önceden yüklü gelir

## Kurulum Adımları

1. Dosyaları bilgisayarınıza indirin
   - `install.py`
   - `main.py`
   - `backup_ui.py`
   - `icon_backup.png` (isteğe bağlı)
   - Tüm dosyaların aynı klasörde olduğundan emin olun

2. Kurulumu başlatın
   - Terminali açın ve dosyaların bulunduğu dizine gidin
   - Aşağıdaki komutu çalıştırarak kurulumu başlatın:
     ```bash
     python3 install.py
     ```

3. Kurulum sihirbazını takip edin
   - Gerekli dosyaların kopyalanması ve yapılandırma dosyalarının oluşturulması otomatik olarak yapılacaktır

## Kurulum Sonrası

Kurulum tamamlandığında:
- Program `~/.local/share/backup-app` klasörüne kurulacak
- `~/.local/bin` dizininde çalıştırılabilir bir dosya oluşturulacak
- Uygulama menüsünde bir giriş oluşturulacak

## Sorun Giderme

1. "Error: Required file not found" hatası alırsanız:
   - Tüm gerekli dosyaların aynı klasörde olduğundan emin olun

2. Uygulama menüsünde simge görünmüyorsa:
   - Oturumu kapatıp tekrar açmayı deneyin

3. Kurulum sırasında hata alırsanız:
   - Terminaldeki hata mesajlarını kontrol edin
   - Gerekli izinlerin verildiğinden emin olun

## İletişim

Herhangi bir sorun yaşarsanız veya yardıma ihtiyacınız olursa:
- [devrimtuncer@gmail.com]
- [Devrim Tuncer](https://www.linkedin.com/in/devrim-tun%C3%A7er-218a55320/)

## Lisans

[MIT Lisansı](LICENSE) 