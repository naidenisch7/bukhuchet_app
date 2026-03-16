[app]

# Title of your application
title = Бухучет

# Package name (no spaces, no special chars)
package.name = bukhuchet

# Package domain (for android/ios package identifier)
package.domain = org.bukhuchet

# Source directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,txt,db

# Source files to exclude
source.exclude_dirs = __pycache__,.git,bin,.buildozer

# Application versioning
version = 1.0.0

# Application requirements
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,openpyxl,pyjnius,android,materialyoucolor,exceptiongroup,asyncgui,asynckivy

# Supported orientations (portrait, landscape, all)
orientation = portrait

# Android specific
fullscreen = 0

# Android API level
android.api = 33

# Minimum Android API
android.minapi = 21

# Android NDK API
android.ndk_api = 21

# Android SDK
android.sdk = 33

# Android NDK version
android.ndk = 25b

# Android permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android architecture
android.archs = arm64-v8a,armeabi-v7a

# Accept SDK license automatically
android.accept_sdk_license = True

# Android Gradle dependencies (none needed)
# android.gradle_dependencies =

# Presplash color (dark theme)
android.presplash_color = #1F1F24

# Icon
# icon.filename = %(source.dir)s/icon.png

# Presplash image
# presplash.filename = %(source.dir)s/presplash.png

# Log level (2 = warning)
log_level = 2

# Copy libraries instead of making a reference
# android.copy_libs = 1

# p4a branch
p4a.branch = master

# Bootstrap
p4a.bootstrap = sdl2

[buildozer]

# Build artifact directory
# build_dir = ./.buildozer

# Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
