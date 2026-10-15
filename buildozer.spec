[app]

# (str) Title of your application
title = Minik Kasifler Atolyesi

# (str) Package name
package.name = minikkasifler

# (str) Package domain (needed for android packaging)
package.domain = org.minikkasifler

# (str) Source where the source code is located
source.dir = .

# (list) Source files to include (let it empty to include all files)
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

# (list) Source files to exclude (let it empty to exclude nothing)
source.exclude_exts = spec

# (list) List of directory to exclude (let it empty to exclude nothing)
source.exclude_dirs = tests, bin, .git

# (list) Application requirements
requirements = python3,kivy,gtts,kivmob,charset-normalizer,urllib3,idna,certifi,requests

# (str) Version of your application
version = 1.0.0

# (str) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (list) The Android archs to build for
android.archs = arm64-v8a, armeabi-v7a

# Android SDK lisanslarini otomatik kabul et
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_root = 1
