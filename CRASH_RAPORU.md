# Android başlangıç hatası

18 Ekim 2026 tarihli erişilebilir `oyun_hatasi.txt` gerçek cihaz kaydı incelendi. Kişisel ve diğer uygulamalara ait satırlar teslim paketine alınmadı. İlgili bölüm:

```text
[MinikStartup] UNCAUGHT PYTHON EXCEPTION
File "main.py", line 14, in <module>
... kivy/app.py
... kivy/uix/widget.py
... kivy/graphics/...
... kivy/core/image/__init__.py, line 65
ModuleNotFoundError: No module named 'filetype'
Python for android ended.
```

Bu kayıttaki Python başlangıcını durduran neden `filetype` paketinin bulunmamasıdır. Giriş ekranı oluşturulmadan Kivy içe aktarılırken hata oluşur. Masaüstünde pip Kivy'nin bağımlılığını otomatik yüklediği için yalnızca masaüstü açılış testi bu APK eksikliğini yakalayamıyordu.

## Kaynaktaki düzeltme

`buildozer.spec` gereksinimlerine `filetype==1.2.0` açıkça eklendi. Python 3.11.5, Kivy 2.3.1 ve önceki `chardet==5.2.0` sabitlemeleri korunmuştur. Başlangıç günlüklemesi korunup sürüm 1.3.0 olarak güncellendi. Hook dosyası ve API35 pencere teması değişmedi.

`tools/audit_apk.py` artık her ARM ABI içindeki Python arşivinde `kivy`, `filetype`, `chardet` paketlerini de arar. Önceki 1.2.1 tanı APK'sına bu yeni kontrol uygulandı: 230 ELF dosyası tarandı, iki ABI için de `missing Python package filetype` hatası bulundu. Bu, yeni denetimin gerçek kusurlu APK'yı reddettiğini gösterir; eski APK'nın çalıştığı varsayılmaz.

GitHub Actions APK çıktısını yüklemeden önce bu denetimi çalıştırır. Gereksinim satırı ve eksik paket reddi otomatik testlerle korunur.

## Doğrulamanın sınırı

Yeni kaynakta bağımlılık düzeltildi ve masaüstü testleri geçti. **Yeni ARM APK üretimi tamamlanmadı ve bu sürüm Samsung cihazda/emülatörde çalıştırılmadı.** Dolayısıyla telefon açılışının başarıyla doğrulandığı veya başka Android hatalarının bulunmadığı iddia edilmiyor. İlerideki Android doğrulaması, temiz kaynak derlemesi ve cihaz açılış kaydı gerektirir. Bu aşamada kullanıcıdan yeni kurulum istenmiyor.
