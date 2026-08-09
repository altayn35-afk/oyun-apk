import array
import math
import os
import random
import threading
import time
import tkinter as tk

# Ses ve Müzik için Pygame
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.set_num_channels(8)
    PYGAME_MEVCUT = True
except ImportError:
    PYGAME_MEVCUT = False

# Görsel işleme için Pillow
try:
    from PIL import Image, ImageTk
    PIL_MEVCUT = True
except ImportError:
    PIL_MEVCUT = False

# Doğal Türkçe Ses Motoru (Google TTS)
try:
    from gtts import gTTS
    GTTS_MEVCUT = True
except ImportError:
    GTTS_MEVCUT = False


# Global Ses Durumu
SES_ACIK = True


# ==========================================
# YAZILIMSAL SES EFEKTİ VE SESLENDİRME
# ==========================================
def tin_sesi_uret():
    if not PYGAME_MEVCUT:
        return None
    try:
        sample_rate = 44100
        duration = 0.12
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * (n_samples * 2))
        freq = 880.0
        for i in range(n_samples):
            t = float(i) / sample_rate
            envelope = math.exp(-t * 20)
            val = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * freq * t) * envelope)
            buf[i * 2] = val
            buf[i * 2 + 1] = val
        return pygame.mixer.Sound(buffer=buf)
    except Exception as e:
        print(f"Tin sesi hatası: {e}")
        return None


def aaa_sesi_uret():
    if not PYGAME_MEVCUT:
        return None
    try:
        sample_rate = 44100
        duration = 0.25
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * (n_samples * 2))
        for i in range(n_samples):
            t = float(i) / sample_rate
            freq = 350.0 - (130.0 * (t / duration))
            envelope = math.sin(math.pi * (t / duration))
            val = int(32767.0 * 0.25 * math.sin(2.0 * math.pi * freq * t) * envelope)
            buf[i * 2] = val
            buf[i * 2 + 1] = val
        return pygame.mixer.Sound(buffer=buf)
    except Exception as e:
        print(f"Aaa sesi hatası: {e}")
        return None


def tik_sesi_uret():
    if not PYGAME_MEVCUT:
        return None
    try:
        sample_rate = 44100
        duration = 0.04
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * (n_samples * 2))
        freq = 1200.0
        for i in range(n_samples):
            t = float(i) / sample_rate
            envelope = math.exp(-t * 50)
            val = int(32767.0 * 0.2 * math.sin(2.0 * math.pi * freq * t) * envelope)
            buf[i * 2] = val
            buf[i * 2 + 1] = val
        return pygame.mixer.Sound(buffer=buf)
    except Exception as e:
        print(f"Tik sesi hatası: {e}")
        return None


def alkis_sesi_uret():
    if not PYGAME_MEVCUT:
        return None
    try:
        sample_rate = 44100
        duration = 0.6
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * (n_samples * 2))
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = int(32767.0 * 0.2 * (random.random() * 2 - 1) * math.sin(math.pi * (t / duration)))
            buf[i * 2] = val
            buf[i * 2 + 1] = val
        return pygame.mixer.Sound(buffer=buf)
    except Exception as e:
        print(f"Alkış sesi hatası: {e}")
        return None


TIN_SESI = tin_sesi_uret() if PYGAME_MEVCUT else None
AAA_SESI = aaa_sesi_uret() if PYGAME_MEVCUT else None
TIK_SESI = tik_sesi_uret() if PYGAME_MEVCUT else None
ALKIS_SESI = alkis_sesi_uret() if PYGAME_MEVCUT else None


def muziK_ses_seviyesi_ayarla(seviye):
    """Müzik Ses Seviyesini Değiştiren Yardımcı Fonksiyon (0.2 -> %20, 0.5 -> %50)"""
    if PYGAME_MEVCUT and pygame.mixer.music.get_busy() and SES_ACIK:
        try:
            pygame.mixer.music.set_volume(seviye)
        except Exception as e:
            print(f"Müzik ses seviyesi ayarlama hatası: {e}")


def metni_turkce_seslendir(metin, bitince_bunu_yap=None):
    if not SES_ACIK:
        if bitince_bunu_yap:
            bitince_bunu_yap()
        return

    def seslendir():
        dosya_adi = f"gecici_ses_{random.randint(1000, 9999)}.mp3"
        try:
            if GTTS_MEVCUT and PYGAME_MEVCUT:
                tts = gTTS(text=metin, lang='tr', slow=False)
                tts.save(dosya_adi)
                
                if SES_ACIK:
                    ses_obj = pygame.mixer.Sound(dosya_adi)
                    okuma_suresi = ses_obj.get_length()
                    pygame.mixer.Channel(6).play(ses_obj)
                    time.sleep(okuma_suresi)

                try:
                    os.remove(dosya_adi)
                except:
                    pass
        except Exception as e:
            print(f"Türkçe seslendirme hatası: {e}")
        
        if bitince_bunu_yap and SES_ACIK:
            bitince_bunu_yap()

    threading.Thread(target=seslendir, daemon=True).start()


def ses_efekti_cal(ses_tipi):
    if not PYGAME_MEVCUT or not SES_ACIK:
        return

    try:
        if ses_tipi == "sarki":
            if os.path.exists("fon_muzigi.mp3"):
                pygame.mixer.music.load("fon_muzigi.mp3")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            else:
                for dosya in os.listdir("."):
                    if dosya.endswith(".mp3") and not dosya.startswith("gecici_ses_"):
                        pygame.mixer.music.load(dosya)
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                        break
        elif ses_tipi == "tin":
            if TIN_SESI:
                pygame.mixer.Channel(2).play(TIN_SESI)
        elif ses_tipi == "uzuntu":
            if AAA_SESI:
                pygame.mixer.Channel(3).play(AAA_SESI)
        elif ses_tipi == "tik":
            if TIK_SESI:
                pygame.mixer.Channel(4).play(TIK_SESI)
        elif ses_tipi == "alkis":
            if ALKIS_SESI:
                pygame.mixer.Channel(5).play(ALKIS_SESI)
    except Exception as e:
        print(f"Ses hatası: {e}")


def akilli_gorsel_bul(aranan_anahtar):
    klasor_dosyalari = os.listdir(".")
    for dosya in klasor_dosyalari:
        isim_suz = os.path.splitext(dosya)[0].lower()
        if aranan_anahtar.lower() == isim_suz:
            return dosya
    for dosya in klasor_dosyalari:
        if aranan_anahtar.lower() in dosya.lower():
            return dosya
    return None


class MinikKasiflerAtolyesi:
    def __init__(self, root):
        self.root = root
        self.root.title("Minik Kaşifler Atölyesi")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.cocuk_ismi = "Minik Kaşif"
        self.puan = 0
        self.seviye = 1
        self.mevcut_oyun_kodu = "genel"
        
        # CAN & REKLAM DEĞİŞKENLERİ
        self.canlar = 3
        self.max_can = 3
        self.can_yenilenme_suresi = 180  # 3 Dakika
        self.kalan_can_suresi = self.can_yenilenme_suresi
        self.son_can_zaman = time.time()
        
        self.balon_hizi = 2.5
        self.balon_aktif = False
        self.ari_oyunu_aktif = False
        self.sekil_oyunu_aktif = False
        self.bulmaca_oyunu_aktif = False
        
        self.bulmaca_kule_toplam_blok = 0
        self.balon_renkleri = ["#FF4D4D", "#4D94FF", "#4DFF88", "#FFD633", "#B366FF", "#FF9933"]

        # Geçici ses temizliği
        for f in os.listdir("."):
            if f.startswith("gecici_ses_"):
                try:
                    os.remove(f)
                except:
                    pass

        ses_efekti_cal("sarki")
        self.can_zamanlayicisi_dongusu()
        self.giris_ekrani_olustur()

    def can_zamanlayicisi_dongusu(self):
        """Arka planda 3 dakikada 1 can dolduran sayaç"""
        if self.canlar < self.max_can:
            su_an = time.time()
            gecen_sure = su_an - self.son_can_zaman
            self.kalan_can_suresi = max(0, int(self.can_yenilenme_suresi - gecen_sure))
            
            if gecen_sure >= self.can_yenilenme_suresi:
                self.canlar += 1
                self.son_can_zaman = time.time()
                self.kalan_can_suresi = self.can_yenilenme_suresi
        else:
            self.son_can_zaman = time.time()
            self.kalan_can_suresi = self.can_yenilenme_suresi

        self.root.after(1000, self.can_zamanlayicisi_dongusu)

    def can_azalt(self, canvas, yeniden_baslat_fonksiyonu):
        """Canı 1 azaltır. Can 0 olursa oyuna özel pop-up gösterir."""
        self.canlar -= 1
        ses_efekti_cal("uzuntu")
        
        if self.canlar <= 0:
            self.canlar = 0
            self.oyun_bitti_reklam_ekrani_goster(canvas)
        else:
            if yeniden_baslat_fonksiyonu:
                self.root.after(1000, yeniden_baslat_fonksiyonu)

    def reklam_izle_can_al(self, callback_fonksiyonu=None):
        """1 Reklam İzlemeye +1 Can Verme Mekanizması"""
        if self.canlar < self.max_can:
            self.canlar += 1
        ses_efekti_cal("alkis")
        metni_turkce_seslendir("Harika! 1 Can Kazandın!")
        
        if callback_fonksiyonu:
            callback_fonksiyonu()
        else:
            self.menu_ekrani_olustur()

    def oyun_bitti_reklam_ekrani_goster(self, canvas):
        """Her oyuna özel eğlenceli çocuk pop-up ekranı"""
        self.balon_aktif = False
        self.ari_oyunu_aktif = False
        self.sekil_oyunu_aktif = False
        self.bulmaca_oyunu_aktif = False

        canvas.create_rectangle(50, 50, 750, 550, fill="#1F1135", outline="#FF4500", width=4)
        canvas.create_text(400, 100, text="💔 CANLARIN BİTTİ! 💔", font=("Impact", 28, "bold"), fill="#FF4D4D")
        
        # Oyuna özel slogan ve ikon ayarı
        if self.mevcut_oyun_kodu == "balon":
            ikon_emoji = "🎈 💥"
            alt_metin = "Eyvah, Balonlar Gökyüzüne Kaçtı!"
            buton_metni = "🎬 SİHİRLİ İĞNE KAZANMAK İÇİN VİDEO İZLE (+1 CAN)"
        elif self.mevcut_oyun_kodu == "ari":
            ikon_emoji = "😴 💫"
            alt_metin = "Sevimli Arı Yorgun Düştü ve Bayıldı!"
            buton_metni = "🎬 ARIYI KURTARMAK İÇİN VİDEO İZLE (+1 CAN)"
        elif self.mevcut_oyun_kodu == "sekil":
            ikon_emoji = "🔍 ❓"
            alt_metin = "Tüm İpuçları Saklandı!"
            buton_metni = "🎬 SÜPER BÜYÜTECİ AÇMAK İÇİN VİDEO İZLE (+1 CAN)"
        elif self.mevcut_oyun_kodu == "bulmaca":
            ikon_emoji = "🏰 🧩"
            alt_metin = "Sihirli Kule Blokları Bitti!"
            buton_metni = "🎬 KULEYİ BÜYÜTMEYE DEVAM İÇİN VİDEO İZLE (+1 CAN)"
        else:
            ikon_emoji = "⭐ 🚀"
            alt_metin = "Macera Yarıda Kaldı!"
            buton_metni = "🎬 VİDEO İZLE (+1 CAN KAZAN)"

        # İkon ve Metin
        canvas.create_text(400, 170, text=ikon_emoji, font=("Arial", 32))
        canvas.create_text(400, 230, text=alt_metin, font=("Arial", 14, "bold"), fill="#FFD166")
        
        dakika = self.kalan_can_suresi // 60
        saniye = self.kalan_can_suresi % 60
        sure_metni = f"{dakika:02d}:{saniye:02d}"
        
        canvas.create_text(400, 270, text=f"Yeni Can İçin Otomatik Süre: {sure_metni}", 
                           font=("Arial", 12), fill="#FFFFFF")

        # Oyuna Özel Reklam Butonu
        btn_reklam = tk.Button(self.root, text=buton_metni, font=("Arial", 10, "bold"),
                               bg="#2ECC71", fg="white", activebackground="#27AE60", activeforeground="white",
                               cursor="hand2", command=lambda: self.reklam_izle_can_al())
        canvas.create_window(400, 340, window=btn_reklam, width=420, height=48)

        # Menüye Dön Butonu
        btn_menu = tk.Button(self.root, text="🏠 Menüye Dön", font=("Arial", 11, "bold"),
                             bg="#E74C3C", fg="white", command=self.menu_ekrani_olustur)
        canvas.create_window(400, 410, window=btn_menu, width=200, height=40)

    def can_ve_ses_paneli_ekle(self, target_canvas):
        """Kayıp canlarda Kırmızı Çarpı (❌) gösteren Can Paneli"""
        metin = "🔊 Ses Açık" if SES_ACIK else "🔇 Ses Kapalı"
        renk = "#2ECC71" if SES_ACIK else "#E74C3C"
        btn_ses = tk.Button(self.root, text=metin, font=("Arial", 10, "bold"), bg=renk, fg="white",
                            activebackground=renk, activeforeground="white", command=self.genel_ses_degistir)
        target_canvas.create_window(720, 30, window=btn_ses, tags="ses_butonu")

        # Canları Kalp (❤️) ve Kayıpları Çarpı (❌) Olarak Göster
        kalpler = "❤️ " * self.canlar + "❌ " * (self.max_can - self.canlar)
        target_canvas.create_rectangle(290, 10, 490, 50, fill="#FFFFFF", outline="#FF4D4D", width=2, tags="can_paneli")
        target_canvas.create_text(390, 30, text=f"Can: {kalpler.strip()}", font=("Arial", 12, "bold"), fill="#D32F2F", tags="can_paneli")

    def genel_ses_degistir(self):
        global SES_ACIK
        SES_ACIK = not SES_ACIK
        if not SES_ACIK and PYGAME_MEVCUT:
            pygame.mixer.music.pause()
            pygame.mixer.stop()
        elif SES_ACIK and PYGAME_MEVCUT:
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy():
                ses_efekti_cal("sarki")
        
        if hasattr(self, "mevcut_ekran_yenile"):
            self.mevcut_ekran_yenile()

    def ekrani_temizle(self):
        self.balon_aktif = False
        self.ari_oyunu_aktif = False
        self.sekil_oyunu_aktif = False
        self.bulmaca_oyunu_aktif = False
        for widget in self.root.winfo_children():
            widget.destroy()

    def gorsel_yukle(self, aranan_anahtar, genislik=800, yukseklik=600):
        dosya_yolu = akilli_gorsel_bul(aranan_anahtar)
        if PIL_MEVCUT and dosya_yolu:
            try:
                img = Image.open(dosya_yolu).convert("RGBA")
                img = img.resize((genislik, yukseklik), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Görsel yükleme hatası ({dosya_yolu}): {e}")
        return None

    def ciz_vektorel_oyun_arkaplan(self, canvas):
        canvas.create_rectangle(0, 0, 800, 600, fill="#70D6FF", outline="")
        canvas.create_oval(650, -30, 830, 150, fill="#FFD166", outline="#FFE6A7", width=6)
        
        def bulut_ciz(x, y, olcek=1.0):
            r = int(25 * olcek)
            canvas.create_oval(x-r, y-r, x+r, y+r, fill="#FFFFFF", outline="")
            canvas.create_oval(x+r*0.8, y-r*1.2, x+r*2.2, y+r*0.5, fill="#FFFFFF", outline="")
            canvas.create_oval(x+r*1.8, y-r*0.5, x+r*3.2, y+r, fill="#FFFFFF", outline="")
            canvas.create_rectangle(x-r, y, x+r*3.2, y+r, fill="#FFFFFF", outline="")

        bulut_ciz(60, 90, 1.2)
        bulut_ciz(350, 70, 0.9)
        bulut_ciz(550, 130, 1.1)

        canvas.create_oval(-100, 380, 500, 750, fill="#95D5B2", outline="")
        canvas.create_oval(300, 420, 900, 750, fill="#74C69D", outline="")
        canvas.create_oval(-50, 460, 450, 800, fill="#52B788", outline="")
        canvas.create_oval(250, 450, 850, 800, fill="#40916C", outline="")
        canvas.create_rectangle(0, 560, 800, 600, fill="#2D6A4F", outline="")

    def ciz_vektorel_giris_arkaplan(self, canvas):
        canvas.create_rectangle(0, 0, 800, 600, fill="#2B1E3A", outline="")
        random.seed(42)
        for _ in range(40):
            sx = random.randint(20, 780)
            sy = random.randint(20, 580)
            sr = random.randint(2, 5)
            canvas.create_oval(sx-sr, sy-sr, sx+sr, sy+sr, fill="#FFD166", outline="")
        random.seed()

        canvas.create_oval(680, 420, 850, 590, fill="#4D94FF", outline="")
        canvas.create_oval(30, 450, 150, 570, fill="#FF9933", outline="")

    # ==========================================
    # EKRAN 1: GİRİŞ EKRANI (MÜZİK %50)
    # ==========================================
    def giris_ekrani_olustur(self):
        self.ekrani_temizle()
        self.mevcut_ekran_yenile = self.giris_ekrani_olustur
        self.mevcut_oyun_kodu = "giris"
        
        # Ana menüde müzik %50 seviyesine çıkar
        muziK_ses_seviyesi_ayarla(0.5)

        canvas = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        self.giris_bg = self.gorsel_yukle("oyun_arkaplan1") or self.gorsel_yukle("giris_arkaplan")
        if self.giris_bg:
            canvas.create_image(0, 0, image=self.giris_bg, anchor="nw")
        else:
            self.ciz_vektorel_giris_arkaplan(canvas)

        self.can_ve_ses_paneli_ekle(canvas)

        canvas.create_text(400, 80, text="✨ MİNİK KAŞİFLER ATÖLYESİ ✨", font=("Impact", 32, "bold"), fill="#FFD700")
        canvas.create_text(400, 130, text="Eğlenceli Öğrenme Dünyasına Hoş Geldin!", font=("Arial", 16, "bold"), fill="#00FFFF")

        canvas.create_rectangle(220, 380, 580, 540, fill="#1F1135", outline="#FFD700", width=3)
        canvas.create_text(400, 415, text="Adın Nedir Minik Kaşif?", font=("Arial", 16, "bold"), fill="#FFFFFF")

        txt_isim = tk.Entry(self.root, font=("Arial", 16), justify="center", bd=2, relief="groove")
        canvas.create_window(400, 455, window=txt_isim, width=260, height=38)
        txt_isim.focus()

        def oyuna_basla():
            girilen_isim = txt_isim.get().strip()
            if girilen_isim:
                self.cocuk_ismi = girilen_isim
            self.menu_ekrani_olustur()

        btn_basla = tk.Button(self.root, text="MACERAYA BAŞLA 🚀", font=("Arial", 13, "bold"),
                              bg="#FF4500", fg="white", activebackground="#FF6347",
                              activeforeground="white", bd=2, cursor="hand2", command=oyuna_basla)
        canvas.create_window(400, 505, window=btn_basla, width=220, height=40)

    # ==========================================
    # EKRAN 2: OYUN SEÇİM MENÜSÜ (MÜZİK %50)
    # ==========================================
    def menu_ekrani_olustur(self):
        self.ekrani_temizle()
        self.mevcut_ekran_yenile = self.menu_ekrani_olustur
        self.mevcut_oyun_kodu = "menu"

        # Menüde müzik %50 seviyesine çıkar
        muziK_ses_seviyesi_ayarla(0.5)

        canvas = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        self.menu_bg = self.gorsel_yukle("oyun_arkaplan") or self.gorsel_yukle("menu_arkaplan")
        if self.menu_bg:
            canvas.create_image(0, 0, image=self.menu_bg, anchor="nw")
        else:
            self.ciz_vektorel_oyun_arkaplan(canvas)

        self.can_ve_ses_paneli_ekle(canvas)

        canvas.create_rectangle(180, 75, 620, 135, fill="#FFFFFF", outline="#FF8C00", width=3)
        canvas.create_text(400, 105, text=f"Sevgili {self.cocuk_ismi}, Oyununu Seç!",
                           font=("Arial", 18, "bold"), fill="#2E8B57")

        oyunlar = [
            ("🎈 Balon Patlatma Macerası", "#FF4500", self.balon_oyunu_kontrol),
            ("🐝 Bal Peşinde Neşeli Arı", "#FFB300", self.ari_oyunu_kontrol),
            ("🔍 Şekil ve Renk Avcısı", "#2E8B57", self.sekil_oyunu_kontrol),
            ("🧩 Sürpriz Bulmaca Kulesi", "#D35400", self.bulmaca_oyunu_kontrol)
        ]

        y_pos = 195
        for baslik, renk, komut in oyunlar:
            btn = tk.Button(self.root, text=baslik, font=("Arial", 14, "bold"), bg=renk, fg="white",
                            activebackground="#333333", activeforeground="white", bd=3, cursor="hand2", command=komut)
            canvas.create_window(400, y_pos, window=btn, width=400, height=52)
            y_pos += 72

        btn_geri = tk.Button(self.root, text="👤 İsim Değiştir", font=("Arial", 10, "bold"),
                             bg="#2980B9", fg="white", command=self.giris_ekrani_olustur)
        canvas.create_window(90, 30, window=btn_geri)

    def can_kontrol_ve_baslat(self, oyun_baslat_fn, oyun_kodu):
        self.mevcut_oyun_kodu = oyun_kodu
        if self.canlar > 0:
            oyun_baslat_fn()
        else:
            self.oyun_bitti_reklam_ekrani_goster(self.root.winfo_children()[0])

    def balon_oyunu_kontrol(self): self.can_kontrol_ve_baslat(self.balon_oyunu_baslat, "balon")
    def ari_oyunu_kontrol(self): self.can_kontrol_ve_baslat(self.ari_oyunu_baslat, "ari")
    def sekil_oyunu_kontrol(self): self.can_kontrol_ve_baslat(self.sekil_oyunu_baslat, "sekil")
    def bulmaca_oyunu_kontrol(self): self.can_kontrol_ve_baslat(self.bulmaca_oyunu_baslat, "bulmaca")

    # ==========================================
    # OYUN 1: BALON PATLATMA (MÜZİK %20)
    # ==========================================
    def balon_oyunu_baslat(self):
        self.ekrani_temizle()
        self.mevcut_ekran_yenile = self.balon_oyunu_baslat
        self.mevcut_oyun_kodu = "balon"
        self.balon_aktif = True
        self.puan = 0
        self.seviye = 1
        self.balon_hizi = 2.5

        # Oyun içine girildiğinde fon müziği %20'ye düşer
        muziK_ses_seviyesi_ayarla(0.2)

        self.oyun_tuvali = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        self.oyun_tuvali.pack(fill="both", expand=True)

        self.oyun_bg = self.gorsel_yukle("oyun_arkaplan") or self.gorsel_yukle("menu_arkaplan")
        if self.oyun_bg:
            self.oyun_tuvali.create_image(0, 0, image=self.oyun_bg, anchor="nw")
        else:
            self.ciz_vektorel_oyun_arkaplan(self.oyun_tuvali)

        self.can_ve_ses_paneli_ekle(self.oyun_tuvali)

        btn_geri = tk.Button(self.root, text="⬅ Menüye Dön", font=("Arial", 11, "bold"), bg="#E74C3C", fg="white", command=self.menu_ekrani_olustur)
        self.oyun_tuvali.create_window(80, 30, window=btn_geri)

        self.lbl_skor = tk.Label(self.root, text=f"Puan: {self.puan}  |  Seviye: {self.seviye}",
                                 font=("Arial", 12, "bold"), fg="#1B5E20", bg="#C8E6C9", padx=8, pady=2, bd=2, relief="ridge")
        self.oyun_tuvali.create_window(580, 30, window=self.lbl_skor)

        self.yeni_balon_olustur()
        self.balon_ucur_dongusu()

    def yeni_balon_olustur(self):
        self.balon_x = random.randint(100, 700)
        self.balon_y = 580
        self.balon_aci = 0
        self.balon_renk = random.choice(self.balon_renkleri)

    def balon_ucur_dongusu(self):
        if not self.balon_aktif or not self.oyun_tuvali.winfo_exists():
            return

        self.oyun_tuvali.delete("oyun_nesnesi")

        mevcut_hiz = self.balon_hizi + (self.seviye * 1.0)
        self.balon_y -= mevcut_hiz

        self.balon_aci += 0.08
        self.balon_x += math.sin(self.balon_aci) * 3
        self.balon_x = max(50, min(750, self.balon_x))

        r = 38
        self.oyun_tuvali.create_oval(self.balon_x-r, self.balon_y-r, self.balon_x+r, self.balon_y+r,
                                     fill=self.balon_renk, outline="white", width=2, tags="oyun_nesnesi")
        self.oyun_tuvali.create_oval(self.balon_x-r*0.5, self.balon_y-r*0.6, self.balon_x-r*0.1, self.balon_y-r*0.2,
                                     fill="#FFFFFF", outline="", tags="oyun_nesnesi")
        self.oyun_tuvali.create_polygon(self.balon_x-6, self.balon_y+r, self.balon_x+6, self.balon_y+r, self.balon_x, self.balon_y+r+10,
                                     fill=self.balon_renk, outline="", tags="oyun_nesnesi")
        self.oyun_tuvali.create_line(self.balon_x, self.balon_y+r+10, self.balon_x, self.balon_y+r+35,
                                     fill="#444444", width=2, tags="oyun_nesnesi")

        self.oyun_tuvali.tag_bind("oyun_nesnesi", "<Button-1>", lambda event: self.balon_patlatildi())

        if self.balon_y < -40:
            self.yeni_balon_olustur()
            self.can_azalt(self.oyun_tuvali, None)
            self.can_ve_ses_paneli_ekle(self.oyun_tuvali)

        if self.canlar > 0:
            self.root.after(30, self.balon_ucur_dongusu)

    def balon_patlatildi(self):
        self.puan += 10
        ses_efekti_cal("tin")
        self.seviye = (self.puan // 30) + 1
        self.lbl_skor.configure(text=f"Puan: {self.puan}  |  Seviye: {self.seviye}")
        self.yeni_balon_olustur()

    # ==========================================
    # OYUN 2: BAL PEŞİNDE NEŞELİ ARI (MÜZİK %20)
    # ==========================================
    def ari_oyunu_baslat(self):
        self.ekrani_temizle()
        self.mevcut_ekran_yenile = self.ari_oyunu_baslat
        self.mevcut_oyun_kodu = "ari"
        self.ari_oyunu_aktif = True
        self.ari_puan = 0
        self.ari_seviye = 1
        self.kalan_mesafe = 1000

        # Oyun içine girildiğinde fon müziği %20'ye düşer
        muziK_ses_seviyesi_ayarla(0.2)

        self.ari_x = 120
        self.ari_y = 300
        self.kanat_aci = 0
        self.engeller = []
        self.bal_kutusu = None
        self.ari_dondumu = False

        self.oyun_tuvali = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        self.oyun_tuvali.pack(fill="both", expand=True)

        self.ari_bg = self.gorsel_yukle("oyun_arkaplan") or self.gorsel_yukle("menu_arkaplan")
        self.oyun_tuvali.bind("<Motion>", self.ari_fare_hareket)

        btn_geri = tk.Button(self.root, text="⬅ Menüye Dön", font=("Arial", 11, "bold"), bg="#E74C3C", fg="white", command=self.menu_ekrani_olustur)
        self.oyun_tuvali.create_window(80, 30, window=btn_geri)

        self.ari_dongusu()

    def ari_fare_hareket(self, event):
        if self.ari_oyunu_aktif and not self.ari_dondumu:
            self.ari_y = max(50, min(550, event.y))

    def ciz_3d_ari(self, x, y, sersem=False):
        self.kanat_aci += 0.5
        kanat_ofset = math.sin(self.kanat_aci) * 8 if not sersem else 2
        
        self.oyun_tuvali.create_oval(x-15, y-30+kanat_ofset, x+5, y-8, fill="#E0F7FA", outline="#80DEEA", width=2)
        self.oyun_tuvali.create_oval(x, y-30-kanat_ofset, x+20, y-8, fill="#E0F7FA", outline="#80DEEA", width=2)
        self.oyun_tuvali.create_oval(x-30, y-20, x+25, y+20, fill="#FFC107", outline="#FF8F00", width=2)
        self.oyun_tuvali.create_rectangle(x-12, y-19, x-3, y+19, fill="#3E2723", outline="")
        self.oyun_tuvali.create_rectangle(x+5, y-18, x+14, y+18, fill="#3E2723", outline="")
        
        if sersem:
            self.oyun_tuvali.create_text(x+15, y-10, text="💫 😵", font=("Arial", 16))
        else:
            self.oyun_tuvali.create_oval(x+10, y-12, x+22, y, fill="white", outline="#3E2723")
            self.oyun_tuvali.create_oval(x+16, y-9, x+20, y-4, fill="black", outline="")
            
        self.oyun_tuvali.create_line(x+20, y+3, x+25, y+7, fill="#3E2723", width=2)
        self.oyun_tuvali.create_polygon(x-30, y-5, x-38, y, x-30, y+5, fill="#3E2723", outline="")

    def ari_bas_donup_dusme_animasyonu(self, adim=0):
        if adim < 15:
            self.ari_y += 12
            self.ari_x -= 3
            self.oyun_tuvali.delete("all")
            
            if self.ari_bg:
                self.oyun_tuvali.create_image(0, 0, image=self.ari_bg, anchor="nw")
            else:
                self.ciz_vektorel_oyun_arkaplan(self.oyun_tuvali)

            self.can_ve_ses_paneli_ekle(self.oyun_tuvali)
            self.ciz_3d_ari(self.ari_x, self.ari_y, sersem=True)
            self.root.after(40, lambda: self.ari_bas_donup_dusme_animasyonu(adim + 1))
        else:
            self.can_azalt(self.oyun_tuvali, self.ari_oyunu_baslat)

    def ciz_3d_bal_kovani(self, x, y):
        self.oyun_tuvali.create_oval(x-40, y+10, x+40, y+40, fill="#FFA000", outline="#E65100", width=3)
        self.oyun_tuvali.create_oval(x-35, y-15, x+35, y+15, fill="#FFB300", outline="#E65100", width=3)
        self.oyun_tuvali.create_oval(x-28, y-38, x+28, y-8, fill="#FFC107", outline="#E65100", width=3)
        self.oyun_tuvali.create_oval(x-18, y-52, x+18, y-30, fill="#FFCA28", outline="#E65100", width=3)
        self.oyun_tuvali.create_oval(x-10, y, x+10, y+18, fill="#3E2723", outline="#FFA000")
        self.oyun_tuvali.create_oval(x-4, y+15, x+4, y+28, fill="#FFD54F", outline="")

    def ari_dongusu(self):
        if not self.ari_oyunu_aktif or not self.oyun_tuvali.winfo_exists() or self.ari_dondumu:
            return

        self.oyun_tuvali.delete("all")

        if self.ari_bg:
            self.oyun_tuvali.create_image(0, 0, image=self.ari_bg, anchor="nw")
        else:
            self.ciz_vektorel_oyun_arkaplan(self.oyun_tuvali)

        self.can_ve_ses_paneli_ekle(self.oyun_tuvali)

        btn_geri = tk.Button(self.root, text="⬅ Menüye Dön", font=("Arial", 11, "bold"), bg="#E74C3C", fg="white", command=self.menu_ekrani_olustur)
        self.oyun_tuvali.create_window(80, 30, window=btn_geri)

        hiz = 4 + (self.ari_seviye * 1.5)
        self.kalan_mesafe -= 1

        self.ciz_3d_ari(self.ari_x, self.ari_y)

        if self.kalan_mesafe > 100 and random.random() < (0.02 + self.ari_seviye * 0.008):
            eng_y = random.randint(80, 520)
            eng_h = random.randint(60, 110)
            self.engeller.append([850, eng_y, eng_h])

        yeni_engeller = []
        for eng in self.engeller:
            eng[0] -= hiz
            ex, ey, eh = eng[0], eng[1], eng[2]
            
            self.oyun_tuvali.create_rectangle(ex-15, ey-eh//2, ex+15, ey+eh//2, fill="#795548", outline="#3E2723", width=2)
            self.oyun_tuvali.create_oval(ex-30, ey-eh//2-15, ex+30, ey-eh//2+15, fill="#388E3C", outline="")

            if abs(self.ari_x - ex) < 35 and abs(self.ari_y - ey) < (eh // 2 + 20):
                self.ari_dondumu = True
                ses_efekti_cal("uzuntu")
                self.ari_bas_donup_dusme_animasyonu()
                return

            if ex > -50:
                yeni_engeller.append(eng)

        self.engeller = yeni_engeller

        if self.kalan_mesafe <= 0:
            if self.bal_kutusu is None:
                self.bal_kutusu = 850
            self.bal_kutusu -= hiz

            self.ciz_3d_bal_kovani(self.bal_kutusu, 300)

            if abs(self.ari_x - self.bal_kutusu) < 45 and abs(self.ari_y - 300) < 60:
                ses_efekti_cal("tin")
                self.ari_seviye += 1
                self.ari_puan += 50
                self.kalan_mesafe = 1000 + (self.ari_seviye * 200)
                self.bal_kutusu = None

        self.oyun_tuvali.create_rectangle(520, 10, 640, 50, fill="#FFF8E1", outline="#FFA000", width=2)
        self.oyun_tuvali.create_text(580, 30, text=f"Puan: {self.ari_puan} | Sev: {self.ari_seviye}",
                                     font=("Arial", 9, "bold"), fill="#5D4037")

        if self.canlar > 0:
            self.root.after(30, self.ari_dongusu)

    # ==========================================
    # OYUN 3: ŞEKİL VE RENK AVCISI (MÜZİK %20)
    # ==========================================
    def sekil_oyunu_baslat(self):
        self.ekrani_temizle()
        self.mevcut_ekran_yenile = self.sekil_oyunu_baslat
        self.mevcut_oyun_kodu = "sekil"
        self.sekil_oyunu_aktif = True
        self.sekil_seviye = 1
        self.sekil_puan = 0
        self.konfeti_parcaciklari = []

        # Oyun içine girildiğinde fon müziği %20'ye düşer
        muziK_ses_seviyesi_ayarla(0.2)

        self.sekil_seviye_yukle()

    def sekil_seviye_yukle(self):
        self.sekil_oyunu_aktif = True
        self.zamanlayici_calisiyor = False
        self.kalan_sure = max(8, 21 - self.sekil_seviye)
        self.bulunan_sayisi = 0
        self.konfeti_parcaciklari = []

        self.renk_sozlugu = {
            "Kırmızı": "#FF3333", "Yeşil": "#2ECC71", "Mavi": "#3498DB",
            "Turuncu": "#E67E22", "Mor": "#9B59B6", "Sarı": "#F1C40F"
        }
        self.sekil_tipleri = ["Yuvarlak", "Kare", "Üçgen", "Yıldız"]

        self.hedef_renk_adi = random.choice(list(self.renk_sozlugu.keys()))
        self.hedef_renk_kod = self.renk_sozlugu[self.hedef_renk_adi]
        self.hedef_sekil = random.choice(self.sekil_tipleri)
        self.hedef_sayi = random.randint(3, 5)

        self.ekran_nesneleri = []
        for _ in range(self.hedef_sayi):
            self.ekran_nesneleri.append({
                "renk_adi": self.hedef_renk_adi, "renk_kod": self.hedef_renk_kod,
                "sekil": self.hedef_sekil, "hedef_mi": True, "bulundu": False
            })

        celdirici_sayisi = random.randint(10, 14) + self.sekil_seviye
        for _ in range(celdirici_sayisi):
            r_ad = random.choice(list(self.renk_sozlugu.keys()))
            s_tip = random.choice(self.sekil_tipleri)
            if r_ad == self.hedef_renk_adi and s_tip == self.hedef_sekil:
                s_tip = "Kare" if self.hedef_sekil != "Kare" else "Yuvarlak"

            self.ekran_nesneleri.append({
                "renk_adi": r_ad, "renk_kod": self.renk_sozlugu[r_ad],
                "sekil": s_tip, "hedef_mi": False, "bulundu": False
            })

        random.shuffle(self.ekran_nesneleri)

        grid_positions = []
        for x in range(120, 700, 90):
            for y in range(160, 500, 85):
                grid_positions.append((x + random.randint(-10, 10), y + random.randint(-10, 10)))
        
        random.shuffle(grid_positions)
        for i, nesne in enumerate(self.ekran_nesneleri):
            if i < len(grid_positions):
                nesne["x"], nesne["y"] = grid_positions[i]
            else:
                nesne["x"] = random.randint(100, 700)
                nesne["y"] = random.randint(150, 500)

        if hasattr(self, "sekil_tuvali"):
            self.sekil_tuvali.destroy()

        self.sekil_tuvali = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        self.sekil_tuvali.pack(fill="both", expand=True)

        self.sekil_bg = self.gorsel_yukle("oyun_arkaplan") or self.gorsel_yukle("menu_arkaplan")

        self.sekil_ekran_ciz()
        soru_okuma = f"{self.hedef_sayi} tane {self.hedef_renk_adi} {self.hedef_sekil} bul!"
        metni_turkce_seslendir(soru_okuma, bitince_bunu_yap=self.sekil_zaman_sayacini_baslat)

    def sekil_zaman_sayacini_baslat(self):
        self.zamanlayici_calisiyor = True
        self.sekil_zaman_sayaci()

    def tek_sekil_ciz(self, x, y, sekil_tipi, renk_kod, etiket, bulundu=False):
        r = 30
        if bulundu:
            self.sekil_tuvali.create_oval(x-r-8, y-r-8, x+r+8, y+r+8, fill="#2ECC71", outline="#FFFFFF", width=3, tags=etiket)

        if sekil_tipi == "Yuvarlak":
            self.sekil_tuvali.create_oval(x-r, y-r, x+r, y+r, fill=renk_kod, outline="#FFFFFF", width=3, tags=etiket)
        elif sekil_tipi == "Kare":
            self.sekil_tuvali.create_rectangle(x-r, y-r, x+r, y+r, fill=renk_kod, outline="#FFFFFF", width=3, tags=etiket)
        elif sekil_tipi == "Üçgen":
            self.sekil_tuvali.create_polygon(x, y-r-4, x-r-4, y+r, x+r+4, y+r, fill=renk_kod, outline="#FFFFFF", width=3, tags=etiket)
        elif sekil_tipi == "Yıldız":
            points = []
            for i in range(10):
                angle = i * math.pi / 5 - math.pi / 2
                radius = r + 4 if i % 2 == 0 else r // 2
                points.append(x + radius * math.cos(angle))
                points.append(y + radius * math.sin(angle))
            self.sekil_tuvali.create_polygon(points, fill=renk_kod, outline="#FFFFFF", width=2, tags=etiket)

    def sekil_ekran_ciz(self):
        self.sekil_tuvali.delete("all")

        if self.sekil_bg:
            self.sekil_tuvali.create_image(0, 0, image=self.sekil_bg, anchor="nw")
        else:
            self.ciz_vektorel_oyun_arkaplan(self.sekil_tuvali)

        self.can_ve_ses_paneli_ekle(self.sekil_tuvali)

        self.sekil_tuvali.create_rectangle(160, 15, 640, 85, fill="#1F1135", outline="#FFD700", width=3)
        soru_metni = f"Aşağıdaki {self.hedef_sayi} tane {self.hedef_renk_adi} {self.hedef_sekil}'i Bul!"
        self.sekil_tuvali.create_text(400, 50, text=soru_metni, font=("Arial", 16, "bold"), fill="#00FFFF")

        self.sekil_tuvali.create_rectangle(640, 95, 780, 160, fill="#FFF8E1", outline="#FFA000", width=3)
        self.sekil_tuvali.create_text(710, 110, text=f"Seviye: {self.sekil_seviye}", font=("Arial", 10, "bold"), fill="#5D4037")
        self.sekil_tuvali.create_text(710, 128, text=f"Süre: {self.kalan_sure} sn", font=("Arial", 11, "bold"), fill="#D32F2F" if self.kalan_sure <= 5 else "#2E8B57")
        self.sekil_tuvali.create_text(710, 146, text=f"Puan: {self.sekil_puan}", font=("Arial", 10, "bold"), fill="#1976D2")

        btn_geri = tk.Button(self.root, text="⬅ Menüye Dön", font=("Arial", 11, "bold"), bg="#E74C3C", fg="white", command=self.menu_ekrani_olustur)
        self.sekil_tuvali.create_window(80, 30, window=btn_geri, tags="ust_buton")

        for idx, nesne in enumerate(self.ekran_nesneleri):
            tag_id = f"nesne_{idx}"
            self.tek_sekil_ciz(nesne["x"], nesne["y"], nesne["sekil"], nesne["renk_kod"], tag_id, nesne["bulundu"])
            self.sekil_tuvali.tag_bind(tag_id, "<Button-1>", lambda event, n=nesne: self.sekil_tiklandi(n))

        for p in self.konfeti_parcaciklari:
            self.sekil_tuvali.create_oval(p["x"]-p["r"], p["y"]-p["r"], p["x"]+p["r"], p["y"]+p["r"], fill=p["c"], outline="")

    def sekil_tiklandi(self, nesne):
        if not self.sekil_oyunu_aktif or nesne["bulundu"]:
            return

        if nesne["hedef_mi"]:
            nesne["bulundu"] = True
            self.bulunan_sayisi += 1
            self.sekil_puan += 10
            ses_efekti_cal("tin")

            if self.bulunan_sayisi >= self.hedef_sayi:
                self.sekil_kazandi_durumu()
            else:
                self.sekil_ekran_ciz()
        else:
            self.can_azalt(self.sekil_tuvali, None)
            self.sekil_ekran_ciz()

    def sekil_kazandi_durumu(self):
        self.sekil_oyunu_aktif = False
        self.zamanlayici_calisiyor = False
        ses_efekti_cal("alkis")
        metni_turkce_seslendir(f"Tebrikler {self.cocuk_ismi}!")
        
        for _ in range(70):
            self.konfeti_parcaciklari.append({
                "x": random.randint(50, 750), "y": random.randint(50, 550),
                "r": random.randint(4, 9), "c": random.choice(self.balon_renkleri)
            })

        self.sekil_ekran_ciz()
        self.sekil_tuvali.create_rectangle(180, 240, 620, 360, fill="#2ECC71", outline="#FFFFFF", width=4)
        self.sekil_tuvali.create_text(400, 285, text=f"🎉 TEBRİKLER {self.cocuk_ismi.upper()}! 🎉", font=("Arial", 18, "bold"), fill="#FFFFFF")
        self.sekil_tuvali.create_text(400, 325, text=f"Seviye {self.sekil_seviye + 1}'e Geçiliyor...", font=("Arial", 14, "bold"), fill="#FFF8E1")

        self.sekil_seviye += 1
        self.root.after(2000, self.sekil_seviye_yukle)

    def sekil_zaman_sayaci(self):
        if not self.sekil_oyunu_aktif or not getattr(self, "zamanlayici_calisiyor", False) or not self.sekil_tuvali.winfo_exists():
            return

        if self.kalan_sure > 0:
            self.kalan_sure -= 1
            if self.kalan_sure <= 5:
                ses_efekti_cal("tik")

            self.sekil_ekran_ciz()
            self.root.after(1000, self.sekil_zaman_sayaci)
        else:
            self.sekil_oyunu_aktif = False
            self.zamanlayici_calisiyor = False
            self.can_azalt(self.sekil_tuvali, self.sekil_seviye_yukle)

    # ==========================================
    # OYUN 4: SÜRPRİZ BULMACA KULESİ (MÜZİK %20)
    # ==========================================
    def bulmaca_oyunu_baslat(self):
        self.ekrani_temizle()
        self.mevcut_ekran_yenile = self.bulmaca_oyunu_baslat
        self.mevcut_oyun_kodu = "bulmaca"
        self.bulmaca_oyunu_aktif = True
        self.bulmaca_seviye = 1
        self.bulmaca_puan = 0
        self.bulmaca_kule_toplam_blok = 0

        # Oyun içine girildiğinde fon müziği %20'ye düşer
        muziK_ses_seviyesi_ayarla(0.2)

        self.bulmaca_seviye_yukle()

    def bulmaca_seviye_yukle(self):
        self.bulmaca_oyunu_aktif = True
        self.secilen_kartlar = []
        self.eslesen_ciftler = 0
        self.tiklama_kilitli = True
        self.konfeti_parcaciklari = []
        self.ezber_suresi = 5

        tum_semboller = ["🐶", "🐱", "🍎", "🍌", "🚗", "🚀", "🎈", "🌟", "🐼", "🐸", "🍇", "🍓"]
        
        if self.bulmaca_seviye == 1:
            self.toplam_cift = 3
            self.grid_cols = 3
        elif self.bulmaca_seviye == 2:
            self.toplam_cift = 4
            self.grid_cols = 4
        else:
            self.toplam_cift = 6
            self.grid_cols = 4

        secilen_semboller = random.sample(tum_semboller, self.toplam_cift)
        kart_listesi = secilen_semboller * 2
        random.shuffle(kart_listesi)

        self.kartlar = []
        for idx, sembol in enumerate(kart_listesi):
            self.kartlar.append({
                "id": idx, "sembol": sembol, "acik": True, "eslesdi": False
            })

        if hasattr(self, "bulmaca_tuvali"):
            self.bulmaca_tuvali.destroy()

        self.bulmaca_tuvali = tk.Canvas(self.root, width=800, height=600, highlightthickness=0)
        self.bulmaca_tuvali.pack(fill="both", expand=True)

        self.bulmaca_bg = self.gorsel_yukle("oyun_arkaplan") or self.gorsel_yukle("menu_arkaplan")
        
        self.bulmaca_ekran_ciz()
        metni_turkce_seslendir("Kartları aklında tut!")
        self.ezber_sayaci_baslat()

    def ezber_sayaci_baslat(self):
        if not self.bulmaca_oyunu_aktif:
            return

        if self.ezber_suresi > 0:
            ses_efekti_cal("tik")
            self.ezber_suresi -= 1
            self.bulmaca_ekran_ciz()
            self.root.after(1000, self.ezber_sayaci_baslat)
        else:
            for k in self.kartlar:
                k["acik"] = False
            self.tiklama_kilitli = False
            ses_efekti_cal("tin")
            self.bulmaca_ekran_ciz()

    def bulmaca_ekran_ciz(self):
        self.bulmaca_tuvali.delete("all")

        if self.bulmaca_bg:
            self.bulmaca_tuvali.create_image(0, 0, image=self.bulmaca_bg, anchor="nw")
        else:
            self.ciz_vektorel_oyun_arkaplan(self.bulmaca_tuvali)

        self.can_ve_ses_paneli_ekle(self.bulmaca_tuvali)

        self.bulmaca_tuvali.create_rectangle(160, 15, 640, 80, fill="#1F1135", outline="#FFD700", width=3)
        if self.ezber_suresi > 0 and self.tiklama_kilitli:
            durum_metni = f"🧠 Kartları İncele: {self.ezber_suresi + 1} sn!"
            metin_renk = "#FFD166"
        else:
            durum_metni = "🧩 Eşleri Bul ve Kuleyi Yükselt!"
            metin_renk = "#00FFFF"
        self.bulmaca_tuvali.create_text(400, 47, text=durum_metni, font=("Arial", 16, "bold"), fill=metin_renk)

        self.bulmaca_tuvali.create_rectangle(640, 95, 780, 160, fill="#FFF8E1", outline="#FFA000", width=3)
        self.bulmaca_tuvali.create_text(710, 115, text=f"Seviye: {self.bulmaca_seviye}", font=("Arial", 11, "bold"), fill="#5D4037")
        self.bulmaca_tuvali.create_text(710, 140, text=f"Puan: {self.bulmaca_puan}", font=("Arial", 12, "bold"), fill="#1976D2")

        btn_geri = tk.Button(self.root, text="⬅ Menüye Dön", font=("Arial", 11, "bold"), bg="#E74C3C", fg="white", command=self.menu_ekrani_olustur)
        self.bulmaca_tuvali.create_window(80, 30, window=btn_geri, tags="ust_buton")

        # KULE ÇİZİMİ
        self.bulmaca_tuvali.create_rectangle(640, 540, 760, 560, fill="#795548", outline="#3E2723", width=3)
        kule_renkleri = ["#E74C3C", "#F1C40F", "#2ECC71", "#3498DB", "#9B59B6", "#E67E22", "#1ABC9C", "#D35400"]
        blok_h = 24
        for i in range(self.bulmaca_kule_toplam_blok):
            by = 540 - ((i + 1) * blok_h)
            if by < 170:
                break
            renk = kule_renkleri[i % len(kule_renkleri)]
            self.bulmaca_tuvali.create_rectangle(650, by, 750, by + blok_h - 3, fill=renk, outline="#FFFFFF", width=2)
            self.bulmaca_tuvali.create_text(700, by + (blok_h // 2) - 1, text="🌟", font=("Arial", 10))

        # KARTLAR
        start_x = 100 if self.grid_cols == 3 else 70
        start_y = 125
        card_w, card_h = 105, 125
        gap_x, gap_y = 20, 20
        card_bg_colors = ["#FFEBEE", "#E3F2FD", "#E8F5E9", "#FFFDE7", "#F3E5F5", "#E0F7FA"]

        for idx, kart in enumerate(self.kartlar):
            col = idx % self.grid_cols
            row = idx // self.grid_cols
            x = start_x + col * (card_w + gap_x)
            y = start_y + row * (card_h + gap_y)

            tag_id = f"kart_{idx}"
            renk_bg = card_bg_colors[idx % len(card_bg_colors)]

            if kart["eslesdi"]:
                self.bulmaca_tuvali.create_rectangle(x, y, x+card_w, y+card_h, fill="#C8E6C9", outline="#2ECC71", width=3, tags=tag_id)
                self.bulmaca_tuvali.create_text(x + card_w//2, y + card_h//2, text=kart["sembol"], font=("Segoe UI Emoji", 34), tags=tag_id)
            elif kart["acik"]:
                self.bulmaca_tuvali.create_rectangle(x, y, x+card_w, y+card_h, fill=renk_bg, outline="#FFD700", width=4, tags=tag_id)
                self.bulmaca_tuvali.create_text(x + card_w//2, y + card_h//2, text=kart["sembol"], font=("Segoe UI Emoji", 34), tags=tag_id)
            else:
                self.bulmaca_tuvali.create_rectangle(x, y, x+card_w, y+card_h, fill="#3498DB", outline="#FFFFFF", width=3, tags=tag_id)
                self.bulmaca_tuvali.create_text(x + card_w//2, y + card_h//2, text="❓", font=("Arial", 28, "bold"), fill="#FFFFFF", tags=tag_id)

            self.bulmaca_tuvali.tag_bind(tag_id, "<Button-1>", lambda event, i=idx: self.kart_tiklandi(i))

        for p in self.konfeti_parcaciklari:
            self.bulmaca_tuvali.create_oval(p["x"]-p["r"], p["y"]-p["r"], p["x"]+p["r"], p["y"]+p["r"], fill=p["c"], outline="")

    def kart_tiklandi(self, idx):
        if not self.bulmaca_oyunu_aktif or self.tiklama_kilitli:
            return

        kart = self.kartlar[idx]
        if kart["acik"] or kart["eslesdi"]:
            return

        ses_efekti_cal("tik")
        kart["acik"] = True
        self.secilen_kartlar.append(kart)
        self.bulmaca_ekran_ciz()

        if len(self.secilen_kartlar) == 2:
            self.tiklama_kilitli = True
            k1, k2 = self.secilen_kartlar[0], self.secilen_kartlar[1]

            if k1["sembol"] == k2["sembol"]:
                ses_efekti_cal("tin")
                k1["eslesdi"] = True
                k2["eslesdi"] = True
                self.eslesen_ciftler += 1
                self.bulmaca_puan += 15
                self.bulmaca_kule_toplam_blok += 1
                self.secilen_kartlar = []
                self.tiklama_kilitli = False
                self.bulmaca_ekran_ciz()

                if self.eslesen_ciftler >= self.toplam_cift:
                    self.bulmaca_kazandi_durumu()
            else:
                self.root.after(600, lambda: self.kartlari_kapat(k1, k2))

    def kartlari_kapat(self, k1, k2):
        k1["acik"] = False
        k2["acik"] = False
        self.secilen_kartlar = []
        self.tiklama_kilitli = False
        self.can_azalt(self.bulmaca_tuvali, None)
        self.bulmaca_ekran_ciz()

    def bulmaca_kazandi_durumu(self):
        self.bulmaca_oyunu_aktif = False
        ses_efekti_cal("alkis")
        metni_turkce_seslendir(f"Tebrikler {self.cocuk_ismi}!")

        for _ in range(80):
            self.konfeti_parcaciklari.append({
                "x": random.randint(50, 750), "y": random.randint(50, 550),
                "r": random.randint(4, 9), "c": random.choice(self.balon_renkleri)
            })

        self.bulmaca_ekran_ciz()
        self.bulmaca_tuvali.create_rectangle(160, 230, 640, 360, fill="#2ECC71", outline="#FFFFFF", width=4)
        self.bulmaca_tuvali.create_text(400, 275, text=f"🏰 KULE BÜYÜYOR! 🏰", font=("Arial", 20, "bold"), fill="#FFFFFF")
        self.bulmaca_tuvali.create_text(400, 315, text=f"Seviye {self.bulmaca_seviye + 1}'e Geçiliyor...", font=("Arial", 14, "bold"), fill="#FFF8E1")

        self.bulmaca_seviye += 1
        self.root.after(2000, self.bulmaca_seviye_yukle)


if __name__ == "__main__":
    root = tk.Tk()
    oyun = MinikKasiflerAtolyesi(root)
    root.mainloop()