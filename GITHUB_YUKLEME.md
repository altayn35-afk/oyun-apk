# Gelecek Android derlemesi için başvuru

Şu anda GitHub değişikliği veya APK kurulumu yapılması gerekmiyor. Aşağıdaki bilgiler ileride Android derleme aşamasına geçildiğinde kullanılmak üzere pakete dahildir.

ZIP'in içindeki `Minik_Kasifler_Atolyesi_1_3` klasörü proje köküdür. Gelecekteki aktarımda `main.py`, diğer kök Python modülleri, `assets/`, `tests/`, `tools/`, `buildozer.spec`, `android_build_hook.py`, `requirements-dev.txt`, `build_android.sh`, `.gitignore` ve özellikle gizli `.github/workflows/build.yml` dosyası birlikte korunmalıdır. ZIP klasörünü depoda bir alt klasöre koyup proje kökünü eski bırakmak doğru değildir. Önceki dosyalar yedeklenebilir; kişisel oyuncu kaydı kaynak paketine taşınmamalıdır.

Mevcut depoya bu oturumda hiçbir dosya gönderilmedi ve Actions tetiklenmedi. Karşılaştırılan GitHub HEAD: `f1c14f0363b609408591bda0bfa378945dd130b5`. Depodaki eski tek dosyalı sürüm yerine önceki 1.2.1 çok modüllü geliştirme tabanı sürdürüldü. Önceki geliştirmedeki sabitlenmiş p4a/NDK/API ve Android hook zinciri korundu; gerekli filetype bağımlılığı, sürüm ve ek test adımı güncellendi.

Derleme zinciri: Ubuntu 22.04, Java 17, Buildozer 1.5.0, Cython 0.29.36, Python-for-Android v2024.01.21 sabit commit, hedef Python 3.11.5 / Kivy 2.3.1, NDK25b, minAPI24 / API35, ARM64 ve ARMv7. Hook üretilen şablonda AGP8.6.0 / Gradle8.7 / BuildTools35.0.0 ayarlar; beklenmeyen şablonda sessiz değişiklik yapmak yerine hata verir.

Tam araçları kurulu Linux ortamında kaynak derleme komutu `bash build_android.sh` olur. APK üretiminden sonra `python tools/audit_apk.py bin/DOSYA.apk` kontrolü yapılmalıdır. CI aynı kontrolü çalıştırır. APK üretimi ve bu sürümün gerçek cihaz testi bu teslimatta tamamlanmış değildir.
