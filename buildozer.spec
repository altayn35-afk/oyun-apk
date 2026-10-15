[app]

# (str) Title of your application
title = Minik Kasifler Atolyesi

# (str) Package name
package.name = minikkasifler

# (str) Package domain (needed for android packaging)
package.domain = org.minikkasifler

# (list) Source files to include (let it empty to include all files)
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

# (list) Source files to exclude (let it empty to exclude nothing)
source.exclude_exts = spec

# (list) List of directory to exclude (let it empty to exclude nothing)
source.exclude_dirs = tests, bin, .git

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,gtts,kivmob,charset-normalizer,urllib3,idna,certifi,requests

# (str) Supported orientations
orientation = portrait

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (str) Supported orientations (portrait, landscape)
osx.python_version = 3
osx.kivy_version = 1.9.1

# (list) The Android archs to build for,, can be armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# Android SDK lisanslarini otomatik kabul et (Hatanin cozumu burasi)
android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_root = 1
