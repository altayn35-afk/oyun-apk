# 1.3.0 teslim doğrulaması — 18 Ekim 2026

## Geçen kontroller

- Python derleme kontrolü: uygulama modülleri, Android hook'u, test ve araç kodu.
- **45 otomatik test geçti.** Linux Kivy 2.3.1 / Python 3.12, SDL2 offscreen görüntü ve dummy ses sürücüsü kullanıldı. Bu bir Android emülatörü değildir.
- Tek ad alanı ve gerçek Başla eylemi; adın yeniden yüklenmesi; menüde dört oyun düğmesine gerçek Kivy dokunma olayı gönderilmesi.
- 320×568, 390×844 ve 600×960 boyutlarında menü/giriş metin ve dokunma alanları, kart sınırları ve başarılar kaydırması.
- Dört oyunda yeni oturumun puan/can/seviye sıfırlaması; menü çıkışında saatlerin iptali; Android yaşam döngüsü için ortak duraklatma/devam kod yolu; ekrandan taşınmayan efektler.
- Balon doğru/tehlikeli dokunma, delta-time hareketi, art arda iki seviye tamamlama, devam ve yıldız kaydı.
- Arı petek toplama, tehlike/can kaybı, seviye hedefi ve devam; parmağı yumuşak takip ve yeni oyunda hedefin sıfırlanması.
- Şekil doğru/yanlış seçim, seviye geçişi, duraklatılan süre ve sayaç sıfır olduğu anda can kaybı.
- Hayvan hafızasında ilk kartların kapalı olması, dört sütun, aynı hayvan eşleştirme, yanlış çiftte üçüncü dokunmanın kilitlenmesi, gerçek 0,7 saniye gecikme sonrası kapanma, can kaybı, çıkışta gecikmenin iptali, yeni seviyenin 12 kartla kapalı başlaması.
- Sonuçta gerçek canlara göre üç yıldız görseli; tekrar çift tıklamanın bonusu/ilerlemeyi çoğaltmaması; oyun bitti → tekrar oyna.
- Bozuk kayıttan güvenli varsayılanlara dönüş, sıfır başlangıç başarıları, en iyi puanın geriye gitmemesi, tamamlanma/yıldızların diskte korunması.
- Ses ve müzik tercihlerinin kalıcılığı; beş WAV dosyasının SDL2 ile çözülmesi; müzik seçeneğinin oynatmayı başlatması/durdurması. Dummy ses kullanıldığından hoparlörden işitsel dinleme yapılmadı.
- **63 varlığın tamamı** açıldı/doğrulandı: 52 RGBA PNG, 5 JPEG, 5 WAV, 1 TTF. PNG alpha, dosya yolu, Android uzantı listesi, font lisansı ve dosya sayısı kontrol edildi.
- Android hook API35 tema/Gradle ayarları, tekrar çalıştırma güvenliği, beklenmeyen şablonun reddi; filetype/chardet/Kivy gereksinimleri; eksik Python paketinin APK denetiminde reddi.

## Gerçek uygulama ekranlarının incelenmesi

Giriş → menü → dört oyun → hayvan eşleşmesi → seviye 3 tamamlanması → devam/duraklat → oyun bitti → ayarlar → başarılar yolları Kivy üzerinde işletildi. 320×568, 390×844, 600×960 ve 1080×2400 (density=3) boyutlarında toplam 52 ekran kaydı alındı. `dogrulama/ekranlar/` içinde boyuta göre ayrılmış, aktarım boyutu için JPEG olarak sıkıştırılmış gerçek framebuffer görüntüleri bulunur. Sonuçlar tasarım kolajı değildir.

Kart eşleşmeleri ve sonuç puanları renderer içinde oyun dokunma işleyicisiyle oluşur. Balon/arı görsellerini aynı anda incelemek için renderer geçici oyun nesnelerinin konumlarını belirler; bu anlık görsel kontrol nesneleri başlangıç kayıtlarına veya gerçek başarı verisine yazılmaz. Bütün kayıtlar test için geçici dizindedir. Renderer kullanıcı kaydını değiştirmez.

## Android'e özgü kanıt

Paylaşılmış gerçek cihaz logu, Kivy başlangıcında eksik `filetype` modülünü gösteriyor. Kaynak gereksinimi düzeltildi. Güncellenen APK kontrolü eski 1.2.1 tanı APK'sını iki ABI'de de aynı eksik modül nedeniyle reddetti (230 ELF tarandı). Bu negatif testin çıktısı ayrıca pakettedir; yeni APK üretildiği anlamına gelmez.

## Tamamlanamayan doğrulamalar

- Buildozer android debug denemesi `javac` eksikliğinde durdu. JDK/native araç kurma girişimi ortamın apt kullanıcı/önbellek izinlerine takıldı. SDK/NDK ile temiz tam Android derlemesi tamamlanmadı.
- Yeni APK/AAB üretilmedi; önceki APK paket içine eklenmedi.
- Bu sürüm gerçek Samsung telefonunda veya Android emülatöründe çalıştırılmadı. Kaynaktaki düzeltmenin telefonda başarılı açılışı sağladığı henüz doğrulanmış değildir.
- GitHub Actions uzakta tetiklenmedi; YAML ve yerel kontrol kodu doğrulandı. Eklenen CI oyun testi adımının uzak koşusu yapılmadı.
- Gerçek telefonun klavye açılması, dokunma gecikmesi, hoparlör sesi, sistem çubukları ve GPU performansı bu Linux testleriyle doğrulanamaz.
- Referansların sanat dili, iki sütunlu menü ve dört sütunlu hafıza düzeni uygulandı; ekranlar referans görsellerin birebir piksel kopyası değildir. Beş net arka plan önceki geliştirmeden korundu; uçan arı ve menü yüzeyleri bu çalışmada yenilendi.

Bu paket, tamamlanan proje dosyalarının tek teslimatıdır. Kurulum veya GitHub değişikliği talebi içermez.
