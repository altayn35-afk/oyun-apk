[app]

title = Minik Kasifler Atolyesi
package.name = minikkasifler
package.domain = org.minikkasifler
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .git

requirements = python3,kivy,gtts,kivmob,charset-normalizer,urllib3,idna,certifi,requests

version = 1.0.0
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# Kararli mimari ve NDK surumu
android.archs = armeabi-v7a
android.ndk = 25b
android.api = 33
android.minapi = 24

android.accept_sdk_license = True
android.release_artifact = apk

[buildozer]
log_level = 2
warn_root = 1
