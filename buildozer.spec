[app]
title = Minik Kaşifler Atölyesi
package.name = oyunum
package.domain = org.oyun
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,ttf,txt
source.exclude_dirs = tests,tools,bin,.git,.buildozer,__pycache__,dogrulama,android_apk
version = 1.4.2
android.numeric_version = 10246
requirements = python3==3.11.5,hostpython3==3.11.5,kivy==2.3.1,chardet==5.2.0,filetype==1.2.0
p4a.branch = v2026.05.09
p4a.hook = android_build_hook.py
orientation = portrait
fullscreen = 0
presplash.filename = assets/acilis_ekrani_bos.png
android.archs = arm64-v8a,armeabi-v7a
android.api = 36
android.minapi = 24
android.ndk = 28c
android.accept_sdk_license = True
android.release_artifact = aab

[app@tani]
title = Minik Kaşifler Tanı
package.name = minikkasiflertani

[buildozer]
log_level = 2
warn_root = 1
