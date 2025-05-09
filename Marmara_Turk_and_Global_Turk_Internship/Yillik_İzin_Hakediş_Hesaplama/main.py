import tkinter as tk
from tkinter import ttk
import math
import sqlite3
from datetime import datetime
from tkinter import messagebox
import pandas as pd

class IzinHesaplayici:
    def __init__(self):
        self.pencere = tk.Tk()
        self.pencere.title("Yıllık İzin Hesaplayıcı")
        self.pencere.geometry("1000x700")  # Genişlik artırıldı
        self.pencere.configure(bg="#f5f5f5")

        # Veritabanı bağlantısını en başta oluştur
        try:
            self.veritabani_olustur()
        except Exception as e:
            messagebox.showerror("Hata", f"Veritabanı bağlantısı kurulamadı: {str(e)}")
            self.pencere.destroy()
            return

        # Ana container frame
        self.container_frame = ttk.Frame(self.pencere)
        self.container_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # Sol panel (mevcut form)
        self.sol_panel = ttk.Frame(self.container_frame)
        self.sol_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))

        # Sağ panel (tablo için)
        self.sag_panel = ttk.Frame(self.container_frame)
        self.sag_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Style ayarları
        style = ttk.Style()
        style.configure("TFrame", background="#f5f5f5")
        style.configure("TLabel", font=("Segoe UI", 12), background="#f5f5f5")
        style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), background="#f5f5f5")
        style.configure("Input.TLabel", font=("Segoe UI", 14), background="#f5f5f5")
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=10)
        style.configure("Result.TLabel", font=("Segoe UI", 16, "bold"), background="#f5f5f5")
        
        # Treeview stil ayarları
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

        # Başlık
        self.baslik = ttk.Label(
            self.sol_panel,
            text="Yıllık İzin Hesaplama",
            style="Header.TLabel"
        )
        self.baslik.pack(pady=(0, 20))  # Üst boşluk azaltıldı

        # Giriş alanları için frame
        self.giris_frame = ttk.Frame(self.sol_panel)
        self.giris_frame.pack(fill=tk.X, pady=5)  # Padding azaltıldı

        # Çalışma süresi seçimi
        self.sure_frame = ttk.Frame(self.giris_frame)
        self.sure_frame.pack(fill=tk.X, pady=10)  # Padding azaltıldı

        self.sure_label = ttk.Label(
            self.sure_frame,
            text="Çalışma Süresini Seçin:",
            style="Input.TLabel"
        )
        self.sure_label.pack(anchor="w")

        # Radio butonlar için frame
        self.radio_frame = ttk.Frame(self.sure_frame)
        self.radio_frame.pack(fill=tk.X, pady=5)  # Padding azaltıldı

        self.sure_tipi = tk.StringVar(value="ay")
        
        self.ay_radio = ttk.Radiobutton(
            self.radio_frame,
            text="Ay Olarak",
            variable=self.sure_tipi,
            value="ay",
            command=self.sure_tipi_degisti
        )
        self.ay_radio.pack(side=tk.LEFT, padx=20)

        self.gun_radio = ttk.Radiobutton(
            self.radio_frame,
            text="Gün Olarak",
            variable=self.sure_tipi,
            value="gun",
            command=self.sure_tipi_degisti
        )
        self.gun_radio.pack(side=tk.LEFT)

        # Süre giriş alanı
        self.sure_input_frame = ttk.Frame(self.giris_frame)
        self.sure_input_frame.pack(fill=tk.X, pady=5)  # Padding azaltıldı

        self.sure_input_label = ttk.Label(
            self.sure_input_frame,
            text="Çalışılan Ay Sayısı:",
            style="Input.TLabel"
        )
        self.sure_input_label.pack(anchor="w")

        self.sure_entry = ttk.Entry(
            self.sure_input_frame,
            font=("Segoe UI", 12),
            width=20
        )
        self.sure_entry.pack(pady=5)

        # Haftalık çalışma günü
        self.haftalik_frame = ttk.Frame(self.giris_frame)
        self.haftalik_frame.pack(fill=tk.X, pady=10)  # Padding azaltıldı

        self.haftalik_label = ttk.Label(
            self.haftalik_frame,
            text="Haftalık Çalışma Günü:",
            style="Input.TLabel"
        )
        self.haftalik_label.pack(anchor="w")

        self.haftalik_entry = ttk.Entry(
            self.haftalik_frame,
            font=("Segoe UI", 12),
            width=20
        )
        self.haftalik_entry.pack(pady=5)

        # Hesapla butonu
        self.hesapla_btn = ttk.Button(
            self.sol_panel,
            text="HESAPLA",
            command=self.hesapla,
            width=25
        )
        self.hesapla_btn.pack(pady=20)  # Padding azaltıldı

        # Sonuç alanı
        self.sonuc_frame = ttk.Frame(self.sol_panel)
        self.sonuc_frame.pack(fill=tk.X, pady=10)  # Padding azaltıldı

        self.sonuc_label = ttk.Label(
            self.sonuc_frame,
            text="",
            style="Result.TLabel",
            foreground="#1976D2",
            justify="center"
        )
        self.sonuc_label.pack(fill=tk.X)

        # Personal bilgileri ve kaydet butonu yan yana
        self.personal_kaydet_frame = ttk.Frame(self.sol_panel)
        self.personal_kaydet_frame.pack(fill=tk.X, pady=10)

        self.personal_label = ttk.Label(
            self.personal_kaydet_frame,
            text="Personal:",
            style="Input.TLabel"
        )
        self.personal_label.pack(side=tk.LEFT, padx=(0, 10))

        self.personal_entry = ttk.Entry(
            self.personal_kaydet_frame,
            font=("Segoe UI", 12),
            width=20
        )
        self.personal_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.kaydet_btn = ttk.Button(
            self.personal_kaydet_frame,
            text="KAYDET",
            command=self.kaydet,
            width=15
        )
        self.kaydet_btn.pack(side=tk.LEFT)

        # Hesaplama detayları tablosu - Yukarı taşındı
        self.hesap_frame = ttk.Frame(self.sol_panel)
        self.hesap_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.hesap_baslik = ttk.Label(
            self.hesap_frame,
            text="Hesaplama Detayları",
            style="Header.TLabel"
        )
        self.hesap_baslik.pack(pady=(0, 10))

        self.tablo = ttk.Treeview(self.hesap_frame, columns=("Adım", "Değer"), show="headings", height=8)
        self.tablo.heading("Adım", text="İşlem Adımı")
        self.tablo.heading("Değer", text="Sonuç")
        self.tablo.column("Adım", width=200, anchor="w")
        self.tablo.column("Değer", width=100, anchor="center")
        self.tablo.pack(fill=tk.BOTH, expand=True)

        # Sağ panel düzeni güncellendi
        self.sag_panel.configure(padding=(20, 0, 0, 0))  # Sol padding eklendi

        # Kayıtlar tablosu - Tam yükseklik kullanacak şekilde güncellendi
        self.kayit_frame = ttk.Frame(self.sag_panel)
        self.kayit_frame.pack(fill=tk.BOTH, expand=True)

        self.kayit_baslik = ttk.Label(
            self.kayit_frame,
            text="Kayıtlı Personel İzinleri",
            style="Header.TLabel"
        )
        self.kayit_baslik.pack(pady=(0, 10))

        # Kayıt tablosunun yüksekliği artırıldı
        self.kayit_tablo = ttk.Treeview(
            self.kayit_frame, 
            columns=("Personal", "Çalışma Süresi", "Haftalık Gün", "Toplam Hafta", 
                    "Kalan Hafta", "Çalışılan Gün", "İzin Hakkı"), 
            show="headings", 
            height=15
        )
        self.kayit_tablo.heading("Personal", text="Personal")
        self.kayit_tablo.heading("Çalışma Süresi", text="Çalışma Süresi")
        self.kayit_tablo.heading("Haftalık Gün", text="Haftalık Gün")
        self.kayit_tablo.heading("Toplam Hafta", text="Toplam Hafta")
        self.kayit_tablo.heading("Kalan Hafta", text="Kalan Hafta")
        self.kayit_tablo.heading("Çalışılan Gün", text="Çalışılan Gün")
        self.kayit_tablo.heading("İzin Hakkı", text="İzin Hakkı")

        # Sütun genişliklerini ayarla
        self.kayit_tablo.column("Personal", width=150, anchor="w")
        self.kayit_tablo.column("Çalışma Süresi", width=120, anchor="center")
        self.kayit_tablo.column("Haftalık Gün", width=100, anchor="center")
        self.kayit_tablo.column("Toplam Hafta", width=100, anchor="center")
        self.kayit_tablo.column("Kalan Hafta", width=100, anchor="center")
        self.kayit_tablo.column("Çalışılan Gün", width=120, anchor="center")
        self.kayit_tablo.column("İzin Hakkı", width=100, anchor="center")
        
        self.kayit_tablo.pack(fill=tk.BOTH, expand=True)

        # Kayıt tablosuna seçim olayı ekle
        self.kayit_tablo.bind('<<TreeviewSelect>>', self.secim_degisti)

        # Arama çerçevesi
        self.arama_frame = ttk.Frame(self.sag_panel)
        self.arama_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.arama_label = ttk.Label(
            self.arama_frame,
            text="Personel Ara:",
            style="Input.TLabel"
        )
        self.arama_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.arama_entry = ttk.Entry(
            self.arama_frame,
            font=("Segoe UI", 12),
            width=20
        )
        self.arama_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Arama olayını bağla
        self.arama_entry.bind('<KeyRelease>', self.personel_ara)
        
        # Silme butonu - Başlangıçta disabled
        self.sil_btn = ttk.Button(
            self.arama_frame,
            text="Seçili Kaydı Sil",
            command=self.kayit_sil,
            width=15,
            state='disabled'  # Başlangıçta disabled
        )
        self.sil_btn.pack(side=tk.RIGHT)
        
        # Excel indirme butonu
        self.excel_btn = ttk.Button(
            self.arama_frame,  # sag_panel yerine arama_frame'e taşındı
            text="Excel Olarak İndir",
            command=self.excel_indir,
            width=20
        )
        self.excel_btn.pack(side=tk.RIGHT, padx=10)
        
        # En son kayıtları yükle
        try:
            self.kayitlari_yukle()
        except Exception as e:
            messagebox.showerror("Hata", f"Kayıtlar yüklenirken hata oluştu: {str(e)}")

    def sure_tipi_degisti(self):
        if self.sure_tipi.get() == "ay":
            self.sure_input_label.configure(text="Çalışılan Ay Sayısı:")
        else:
            self.sure_input_label.configure(text="Çalışılan Gün Sayısı:")

    def hesapla(self):
        try:
            # Tabloyu temizle
            for item in self.tablo.get_children():
                self.tablo.delete(item)

            sure = float(self.sure_entry.get())
            haftalik_gun = float(self.haftalik_entry.get())

            if haftalik_gun > 7:
                self.sonuc_label.configure(
                    text="Haftalık çalışma günü 7'den fazla olamaz!",
                    foreground="#D32F2F"
                )
                return

            # Tablo verilerini hazırla
            if self.sure_tipi.get() == "ay":
                toplam_gun = sure * 30
                self.tablo.insert("", "end", values=("Girilen Ay Sayısı", f"{sure} ay"))
                self.tablo.insert("", "end", values=("Gün Çevrimi (Ay x 30)", f"{toplam_gun} gün"))
                toplam_hafta = math.floor(toplam_gun / 7)
            else:
                toplam_gun = sure
                self.tablo.insert("", "end", values=("Girilen Gün Sayısı", f"{sure} gün"))
                toplam_hafta = math.floor(sure / 7)
            
            self.tablo.insert("", "end", values=("Toplam Hafta Sayısı", f"{toplam_hafta} hafta"))
            
            kalan_hafta = 52 - toplam_hafta
            self.tablo.insert("", "end", values=("Kalan Hafta (52 - Toplam Hafta)", f"{kalan_hafta} hafta"))
            
            haftalik_calisma = kalan_hafta * haftalik_gun
            self.tablo.insert("", "end", values=(f"Kalan Haftalık Çalışma ({kalan_hafta} x {haftalik_gun})", f"{haftalik_calisma} gün"))
            
            calisan_gun = haftalik_calisma + (sure if self.sure_tipi.get() == "gun" else (sure * 30))
            self.tablo.insert("", "end", values=("Toplam Çalışılan Gün", f"{calisan_gun} gün"))
            
            bolum = calisan_gun / 52
            self.tablo.insert("", "end", values=("52 Haftaya Bölüm", f"{bolum:.2f}"))
            
            yuvarlanmis = math.ceil(bolum)
            self.tablo.insert("", "end", values=("Yukarı Yuvarlama", f"{yuvarlanmis}"))
            
            izin_hakki = yuvarlanmis * 2
            self.tablo.insert("", "end", values=("İzin Hakkı (x2)", f"{izin_hakki} gün"))
            
            self.sonuc_label.configure(
                text=f"Yıllık İzin Hakediş Günü: {izin_hakki}",
                foreground="#1976D2"
            )
        except ValueError:
            self.sonuc_label.configure(
                text="Lütfen geçerli sayılar giriniz!",
                foreground="#D32F2F"
            )

    def kaydet(self):
        try:
            # Önce hesaplama yapılıp yapılmadığını kontrol et
            if not self.tablo.get_children():
                return  # Hesaplama yapılmamışsa sessizce çık
                
            personal = self.personal_entry.get().strip()
            if not personal:
                self.sonuc_label.configure(
                    text="Lütfen personal bilgisi giriniz!",
                    foreground="#D32F2F"
                )
                return

            # Hesaplama değerlerini al
            hesap_degerler = {}
            for item in self.tablo.get_children():
                adim, deger = self.tablo.item(item)["values"]
                hesap_degerler[adim] = deger

            # Çalışma süresini al
            if self.sure_tipi.get() == "ay":
                calisma_suresi = f"{self.sure_entry.get()} ay"
            else:
                calisma_suresi = f"{self.sure_entry.get()} gün"

            # Sayısal değerleri tam sayıya çevir
            toplam_hafta = hesap_degerler.get("Toplam Hafta Sayısı", "")
            toplam_hafta = f"{int(float(toplam_hafta.split()[0]))} hafta"
            
            kalan_hafta = hesap_degerler.get("Kalan Hafta (52 - Toplam Hafta)", "")
            kalan_hafta = f"{int(float(kalan_hafta.split()[0]))} hafta"
            
            calisan_gun = hesap_degerler.get("Toplam Çalışılan Gün", "")
            calisan_gun = f"{int(float(calisan_gun.split()[0]))} gün"
            
            izin_hakki = hesap_degerler.get("İzin Hakkı (x2)", "")
            izin_hakki = f"{int(float(izin_hakki.split()[0]))} gün"

            # Veritabanına kaydet
            self.cursor.execute("""
                INSERT INTO izin_kayitlari (
                    personal, calisma_suresi, haftalik_gun, toplam_hafta,
                    kalan_hafta, calisan_gun, izin_hakki
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                personal,
                calisma_suresi,
                f"{self.haftalik_entry.get()} gün",
                toplam_hafta,
                kalan_hafta,
                calisan_gun,
                izin_hakki
            ))
            
            self.conn.commit()
            
            # Kayıt tablosuna ekle
            self.kayit_tablo.insert("", "end", values=(
                personal,
                calisma_suresi,
                f"{self.haftalik_entry.get()} gün",
                toplam_hafta,
                kalan_hafta,
                calisan_gun,
                izin_hakki
            ))
            
            self.personal_entry.delete(0, tk.END)
            
            self.sonuc_label.configure(
                text="Kayıt başarıyla eklendi!",
                foreground="#2E7D32"
            )
        except Exception as e:
            messagebox.showerror("Hata", "Kayıt eklenirken hata oluştu!")

    def excel_indir(self):
        try:
            # Pandas ve openpyxl kontrolü
            try:
                import openpyxl
            except ImportError as e:
                messagebox.showerror(
                    "Kütüphane Hatası",
                    "Gerekli kütüphaneler bulunamadı!\n\n"
                    "Lütfen terminal veya komut isteminde şu komutları çalıştırın:\n"
                    "pip install openpyxl"
                )
                return

            # Veri kontrolü
            if not self.kayit_tablo.get_children():
                messagebox.showwarning(
                    "Uyarı",
                    "Dışa aktarılacak kayıt bulunamadı!"
                )
                return

            # Veriyi hazırla
            data = []
            try:
                for item in self.kayit_tablo.get_children():
                    values = self.kayit_tablo.item(item)["values"]
                    # Sütunları doğru şekilde al
                    data.append([
                        values[0],  # Personal
                        values[1],  # Çalışma Süresi
                        values[2],  # Haftalık Gün
                        values[3],  # Toplam Hafta
                        values[4],  # Kalan Hafta
                        values[5],  # Çalışılan Gün
                        values[6]   # İzin Hakkı
                    ])
            except Exception as e:
                messagebox.showerror(
                    "Veri Hatası",
                    f"Veriler hazırlanırken hata oluştu:\n{str(e)}"
                )
                return

            # DataFrame oluştur
            try:
                columns = [
                    "Personal",
                    "Çalışma Süresi",
                    "Haftalık Gün",
                    "Toplam Hafta",
                    "Kalan Hafta",
                    "Çalışılan Gün",
                    "İzin Hakkı"
                ]
                df = pd.DataFrame(data, columns=columns)
                
                # DataFrame'i kontrol et
                print("DataFrame Sütunları:", df.columns)
                print("DataFrame Şekli:", df.shape)
                
            except Exception as e:
                messagebox.showerror(
                    "DataFrame Hatası",
                    f"DataFrame oluşturulurken hata oluştu:\n{str(e)}\n"
                    f"Veri boyutu: {len(data)} satır"
                )
                return

            # Dosya yolu oluştur
            try:
                from datetime import datetime
                from os.path import expanduser, join
                desktop = expanduser("~/Desktop")
                tarih_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                dosya_adi = join(desktop, f"Personal_Izin_Kayitlari_{tarih_str}.xlsx")
            except Exception as e:
                messagebox.showerror(
                    "Dosya Yolu Hatası",
                    f"Dosya yolu oluşturulurken hata oluştu:\n{str(e)}"
                )
                return

            # Excel'e kaydet
            try:
                df.to_excel(dosya_adi, index=False, engine='openpyxl')
                messagebox.showinfo(
                    "Başarılı",
                    f"Excel dosyası başarıyla oluşturuldu!\n\n"
                    f"Dosya Konumu: {dosya_adi}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Kaydetme Hatası",
                    f"Excel dosyası kaydedilirken hata oluştu:\n{str(e)}"
                )
                return

        except Exception as e:
            messagebox.showerror(
                "Beklenmeyen Hata",
                f"Beklenmeyen bir hata oluştu:\n{str(e)}"
            )

    def veritabani_olustur(self):
        self.conn = sqlite3.connect('personel_izin.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS izin_kayitlari (
                id INTEGER PRIMARY KEY,
                personal TEXT,
                calisma_suresi TEXT,
                haftalik_gun TEXT,
                toplam_hafta TEXT,
                kalan_hafta TEXT,
                calisan_gun TEXT,
                izin_hakki TEXT
            )
        ''')
        self.conn.commit()

    def kayitlari_yukle(self):
        try:
            # Mevcut kayıtları temizle
            for item in self.kayit_tablo.get_children():
                self.kayit_tablo.delete(item)
            
            # Veritabanından kayıtları al
            self.cursor.execute("SELECT * FROM izin_kayitlari")
            kayitlar = self.cursor.fetchall()
            
            # Kayıtları tabloya ekle
            for kayit in kayitlar:
                self.kayit_tablo.insert("", "end", values=kayit[1:])  # id hariç tüm değerler
        except Exception as e:
            messagebox.showerror("Hata", "Kayıtlar yüklenirken hata oluştu!")

    def personel_ara(self, event):
        arama_terimi = self.arama_entry.get().lower()
        
        try:
            # Mevcut kayıtları temizle
            for item in self.kayit_tablo.get_children():
                self.kayit_tablo.delete(item)
            
            # Veritabanında arama yap
            self.cursor.execute("""
                SELECT * FROM izin_kayitlari 
                WHERE LOWER(personal) LIKE ?
            """, (f'%{arama_terimi}%',))
            
            kayitlar = self.cursor.fetchall()
            
            # Bulunan kayıtları tabloya ekle
            for kayit in kayitlar:
                self.kayit_tablo.insert("", "end", values=kayit[1:])
        except Exception as e:
            messagebox.showerror("Hata", "Arama yapılırken hata oluştu!")

    def secim_degisti(self, event):
        # Seçili öğe varsa butonu aktif et, yoksa pasif
        if self.kayit_tablo.selection():
            self.sil_btn.configure(state='normal')
        else:
            self.sil_btn.configure(state='disabled')

    def kayit_sil(self):
        try:
            secili = self.kayit_tablo.selection()
            if not secili:
                return
            
            kayit_values = self.kayit_tablo.item(secili)['values']
            
            # Veritabanından sil (tarih olmadan)
            self.cursor.execute("""
                DELETE FROM izin_kayitlari 
                WHERE personal = ? AND calisan_gun = ?
            """, (kayit_values[0], kayit_values[5]))
            
            self.conn.commit()
            self.kayit_tablo.delete(secili)
            self.sil_btn.configure(state='disabled')
            
            self.sonuc_label.configure(
                text="Kayıt başarıyla silindi!",
                foreground="#2E7D32"
            )
        except Exception as e:
            messagebox.showerror("Hata", "Kayıt silinirken hata oluştu!")

    def baslat(self):
        try:
            self.pencere.mainloop()
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()

if __name__ == "__main__":
    uygulama = IzinHesaplayici()
    uygulama.baslat() 