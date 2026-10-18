# Görsel ve ses varlıkları

Yeni görseller yerleşik imagegen aracıyla bu oyun için üretildi. Oyun ekranı görüntülerinden kırpılmış veya bulanıklaştırılmış zeminler kullanılmıyor. Görsellerde oyun adı, örnek puan veya sahte başarı istatistiği yoktur. Başlıklar ve etkileşimler Kivy widget'larıdır.

24 ayrı kaynak üretimi:

- 5 dikey sahne: güneşli çayır; çiçekli, ağaçlı ve kovanlı orman; iki sevimli kaşif çocuklu doğa sahnesi; şekiller için ağaç ev oyuncak atölyesi; hafıza oyunu için lavanta renkli orman kulübü.
- 8 hayvan: aslan, panda, kurbağa, tilki, fil, maymun, zürafa ve penguen.
- 4 kabartmalı oyuncak şekil: daire, kare, üçgen, beş köşeli yıldız.
- 7 diğer varlık: kırmızı balon; kafataslı tehlike balonu; arı; bal peteği; kovan; mor soru işaretli kart arkası; yeşil düğme yüzeyi.

Ortak istem: “Premium polished glossy volumetric 3D cartoon toy style, expressive child-friendly characters, consistent warm studio/sun lighting, whole standalone object centered, no text, no watermark.” Karakter ve nesneler şeffaf arka planla; sahneler açık oyun alanı bırakacak biçimde üretildi. Tehlike balonunda kafatası, kart arkasında yalnızca soru işareti istendi.

Kaynak görseller kenar boşlukları temizlenerek optimize edildi. Renk varyantları, üretilen hacim ve parlaklığı koruyan malzeme tonu dönüşümüyle ayrı PNG'lere dönüştürüldü. Balonlar altı, şekiller altı, düğmeler beş renktir. Çalışma zamanında Pillow veya NumPy gerekmez.

- Zeminler: 864×1296 JPEG; en/boy oranı korunarak ekranı kaplar, telefon oranına göre kenarlardan bir miktar kesilebilir.
- Balonlar: 256×384 RGBA PNG.
- Şekiller: 320×320 RGBA PNG.
- Hayvanlar, arı, kovan ve petek: 384×384 RGBA PNG.
- Kart arkası: 288×352 RGBA PNG.
- Düğmeler: 576×192 RGBA PNG.
- Yazı tipi: Türkçe karakter destekli DejaVu Sans; lisansı ayrıca sunuldu.
- Dört kısa efekt ve sekiz saniyelik döngü müziği bu paket için sentezlendi: mono, 22050 Hz, 16 bit PCM WAV.

Toplam 63 çalışma zamanı varlığı: 52 şeffaf PNG, 5 JPEG zemin, 5 WAV ve 1 TTF. Nesneler gerçek oyun kodunda ayrı dokular olarak yüklenir ve önbelleğe alınır. Önceki ekranların bulanık varlıkları son paketten çıkarıldı.


## 1.3.0 görsel ekleri

Yerleşik imagegen ile iki yeni bağımsız kaynak üretildi; ekran kolajı üretilmedi. Optimize edilmiş çalışma zamanı dosyaları `assets/ari_karakter.png` ve `assets/tile.png` olarak kaydedildi; kare menü kartının turuncu, pembe ve mor malzeme tonları `assets/tile_orange.png`, `assets/tile_pink.png`, `assets/tile_purple.png` dosyalarındadır. Arı 384×384; kart yüzeyleri 528×528 RGBA'dır. Alpha korunmuştur. Önceki ayakta arının yerine uçan arı kullanılır. Kare kart PNG'leri yalnız menüde, ayrı düğme PNG'leri eylemlerde kullanılır.

Arı üretim istemi: “Standalone transparent PNG sprite for a preschool mobile honey collecting game. Adorable plump flying bee, round golden yellow body with black stripes, large expressive eyes, joyful smile, curved antennae, translucent pearly wings, tucked legs. Three-quarter view facing right, hovering, whole body visible. Premium glossy volumetric 3D cartoon toy, soft sunlit highlights, crisp silhouette at 100 pixels. No ground, no scene, no text, no watermark, no motion blur.”

Kare kart üretim istemi: “Reusable standalone mobile game menu tile skin, transparent square PNG. Glossy blue rounded-square chunky 3D cartoon toy tile, front-on orthographic, beveled frame with cyan edge highlights, sapphire center, generous empty middle, warm studio lighting. No icon, symbol, writing, numbers, character, background or scene.”

Referanslar: erişilen Minik Kaşifler oyun arayüzü kolajları ve WhatsApp 16 Ekim referansı düzen/sanat yönünü anlamak için incelendi. Bu kolajlar çalışma zamanı arka planı olarak kullanılmadı. 18 Ekim tarihli bazı ek görüntüler teknik konsol/GitHub görüntüleriydi. Bütün eski konuşma dosyalarına erişildiği iddia edilmiyor.
