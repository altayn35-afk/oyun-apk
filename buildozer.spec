[app]
title = Oyunum
package.name = oyunum
package.domain = org.oyun
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav
version = 0.1
requirements = python3==3.11.9,hostpython3==3.11.9,kivy==2.3.1,android,jnius,https://github.com/MichaelStott/KivMob/archive/refs/heads/master.zip
orientation = portrait
fullscreen = 1
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.minapi = 24
android.ndk_api = 24
android.api = 36
android.enable_androidx = True
android.gradle_dependencies = com.google.firebase:firebase-ads:23.6.0
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-4346547259367025~9465488099

[buildozer]
log_level = 2
warn_on_root = 1
