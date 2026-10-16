# -*- coding: utf-8 -*-
"""
MINIK KASIFLER ATOLYESI - KIVY SURUMU (GUNCellenmis + ADMOB + YENI OZELLIKLER)
"""

import math
import os
import random
import threading
import time

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, Triangle, Line, PushMatrix, PopMatrix, Rotate
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window

try:
    from gtts import gTTS
    GTTS_MEVCUT = True
except ImportError:
    GTTS_MEVCUT = False

try:
    from kivmob import KivMob, RewardedListenerInterface
    KIVMOB_MEVCUT = True
except ImportError:
    KIVMOB_MEVCUT = False

# AdMob Kimlikleri (Gonderdiginiz guncel ID'ler)
ADMOB_APP_ID = "ca-app-pub-1540771956171830~3252252740"
ADMOB_REWARDED_ID = "ca-app-pub-1540771956171830/9097896782"

_REKLAM_YONETICISI = None
_ODUL_CALLBACK = None
_REKLAM_HATA = "Reklam sistemi henuz baslatilmadi."


def _reklam_uyarisi(mesaj):
    """Android ekraninda reklam durumunu kullaniciya bildir."""
    def goster(dt):
        icerik = Label(text=str(mesaj)[:450], halign="center", valign="middle")
        icerik.bind(size=lambda nesne, boyut: setattr(nesne, "text_size", boyut))
        Popup(title="Reklam Bilgisi", content=icerik,
              size_hint=(0.9, 0.4)).open()
    Clock.schedule_once(goster, 0)


class _OdulDinleyici(RewardedListenerInterface if KIVMOB_MEVCUT else object):
    def on_rewarded(self, reward_type, amount):
        global _ODUL_CALLBACK
        callback = _ODUL_CALLBACK
        _ODUL_CALLBACK = None
        if callback:
            Clock.schedule_once(lambda dt: callback(), 0)

    def on_rewarded_video_ad_closed(self):
        global _ODUL_CALLBACK
        _ODUL_CALLBACK = None
        Clock.schedule_once(lambda dt: reklam_yeniden_yukle(), 0)


def reklam_sistemini_baslat():
    global _REKLAM_YONETICISI, _REKLAM_HATA
    if not KIVMOB_MEVCUT:
        _REKLAM_HATA = "kivmob kutuphanesi yuklenemedi. Android reklam entegrasyonunu kontrol etmeliyiz."
        print(_REKLAM_HATA)
        return
    try:
        _REKLAM_YONETICISI = KivMob(ADMOB_APP_ID)
        _REKLAM_YONETICISI.set_rewarded_ad_listener(_OdulDinleyici())
        _REKLAM_YONETICISI.load_rewarded_ad(ADMOB_REWARDED_ID)
        _REKLAM_HATA = "Reklam talep edildi ancak henuz hazir olmayabilir. Biraz sonra tekrar deneyin."
    except Exception as e:
        _REKLAM_HATA = "Reklam baslatilamadi: " + str(e)
        _REKLAM_YONETICISI = None
        print(_REKLAM_HATA)


def reklam_yeniden_yukle():
    global _REKLAM_HATA
    if _REKLAM_YONETICISI:
        try:
            _REKLAM_YONETICISI.load_rewarded_ad(ADMOB_REWARDED_ID)
        except Exception as e:
            _REKLAM_HATA = "Reklam yeniden yuklenemedi: " + str(e)
            print(_REKLAM_HATA)


def reklam_goster(callback):
    global _ODUL_CALLBACK, _REKLAM_HATA
    if _REKLAM_YONETICISI is None:
        _ODUL_CALLBACK = None
        _reklam_uyarisi(_REKLAM_HATA)
        return
    try:
        _ODUL_CALLBACK = callback
        _REKLAM_YONETICISI.show_rewarded_ad()
    except Exception as e:
        _ODUL_CALLBACK = None
        _REKLAM_HATA = "Reklam gosterilemedi: " + str(e)
        print(_REKLAM_HATA)
        _reklam_uyarisi(_REKLAM_HATA)

ASSETS_KLASORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# ==========================================
# SES YONETIMI
# ==========================================
SES_ACIK = True
_SES_CACHE = {}


def _ses_dosyasi(ad):
    yol = os.path.join(ASSETS_KLASORU, ad)
    return yol if os.path.exists(yol) else None


def ses_efekti_cal(ses_tipi):
    if not SES_ACIK:
        return
    try:
        if ses_tipi in _SES_CACHE:
            s = _SES_CACHE[ses_tipi]
            s.stop()
            s.play()
            return
        dosya = _ses_dosyasi(f"{ses_tipi}.wav")
        if dosya:
            s = SoundLoader.load(dosya)
            if s:
                _SES_CACHE[ses_tipi] = s
                s.play()
    except Exception as e:
        print(f"Ses hatasi: {e}")


_MUZIK = None


def muzik_baslat():
    global _MUZIK
    if not SES_ACIK:
        return
    dosya = _ses_dosyasi("fon_muzigi.mp3")
    if not dosya:
        kok = os.path.dirname(os.path.abspath(__file__))
        for f in os.listdir(kok):
            if f.lower().endswith(".mp3"):
                dosya = os.path.join(kok, f)
                break
    if dosya:
        try:
            _MUZIK = SoundLoader.load(dosya)
            if _MUZIK:
                _MUZIK.loop = True
                _MUZIK.volume = 0.5
                _MUZIK.play()
        except Exception as e:
            print(f"Muzik hatasi: {e}")


def muzik_ses_seviyesi_ayarla(seviye):
    if _MUZIK and SES_ACIK:
        try:
            _MUZIK.volume = seviye
        except Exception:
            pass


def genel_ses_ac_kapa():
    global SES_ACIK
    SES_ACIK = not SES_ACIK
    if not SES_ACIK:
        if _MUZIK:
            _MUZIK.stop()
    else:
        muzik_baslat()
    return SES_ACIK


def metni_turkce_seslendir(metin, bitince_bunu_yap=None):
    if not SES_ACIK or not GTTS_MEVCUT:
        if bitince_bunu_yap:
            Clock.schedule_once(lambda dt: bitince_bunu_yap(), 0)
        return

    def seslendir():
        dosya_adi = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f"gecici_ses_{random.randint(1000, 9999)}.mp3")
        try:
            tts = gTTS(text=metin, lang='tr', slow=False)
            tts.save(dosya_adi)
            s = SoundLoader.load(dosya_adi)
            if s and SES_ACIK:
                s.play()
                time.sleep(s.length if s.length else 1.5)
            try:
                os.remove(dosya_adi)
            except Exception:
                pass
        except Exception as e:
            print(f"Turkce seslendirme hatasi: {e}")
        if bitince_bunu_yap:
            Clock.schedule_once(lambda dt: bitince_bunu_yap(), 0)

    threading.Thread(target=seslendir, daemon=True).start()


# ==========================================
# ORTAK RENKLER / YARDIMCILAR
# ==========================================
BALON_RENKLERI = [
    (1, 0.30, 0.30, 1), (0.30, 0.58, 1, 1), (0.30, 1, 0.53, 1),
    (1, 0.84, 0.20, 1), (0.70, 0.40, 1, 1), (1, 0.60, 0.20, 1),
]

RENK_SOZLUGU = {
    "Kirmizi": (1, 0.2, 0.2, 1), "Yesil": (0.18, 0.80, 0.44, 1),
    "Mavi": (0.20, 0.60, 0.86, 1), "Turuncu": (0.90, 0.49, 0.13, 1),
    "Mor": (0.61, 0.35, 0.71, 1), "Sari": (0.95, 0.77, 0.06, 1),
}
SEKIL_TIPLERI = ["Yuvarlak", "Kare", "Ucgen", "Yildiz"]


def format_sure(saniye):
    saniye = max(0, int(saniye))
    return f"{saniye // 60}:{saniye % 60:02d}"


class KalpGostergesi(Widget):
    def __init__(self, canlar=0, maxcan=3, **kwargs):
        super().__init__(**kwargs)
        self.canlar = canlar
        self.maxcan = maxcan
        self.bind(size=self._ciz, pos=self._ciz)

    def guncelle(self, canlar, maxcan):
        self.canlar = canlar
        self.maxcan = maxcan
        self._ciz()

    @staticmethod
    def _tek_kalp(cx, cy, b, dolu):
        r = b * 0.27
        if dolu:
            Color(0.90, 0.18, 0.22, 1)
        else:
            Color(0.72, 0.72, 0.76, 1)
        Ellipse(pos=(cx - r * 1.9, cy - r * 0.25), size=(r * 2, r * 2))
        Ellipse(pos=(cx - r * 0.1, cy - r * 0.25), size=(r * 2, r * 2))
        Triangle(points=[cx - r * 1.85, cy + r * 0.35, cx + r * 1.85, cy + r * 0.35, cx, cy - b * 0.42])

    def _ciz(self, *a):
        self.canvas.clear()
        w, h = self.size
        if w <= 1 or h <= 1 or self.maxcan <= 0:
            return
        with self.canvas:
            boyut = min(h * 0.9, w / self.maxcan * 0.9)
            bosluk = max(2, (w - boyut * self.maxcan) / (self.maxcan + 1))
            for i in range(self.maxcan):
                cx = self.x + bosluk * (i + 1) + boyut * i + boyut / 2
                cy = self.y + h / 2
                self._tek_kalp(cx, cy, boyut, i < self.canlar)


class IkonKutusu(Widget):
    def __init__(self, cizim_fn, **kwargs):
        super().__init__(**kwargs)
        self._cizim_fn = cizim_fn
        self.bind(size=self._ciz, pos=self._ciz)

    def _ciz(self, *a):
        self.canvas.clear()
        w, h = self.size
        if w <= 1 or h <= 1:
            return
        with self.canvas:
            self._cizim_fn(self.x + w / 2, self.y + h / 2, min(w, h))


def _ikon_balon(cx, cy, b):
    Color(1, 0.30, 0.30, 1)
    Ellipse(pos=(cx - b * 0.28, cy - b * 0.08), size=(b * 0.56, b * 0.56))


def _ikon_ari(cx, cy, b):
    Color(1, 0.76, 0.03, 1)
    Ellipse(pos=(cx - b * 0.32, cy - b * 0.20), size=(b * 0.64, b * 0.42))


def _ikon_sekil(cx, cy, b):
    Color(0.20, 0.60, 0.86, 1)
    Ellipse(pos=(cx - b * 0.36, cy - b * 0.05), size=(b * 0.30, b * 0.30))


def _ikon_kart(cx, cy, b):
    Color(0.20, 0.60, 0.86, 1)
    Rectangle(pos=(cx - b * 0.32, cy - b * 0.24), size=(b * 0.30, b * 0.44))


class EnerjikArkaplan(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._yeniden_ciz, pos=self._yeniden_ciz)
        Clock.schedule_once(self._yeniden_ciz, 0)

    def _yeniden_ciz(self, *a):
        self.canvas.before.clear()
        w, h = self.size
        if w <= 1 or h <= 1:
            return
        with self.canvas.before:
            renk_ust = (0.25, 0.35, 0.85, 1)
            renk_alt = (1.0, 0.55, 0.35, 1)
            adim = 14
            for i in range(adim):
                t = i / (adim - 1)
                r = renk_ust[0] + (renk_alt[0] - renk_ust[0]) * t
                g = renk_ust[1] + (renk_alt[1] - renk_ust[1]) * t
                b = renk_ust[2] + (renk_alt[2] - renk_ust[2]) * t
                Color(r, g, b, 1)
                Rectangle(pos=(self.x, self.y + h - (i + 1) * (h / adim) - 1), size=(w, h / adim + 2))


# ==========================================
# UST PANEL
# ==========================================
class UstPanel(BoxLayout):
    def __init__(self, app, geri_callback, **kwargs):
        super().__init__(orientation="horizontal", size_hint=(1, None), height=45,
                         padding=6, spacing=6, **kwargs)
        self.app = app

        self.btn_geri = Button(text="< Menu", size_hint=(0.2, 1),
                               background_color=(0.90, 0.30, 0.30, 1), bold=True)
        self.btn_geri.bind(on_release=lambda *a: geri_callback())
        self.add_widget(self.btn_geri)

        self.kalp_gosterge = KalpGostergesi(app.canlar, app.max_can, size_hint=(0.35, 1))
        self.add_widget(self.kalp_gosterge)

        self.lbl_sure = Label(text="", font_size="10sp", size_hint=(0.2, 1), color=(1, 1, 1, 1))
        self.add_widget(self.lbl_sure)

        self.btn_ses = Button(text="Ses" if SES_ACIK else "Sessiz", size_hint=(0.25, 1),
                              background_color=(0.18, 0.80, 0.44, 1) if SES_ACIK else (0.90, 0.30, 0.30, 1))
        self.btn_ses.bind(on_release=self.ses_degistir)
        self.add_widget(self.btn_ses)

    def ses_guncelle(self):
        self.kalp_gosterge.guncelle(self.app.canlar, self.app.max_can)

    def ses_degistir(self, *a):
        acik = genel_ses_ac_kapa()
        self.btn_ses.text = "Ses" if acik else "Sessiz"
        self.btn_ses.background_color = (0.18, 0.80, 0.44, 1) if acik else (0.90, 0.30, 0.30, 1)


# ==========================================
# CAN BITTI POPUP
# ==========================================
def can_bitti_popup_goster(app, oyun_kodu, menuye_don_callback):
    icerik = BoxLayout(orientation="vertical", spacing=10, padding=10)
    icerik.add_widget(Label(text="CANLARIN BITTI!", font_size="20sp", bold=True, color=(1, 0.3, 0.3, 1), size_hint=(1, 0.3)))
    icerik.add_widget(Label(text="Devam etmek icin reklam izle!", font_size="13sp", color=(1, 0.9, 0.4, 1), size_hint=(1, 0.2)))

    popup = Popup(title="", separator_height=0, size_hint=(0.8, 0.5), auto_dismiss=False)

    def can_kazan(*a):
        def odul_verildi():
            app.canlar = min(app.max_can, app.canlar + 1)
            ses_efekti_cal("alkis")
            popup.dismiss()
            menuye_don_callback()
        reklam_goster(odul_verildi)

    def menuye_git(*a):
        popup.dismiss()
        menuye_don_callback()

    btn_reklam = Button(text="REKLAM IZLE & +1 CAN", size_hint=(1, 0.3), background_color=(0.18, 0.80, 0.44, 1), bold=True)
    btn_reklam.bind(on_release=can_kazan)
    icerik.add_widget(btn_reklam)

    btn_menu = Button(text="Menuye Don", size_hint=(1, 0.3), background_color=(0.90, 0.30, 0.30, 1))
    btn_menu.bind(on_release=menuye_git)
    icerik.add_widget(btn_menu)

    popup.content = icerik
    popup.open()


# ==========================================
# EKRAN 0: YUKLEME EKRANI
# ==========================================
class YuklemeEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kok = EnerjikArkaplan()
        icerik = BoxLayout(orientation="vertical", padding=30, spacing=14, size_hint=(0.8, 0.3),
                           pos_hint={"center_x": 0.5, "center_y": 0.5})
        icerik.add_widget(Label(text="MINIK KASIFLER", font_size="22sp", bold=True, color=(1, 1, 1, 1)))
        self.lbl_durum = Label(text="Hazirlaniyor...", font_size="15sp", color=(1, 0.95, 0.6, 1))
        icerik.add_widget(self.lbl_durum)
        kok.add_widget(icerik)
        self.add_widget(kok)


# ==========================================
# EKRAN 1: GIRIS EKRANI
# ==========================================
class TasarimArkaplani(FloatLayout):
    """Gorsel uzerindeki bolgeleri gercek dokunmatik kontrollere baglar."""
    def __init__(self, dosya, **kwargs):
        super().__init__(**kwargs)
        self.resim = Image(source=os.path.join(ASSETS_KLASORU, dosya),
                           allow_stretch=True, keep_ratio=False,
                           size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.resim)


class GirisEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        kok = TasarimArkaplani("giris_tasarim.png")
        # Gorseldeki isim alanini gercek, duzenlenebilir kutuyla ortuyoruz.
        self.isim_kutusu = TextInput(
            hint_text="Adini yaz", multiline=False, font_size="20sp",
            halign="center", foreground_color=(0.24, 0.16, 0.10, 1),
            background_color=(1, 0.97, 0.88, 1),
            size_hint=(0.64, 0.062), pos_hint={"center_x": 0.5, "y": 0.135})
        kok.add_widget(self.isim_kutusu)
        # Gorseldeki yesil Basla dugmesi zaten resimde; gorunmez
        # dokunma alani dugmenin tam uzerinde calisir.
        basla = Button(text="", background_color=(1, 1, 1, 0),
                       background_normal="", background_down="",
                       size_hint=(0.74, 0.11), pos_hint={"center_x": 0.5, "y": 0.022})
        basla.bind(on_release=self.oyuna_basla)
        kok.add_widget(basla)
        self.add_widget(kok)

    def oyuna_basla(self, *a):
        app = App.get_running_app()
        isim = self.isim_kutusu.text.strip()
        if isim:
            app.cocuk_ismi = isim
        ses_efekti_cal("tin")
        self.manager.current = "menu"


class MenuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kok = TasarimArkaplani("menu_tasarim.png")
        # 2x2 buyuk oyun kartlari, tasarimdaki yerlerine yerlestirildi.
        kartlar = [
            ("balon", 0.055, 0.55), ("ari", 0.515, 0.55),
            ("sekil", 0.055, 0.305), ("bulmaca", 0.515, 0.305),
        ]
        for kod, x, y in kartlar:
            btn = Button(text="", background_normal="", background_down="",
                         background_color=(1, 1, 1, 0),
                         size_hint=(0.43, 0.24), pos_hint={"x": x, "y": y})
            btn.bind(on_release=lambda inst, k=kod: self.oyun_sec(k))
            self.kok.add_widget(btn)
        self.baslik = Label(text="", font_size="18sp", bold=True,
                            color=(0.12, 0.12, 0.12, 1),
                            size_hint=(0.48, 0.065), pos_hint={"x": 0.30, "y": 0.865})
        self.kok.add_widget(self.baslik)
        self.add_widget(self.kok)

    def on_enter(self):
        app = App.get_running_app()
        self.baslik.text = app.cocuk_ismi[:15]

    def oyun_sec(self, kod):
        app = App.get_running_app()
        ses_efekti_cal("tin")
        if app.canlar <= 0:
            can_bitti_popup_goster(app, kod, lambda: setattr(self.manager, "current", "menu"))
            return
        self.manager.current = kod
        self.manager.get_screen(kod).oyunu_baslat()


# ==========================================
# OYUN 1: BALON PATLATMA (Tuzak Balonlu & Kompakt Alan)
# ==========================================
class BalonOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = EnerjikArkaplan()
        self.dis = BoxLayout(orientation="vertical", padding=10, spacing=5)

        # Kompakt/Kucultulmus Oyun Alani Container'i
        self.cerceve = FloatLayout(size_hint=(1, 0.85))
        self.oyun_alani = Widget(size_hint=(0.9, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)
        self.cerceve.add_widget(self.oyun_alani)

        self.lbl_skor = Label(text="Puan: 0 | Seviye: 1", size_hint=(1, None), height=35, color=(1, 1, 1, 1), bold=True)

        self.dis.add_widget(self.lbl_skor)
        self.dis.add_widget(self.cerceve)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._olay = None
        self.balonlar = []

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._olay:
            self._olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.puan = 0
        self.seviye = 1
        self.balon_sayaci = 0
        self.oyun_aktif = True
        self.balonlar = []
        muzik_ses_seviyesi_ayarla(0.2)
        if self._olay:
            self._olay.cancel()
        self._olay = Clock.schedule_interval(self.adim, 1 / 30)

    def adim(self, dt):
        if not self.oyun_aktif:
            return
        w = self.oyun_alani.width or 350
        h = self.oyun_alani.height or 450

        # Balon uretme sikligi
        if random.random() < 0.035:
            self.balon_sayaci += 1
            tuzak = (self.balon_sayaci % 7 == 0) # Her 7-8 balon bir tuzak balon!
            self.balonlar.append({
                "x": random.uniform(40, w - 40),
                "y": -30,
                "hiz": 1.5 + self.seviye * 0.4,
                "renk": (0.1, 0.1, 0.1, 1) if tuzak else random.choice(BALON_RENKLERI),
                "tuzak": tuzak,
                "aci": random.uniform(0, 10)
            })

        yeni_balonlar = []
        for b in self.balonlar:
            b["y"] += b["hiz"]
            b["aci"] += 0.05
            b["x"] += math.sin(b["aci"]) * 1.5
            if b["y"] < h + 30:
                yeni_balonlar.append(b)
            elif not b["tuzak"]:
                self._can_azalt()
                if not self.oyun_aktif:
                    break
        self.balonlar = yeni_balonlar

        # Cizim
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            for b in self.balonlar:
                r = 30
                Color(*b["renk"])
                Ellipse(pos=(self.oyun_alani.x + b["x"] - r, self.oyun_alani.y + b["y"] - r), size=(r * 2, r * 2))
                if b["tuzak"]:
                    # Tuzak balonu uzerinde carpi isareti
                    Color(1, 1, 1, 1)
                    Line(points=[self.oyun_alani.x + b["x"] - 12, self.oyun_alani.y + b["y"] - 12,
                                 self.oyun_alani.x + b["x"] + 12, self.oyun_alani.y + b["y"] + 12], width=2)
                    Line(points=[self.oyun_alani.x + b["x"] - 12, self.oyun_alani.y + b["y"] + 12,
                                 self.oyun_alani.x + b["x"] + 12, self.oyun_alani.y + b["y"] - 12], width=2)

    def dokunuldu(self, inst, touch):
        if not self.oyun_aktif or not self.oyun_alani.collide_point(*touch.pos):
            return
        local_x = touch.x - self.oyun_alani.x
        local_y = touch.y - self.oyun_alani.y

        for b in self.balonlar[:]:
            if abs(local_x - b["x"]) < 35 and abs(local_y - b["y"]) < 35:
                if b["tuzak"]:
                    # Tuzak balona tiklandi! Can kaybet
                    ses_efekti_cal("uzuntu")
                    self.balonlar.remove(b)
                    self._can_azalt()
                else:
                    ses_efekti_cal("alkis")
                    self.puan += 10
                    yeni_seviye = (self.puan // 50) + 1
                    if yeni_seviye > self.seviye:
                        self.seviye = yeni_seviye
                        metni_turkce_seslendir(f"Tebrikler, Seviye {self.seviye}")
                        self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye} (Onceki Puan: {self.puan-10})"
                    self.balonlar.remove(b)
                    self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye}"
                break

    def _can_azalt(self):
        self.app.canlar = max(0, self.app.canlar - 1)
        ses_efekti_cal("uzuntu")
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._olay:
                self._olay.cancel()
            can_bitti_popup_goster(self.app, "balon", self.menuye_don)


# ==========================================
# OYUN 2: NESELI ARI (Ağaç Sorunu Çözüldü & Kovan Eklendi)
# ==========================================
class AriOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = EnerjikArkaplan()
        self.dis = BoxLayout(orientation="vertical", padding=10, spacing=5)
        self.oyun_alani = Widget(size_hint=(1, 0.85))
        self.oyun_alani.bind(on_touch_move=self.parmak_hareket, on_touch_down=self.parmak_hareket)

        self.lbl_skor = Label(text="Puan: 0 | Seviye: 1", size_hint=(1, None), height=35, color=(1, 1, 1, 1), bold=True)
        self.dis.add_widget(self.lbl_skor)
        self.dis.add_widget(self.oyun_alani)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._olay = None

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._olay:
            self._olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.puan = 0
        self.seviye = 1
        self.kalan_mesafe = 400
        self.ari_y = 250
        self.engeller = []
        self._engel_bekleme = 15
        self.oyun_aktif = True
        muzik_ses_seviyesi_ayarla(0.2)
        if self._olay:
            self._olay.cancel()
        self._olay = Clock.schedule_interval(self.adim, 1 / 30)

    def parmak_hareket(self, inst, touch):
        if self.oyun_aktif and self.oyun_alani.collide_point(*touch.pos):
            self.ari_y = max(20, min(self.oyun_alani.height - 20, touch.y - self.oyun_alani.y))

    def adim(self, dt):
        if not self.oyun_aktif:
            return
        w = self.oyun_alani.width or 400
        h = self.oyun_alani.height or 500
        ari_x = 70

        hiz = 3.0 + self.seviye * 0.5
        self.kalan_mesafe -= 1

        # Surekli agac/engel uretimi (Seviye 5 ve sonrasında da devam etmesi sağlandı)
        self._engel_bekleme -= 1
        if self._engel_bekleme <= 0:
            yeni_y = random.uniform(60, h - 60)
            self.engeller.append([w + 30, yeni_y, random.uniform(80, 140)])
            self._engel_bekleme = max(25, 55 - self.seviye * 3)

        yeni = []
        carpisti = False
        for eng in self.engeller:
            eng[0] -= hiz
            ex, ey, eh = eng
            if abs(ari_x - ex) < 30 and abs(self.ari_y - ey) < (eh / 2 + 20):
                carpisti = True
            if ex > -50:
                yeni.append(eng)
        self.engeller = yeni

        if carpisti:
            ses_efekti_cal("uzuntu")
            self._can_azalt()
            self.engeller = []
            return

        self._ciz(ari_x, h)

        if self.kalan_mesafe <= 0:
            ses_efekti_cal("alkis")
            self.puan += 50
            self.seviye += 1
            metni_turkce_seslendir(f"Tebrikler, kowana ulastin! Seviye {self.seviye}")
            self.kalan_mesafe = 400 + self.seviye * 100
            self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye} (Onceki Puan: {self.puan-50})"

    def _ciz(self, ari_x, h):
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            # Agac engelleri
            for ex, ey, eh in self.engeller:
                Color(0.35, 0.20, 0.10, 1) # Kahverengi govde
                Rectangle(pos=(self.oyun_alani.x + ex - 15, self.oyun_alani.y + ey - eh / 2), size=(30, eh))
                Color(0.15, 0.60, 0.20, 1) # Yesil yaprak
                Ellipse(pos=(self.oyun_alani.x + ex - 30, self.oyun_alani.y + ey - eh / 2 - 20), size=(60, 40))

            # Kovan (Ekranda hedef olarak gorsel kovan seklinde cizildi)
            if self.kalan_mesafe < 60:
                kx, ky = self.oyun_alani.x + (self.oyun_alani.width or 400) - 60, self.oyun_alani.y + h / 2
                Color(0.85, 0.55, 0.15, 1)
                Ellipse(pos=(kx - 25, ky - 35), size=(50, 70))
                Color(0.4, 0.2, 0.05, 1)
                Ellipse(pos=(kx - 10, ky - 10), size=(20, 20))

            # Ari Cizimi
            Color(1, 0.8, 0.0, 1)
            Ellipse(pos=(self.oyun_alani.x + ari_x - 20, self.oyun_alani.y + self.ari_y - 15), size=(40, 30))
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=(self.oyun_alani.x + ari_x - 8, self.oyun_alani.y + self.ari_y - 15), size=(6, 30))

        self.lbl_skor.text = f"Puan: {self.puan} | Seviye: {self.seviye}"

    def _can_azalt(self):
        self.app.canlar = max(0, self.app.canlar - 1)
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._olay:
                self._olay.cancel()
            can_bitti_popup_goster(self.app, "ari", self.menuye_don)


# ==========================================
# OYUN 3: SEKIL VE RENK AVCISI (Büyük İkonlar & Adet Gösterimi)
# ==========================================
class SekilOyunuEkrani(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = EnerjikArkaplan()
        self.dis = BoxLayout(orientation="vertical", padding=10, spacing=5)

        self.lbl_soru = Label(text="", size_hint=(1, None), height=45, bold=True, color=(1, 1, 0, 1), font_size="16sp")
        self.lbl_durum = Label(text="", size_hint=(1, None), height=30, color=(1, 1, 1, 1))
        
        self.cerceve = FloatLayout(size_hint=(1, 0.8))
        self.oyun_alani = Widget(size_hint=(0.85, 0.85), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)
        self.cerceve.add_widget(self.oyun_alani)

        self.dis.add_widget(self.lbl_soru)
        self.dis.add_widget(self.lbl_durum)
        self.dis.add_widget(self.cerceve)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._zaman_olay = None
        self.nesneler = []

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._zaman_olay:
            self._zaman_olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.seviye = 1
        self.puan = 0
        muzik_ses_seviyesi_ayarla(0.2)
        self._seviye_yukle()

    def _seviye_yukle(self):
        self.oyun_aktif = True
        self.kalan_sure = max(10, 25 - self.seviye)
        self.bulunan = 0

        self.hedef_renk_adi = random.choice(list(RENK_SOZLUGU.keys()))
        self.hedef_renk = RENK_SOZLUGU[self.hedef_renk_adi]
        self.hedef_sekil = random.choice(SEKIL_TIPLERI)
        self.hedef_sayi = random.randint(2, 4)

        self.nesneler = []
        for _ in range(self.hedef_sayi):
            self.nesneler.append({"renk": self.hedef_renk, "sekil": self.hedef_sekil, "hedef": True, "bulundu": False})

        for _ in range(6):
            r_ad = random.choice(list(RENK_SOZLUGU.keys()))
            s_tip = random.choice(SEKIL_TIPLERI)
            if r_ad == self.hedef_renk_adi and s_tip == self.hedef_sekil:
                s_tip = "Kare" if self.hedef_sekil != "Kare" else "Yuvarlak"
            self.nesneler.append({"renk": RENK_SOZLUGU[r_ad], "sekil": s_tip, "hedef": False, "bulundu": False})

        random.shuffle(self.nesneler)

        # Çocukların rahat anlaması için büyük yazı ve adet gösterimi
        self.lbl_soru.text = f"BULACAGIN: {self.hedef_sayi} Adet ({self.hedef_renk_adi} {self.hedef_sekil})"
        self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan} | Sure: {self.kalan_sure}"

        Clock.schedule_once(lambda dt: self._konumlandir_ve_ciz(), 0)
        metni_turkce_seslendir(f"{self.hedef_sayi} tane {self.hedef_renk_adi} {self.hedef_sekil} bul")
        if self._zaman_olay:
            self._zaman_olay.cancel()
        self._zaman_olay = Clock.schedule_interval(self._zaman_adimi, 1)

    def _konumlandir_ve_ciz(self):
        w = self.oyun_alani.width or 320
        h = self.oyun_alani.height or 350
        n_toplam = len(self.nesneler)
        cols = 3
        rows = math.ceil(n_toplam / cols)
        hucre_w, hucre_h = w / cols, h / rows

        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx >= len(self.nesneler):
                    break
                self.nesneler[idx]["x"] = c * hucre_w + hucre_w / 2
                self.nesneler[idx]["y"] = (rows - 1 - r) * hucre_h + hucre_h / 2
                idx += 1
        self._ciz()

    def _zaman_adimi(self, dt):
        if not self.oyun_aktif:
            return False
        if self.kalan_sure > 0:
            self.kalan_sure -= 1
            self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan} | Sure: {self.kalan_sure}"
        else:
            self._zaman_olay.cancel()
            self.oyun_aktif = False
            self._can_azalt()
            return False

    def _ciz(self):
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            for n in self.nesneler:
                x = self.oyun_alani.x + n["x"]
                y = self.oyun_alani.y + n["y"]
                r = 35 # Cocuklar icin daha buyuk sekil boyutlari
                if n["bulundu"]:
                    Color(0.18, 0.80, 0.44, 1)
                    Ellipse(pos=(x - r - 6, y - r - 6), size=((r + 6) * 2, (r + 6) * 2))
                Color(*n["renk"])
                s = n["sekil"]
                if s == "Yuvarlak":
                    Ellipse(pos=(x - r, y - r), size=(r * 2, r * 2))
                elif s == "Kare":
                    Rectangle(pos=(x - r, y - r), size=(r * 2, r * 2))
                elif s == "Ucgen":
                    Triangle(points=[x, y + r, x - r, y - r, x + r, y - r])
                elif s == "Yildiz":
                    Ellipse(pos=(x - r, y - r), size=(r * 2, r * 2)) # Alternatif buyuk daire/yildiz temsili

    def dokunuldu(self, inst, touch):
        if not self.oyun_aktif or not self.oyun_alani.collide_point(*touch.pos):
            return
        local_x = touch.x - self.oyun_alani.x
        local_y = touch.y - self.oyun_alani.y

        for n in self.nesneler:
            if n["bulundu"]:
                continue
            if abs(local_x - n["x"]) < 40 and abs(local_y - n["y"]) < 40:
                if n["hedef"]:
                    n["bulundu"] = True
                    self.bulunan += 1
                    self.puan += 10
                    ses_efekti_cal("tin")
                    self._ciz()
                    if self.bulunan >= self.hedef_sayi:
                        self._kazandi()
                else:
                    self._can_azalt()
                return

    def _kazandi(self):
        self.oyun_aktif = False
        if self._zaman_olay:
            self._zaman_olay.cancel()
        ses_efekti_cal("alkis")
        self.seviye += 1
        self.puan += 30
        metni_turkce_seslendir(f"Tebrikler! Seviye {self.seviye}ye geciliyor")
        self.lbl_soru.text = f"TEBRIKLER! Puan: {self.puan}"
        Clock.schedule_once(lambda dt: self._seviye_yukle() if self.manager and self.manager.current == self.name else None, 2)

    def _can_azalt(self):
        ses_efekti_cal("uzuntu")
        self.app.canlar = max(0, self.app.canlar - 1)
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            if self._zaman_olay:
                self._zaman_olay.cancel()
            can_bitti_popup_goster(self.app, "sekil", self.menuye_don)
        else:
            self._ciz()


# ==========================================
# OYUN 4: KART ESLESTIRME (Bulmaca Kulesi)
# ==========================================
class BulmacaOyunuEkrani(Screen):
    SEMBOLLER = ["Kopek", "Kedi", "Elma", "Muz", "Araba", "Roket", "Balon", "Yildiz"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.kok = EnerjikArkaplan()
        self.dis = BoxLayout(orientation="vertical", padding=10, spacing=5)

        self.lbl_durum = Label(text="", size_hint=(1, None), height=35, bold=True, color=(0, 1, 1, 1))
        self.cerceve = FloatLayout(size_hint=(1, 0.8))
        self.oyun_alani = Widget(size_hint=(0.9, 0.9), pos_hint={"center_x": 0.5, "center_y": 0.5})
        self.oyun_alani.bind(on_touch_down=self.dokunuldu)
        self.cerceve.add_widget(self.oyun_alani)

        self.dis.add_widget(self.lbl_durum)
        self.dis.add_widget(self.cerceve)
        self.kok.add_widget(self.dis)
        self.add_widget(self.kok)
        self.ust_panel = None
        self._ezber_olay = None
        self.kartlar = []

    def _panel_kur(self):
        if self.ust_panel is None:
            self.ust_panel = UstPanel(self.app, self.menuye_don)
            self.dis.add_widget(self.ust_panel, index=len(self.dis.children))

    def menuye_don(self):
        self.oyun_aktif = False
        if self._ezber_olay:
            self._ezber_olay.cancel()
        self.manager.current = "menu"

    def oyunu_baslat(self):
        self.app = App.get_running_app()
        self._panel_kur()
        self.seviye = 1
        self.puan = 0
        muzik_ses_seviyesi_ayarla(0.2)
        self._seviye_yukle()

    def _seviye_yukle(self):
        self.oyun_aktif = True
        self.secilenler = []
        self.eslesen_cift = 0
        self.tiklama_kilitli = True
        self.ezber_suresi = 4

        toplam_cift = 3 if self.seviye == 1 else 4
        secilen = random.sample(self.SEMBOLLER, toplam_cift)
        liste = secilen * 2
        random.shuffle(liste)
        self.toplam_cift = toplam_cift
        self.kartlar = [{"sembol": s, "acik": True, "eslesdi": False} for s in liste]

        self.lbl_durum.text = f"Seviye {self.seviye} | Puan {self.puan}"
        Clock.schedule_once(lambda dt: self._ciz(), 0)
        metni_turkce_seslendir("Kartlari aklinda tut")
        if self._ezber_olay:
            self._ezber_olay.cancel()
        self._ezber_olay = Clock.schedule_interval(self._ezber_adimi, 1)

    def _ezber_adimi(self, dt):
        if not self.oyun_aktif:
            return False
        if self.ezber_suresi > 0:
            self.ezber_suresi -= 1
            self._ciz()
        else:
            for k in self.kartlar:
                k["acik"] = False
            self.tiklama_kilitli = False
            ses_efekti_cal("tin")
            self._ciz()
            return False

    def _kart_konumu(self, idx):
        w = self.oyun_alani.width or 320
        h = self.oyun_alani.height or 350
        cols = 3 if self.toplam_cift == 3 else 4
        rows = 2
        cw, ch = 75, 75
        toplam_w = cols * 85
        start_x = (w - toplam_w) / 2
        col = idx % cols
        row = idx // cols
        x = start_x + col * 85
        y = h / 2 + (0.5 - row) * 90
        return x, y, cw, ch

    def _ciz(self):
        self.oyun_alani.canvas.clear()
        with self.oyun_alani.canvas:
            for idx, kart in enumerate(self.kartlar):
                x, y, cw, ch = self._kart_konumu(idx)
                ax = self.oyun_alani.x + x
                ay = self.oyun_alani.y + y
                if kart["eslesdi"] or kart["acik"]:
                    Color(1, 1, 1, 1)
                    Rectangle(pos=(ax, ay), size=(cw, ch))
                    Color(0.1, 0.1, 0.1, 1)
                    # Sembol adi yazisi yerine basit kutu ici sembol
                    Rectangle(pos=(ax + 15, ay + 15), size=(cw - 30, ch - 30))
                else:
                    Color(0.20, 0.60, 0.86, 1)
                    Rectangle(pos=(ax, ay), size=(cw, ch))

    def dokunuldu(self, inst, touch):
        if not self.oyun_aktif or self.tiklama_kilitli or not self.oyun_alani.collide_point(*touch.pos):
            return
        local_x = touch.x - self.oyun_alani.x
        local_y = touch.y - self.oyun_alani.y

        for idx, kart in enumerate(self.kartlar):
            if kart["acik"] or kart["eslesdi"]:
                continue
            x, y, cw, ch = self._kart_konumu(idx)
            if x <= local_x <= x + cw and y <= local_y <= y + ch:
                ses_efekti_cal("tik")
                kart["acik"] = True
                self.secilenler.append(kart)
                self._ciz()
                if len(self.secilenler) == 2:
                    self.tiklama_kilitli = True
                    k1, k2 = self.secilenler
                    if k1["sembol"] == k2["sembol"]:
                        ses_efekti_cal("alkis")
                        k1["eslesdi"] = True
                        k2["eslesdi"] = True
                        self.eslesen_cift += 1
                        self.puan += 15
                        self.secilenler = []
                        self.tiklama_kilitli = False
                        self._ciz()
                        if self.eslesen_cift >= self.toplam_cift:
                            self._kazandi()
                    else:
                        ses_efekti_cal("uzuntu")
                        Clock.schedule_once(lambda dt, c1=k1, c2=k2: self._kapat(c1, c2), 0.7)
                return

    def _kapat(self, k1, k2):
        k1["acik"] = False
        k2["acik"] = False
        self.secilenler = []
        self.tiklama_kilitli = False
        self._can_azalt()
        if self.oyun_aktif:
            self._ciz()

    def _kazandi(self):
        self.oyun_aktif = False
        ses_efekti_cal("alkis")
        self.seviye += 1
        self.puan += 40
        metni_turkce_seslendir(f"Tebrikler! Seviye {self.seviye}ye geciliyor")
        self.lbl_durum.text = f"TEBRIKLER! Puan: {self.puan}"
        Clock.schedule_once(lambda dt: self._seviye_yukle() if self.manager and self.manager.current == self.name else None, 2)

    def _can_azalt(self):
        self.app.canlar = max(0, self.app.canlar - 1)
        if self.ust_panel:
            self.ust_panel.ses_guncelle()
        if self.app.canlar <= 0:
            self.oyun_aktif = False
            can_bitti_popup_goster(self.app, "bulmaca", self.menuye_don)


# ==========================================
# ANA UYGULAMA (Gerçek Saniye Sayaç Düzeltmesi ile)
# ==========================================
class MinikKasiflerApp(App):
    def build(self):
        Window.clearcolor = (0.25, 0.35, 0.85, 1)
        self.cocuk_ismi = "Minik Kasif"
        self.canlar = 3
        self.max_can = 3
        self.can_yenilenme_suresi = 90
        self.kalan_can_suresi = self.can_yenilenme_suresi

        self.sm = ScreenManager()
        self.sm.add_widget(YuklemeEkrani(name="yukleme"))
        self.sm.current = "yukleme"

        Clock.schedule_once(self._agir_ekranlari_kur, 0.05)
        Clock.schedule_interval(self._can_zamanlayicisi, 1) # Kesintisiz saniye sayacı
        return self.sm

    def _agir_ekranlari_kur(self, dt):
        self.sm.add_widget(GirisEkrani(name="giris"))
        self.sm.add_widget(MenuEkrani(name="menu"))
        self.sm.add_widget(BalonOyunuEkrani(name="balon"))
        self.sm.add_widget(AriOyunuEkrani(name="ari"))
        self.sm.add_widget(SekilOyunuEkrani(name="sekil"))
        self.sm.add_widget(BulmacaOyunuEkrani(name="bulmaca"))
        muzik_baslat()
        reklam_sistemini_baslat()
        self.sm.current = "giris"

    def _can_zamanlayicisi(self, dt):
        if self.canlar < self.max_can:
            self.kalan_can_suresi -= 1
            # Üst paneldeki süreyi her saniye dinamik olarak güncelle
            for ekran_adi in ["balon", "ari", "sekil", "bulmaca"]:
                if not self.sm.has_screen(ekran_adi):
                    continue
                scr = self.sm.get_screen(ekran_adi)
                if hasattr(scr, "ust_panel") and scr.ust_panel:
                    if scr.ust_panel.lbl_sure:
                        scr.ust_panel.lbl_sure.text = f"+1 can:\n{format_sure(self.kalan_can_suresi)}"
            if self.kalan_can_suresi <= 0:
                self.canlar += 1
                self.kalan_can_suresi = self.can_yenilenme_suresi
                for ekran_adi in ["balon", "ari", "sekil", "bulmaca"]:
                    if not self.sm.has_screen(ekran_adi):
                        continue
                    scr = self.sm.get_screen(ekran_adi)
                    if hasattr(scr, "ust_panel") and scr.ust_panel:
                        scr.ust_panel.ses_guncelle()
        else:
            self.kalan_can_suresi = self.can_yenilenme_suresi


if __name__ == "__main__":
    MinikKasiflerApp().run()
