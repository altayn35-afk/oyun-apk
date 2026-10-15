[app]

title = Minik Kasifler Atolyesi
package.name = minikkasifler
package.domain = org.minikkasifler
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .git

# Sadece temel ve kararli gereksinimler
requirements = python3,kivy,gtts,charset-normalizer,urllib3,idna,certifi,requests

version = 1.0.0
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# Çökme riskini azaltmak için tek mimari (armeabi-v7a)
android.archs = armeabi-v7a

android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_root = 1
