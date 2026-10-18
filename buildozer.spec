[app]
title = Minik Kaşifler Atölyesi
package.name = oyunum
package.domain = org.oyun
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,ttf,txt
source.exclude_dirs = tests,tools,bin,.git,.buildozer,__pycache__,dogrulama,android_apk
version = 1.4.0
android.numeric_version = 2
requirements = python3==3.11.5,kivy==2.3.1,chardet==5.2.0,filetype==1.2.0
p4a.branch = v2024.01.21
p4a.commit = 957a3e5f8c270f7aa648ba185e5a68c1077a798d
p4a.hook = android_build_hook.py
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a,armeabi-v7a
android.api = 35
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.release_artifact = apk

[app@tani]
title = Minik Kaşifler Tanı
package.name = minikkasiflertani

[buildozer]
log_level = 2
warn_root = 1
