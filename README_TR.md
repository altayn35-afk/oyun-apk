# Minik Kaşifler Atölyesi — 1.3.0

Bu paket dört oyunun kaynak kodunu, kullanılan ayrı görsel ve ses dosyalarını, Android derleme yapılandırmasını, testleri ve gerçek Kivy ekran kayıtlarını içerir. Giriş, ana menü, dört oyun, sonuç, duraklatma, ayarlar ve başarılar ekranları uygulamada bağlıdır.

**Bu teslimat proje dosyaları içindir. Yeni APK içermez. GitHub'a yükleme veya telefona kurulum yapmanız şu aşamada istenmiyor.** Android derlemesi bu ortamda tamamlanamadı; gerçek cihazda bu sürüm test edilmedi. Ayrıntılar TEST_RAPORU.md ve CRASH_RAPORU.md içindedir.

## Paket düzeni

- main.py: mevcut dört oyunun kuralları, çizimi ve ortak yaşam döngüsü.
- interface.py: giriş, iki sütunlu menü, başarılar, ayarlar ve sonuç pencereleri.
- storage.py: uygulamanın kendi veri alanına atomik oyuncu kaydı.
- startup_diagnostics.py: Kivy yüklenmeden önce başlayan hata kaydı.
- assets/: 63 gerçek çalışma zamanı varlığı; metin ve örnek istatistik gömülü ekran kolajı yoktur.
- buildozer.spec, android_build_hook.py, build_android.sh ve .github/workflows/build.yml: Android yapılandırması.
- tests/: oyun, kayıt, dokunma, boyutlandırma, ses, paketleme ve başlangıç testleri.
- tools/audit_apk.py: ARM mimarilerini ve kritik Python paketlerini APK içinde denetler.
- tools/render_screens.py: geçici kayıt kullanarak gerçek Kivy ekranlarını üretir.
- dogrulama/: test çıktıları ve Linux üzerinde alınmış ekran görüntüleri. Bunlar Android ekran görüntüsü değildir.

## Bilgisayarda çalıştırma ve doğrulama

Python 3.10 veya üzeri ile:

```sh
python -m pip install -r requirements-dev.txt
python main.py
```

Linux'ta görüntüsüz test:

```sh
SDL_VIDEODRIVER=offscreen SDL_AUDIODRIVER=dummy KIVY_NO_ARGS=1 python -m unittest discover -s tests -v
python tests/verify_assets.py
python -m compileall -q main.py interface.py storage.py startup_diagnostics.py android_build_hook.py
```

## Oynanış

- Balon: normal balon +10 puan; her 50 puan bir seviye. Kuru kafalı balon ve kaçırılan normal balon bir can götürür.
- Arı: ekrana dokunup sürükleyerek arıyı yukarı/aşağı yönlendir. Petek +10; seviye hedefi 5 + seviye petek; bitirme bonusu +30. Kuru kafa bir can götürür; ardından kısa koruma süresi vardır.
- Şekiller: üstteki renk/şekil örneğini bul. Doğru nesne +10, bitirme +30. Yanlış seçim veya süre sonu bir can götürür.
- Süper Bulmaca: dört sütunda 4, 6 ve 8 çift hayvan. Eşleşme +15; bitirme +40. Yanlış çift 0,7 saniye sonra kapanır ve bir can götürür. Kapalı kartlar mor soru işaretlidir; eşleşenler yeşil çerçeve alır.
- Her oyun üç canla başlar. Tamamlanan seviyenin yıldızı kalan can sayısıdır (1–3). Tekrar Oyna yeni oturumu başlatır; kazanılmış en iyi puanlar silinmez.

Ad, ses ve müzik tercihleri, oyun bazında en iyi puan, tamamlanan seviye, tamamlanma ve yıldız toplamları yerel kayıttan gelir. İlk açılışta başarılar sıfırdır. Reklam ve reklamla can kazanma yoktur. Ayarlardaki iki ses seçeneği gerçek ses oynatımını kontrol eder. Klavye Enter tuşu da mevcut Başla eylemini çalıştırır.

Android hazırlığına ilişkin isteğe bağlı gelecek başvuru belgesi: GITHUB_YUKLEME.md. Bu teslimat herhangi bir uzaktaki depoyu değiştirmez.
