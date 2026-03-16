#!/bin/bash
# Скрипт для установки Buildozer и сборки APK в WSL Ubuntu
# Запускать из WSL: bash /mnt/c/Users/naidenisch/Desktop/бухучет_app/build_apk.sh

set -e

APP_DIR="/mnt/c/Users/naidenisch/Desktop/бухучет_app"
BUILD_DIR="$HOME/bukhuchet_build"

echo "=== 1. Обновление системы ==="
sudo apt update && sudo apt upgrade -y

echo "=== 2. Установка зависимостей для Buildozer ==="
sudo apt install -y \
    python3 python3-pip python3-venv \
    git zip unzip \
    openjdk-17-jdk \
    autoconf automake libtool \
    libffi-dev libssl-dev \
    build-essential \
    cmake \
    libncurses5 \
    zlib1g-dev \
    pkg-config \
    libsqlite3-dev \
    lld

echo "=== 3. Создание рабочей директории ==="
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"
cp -r "$APP_DIR"/*.py "$BUILD_DIR/"
cp -r "$APP_DIR"/screens "$BUILD_DIR/"
cp "$APP_DIR"/buildozer.spec "$BUILD_DIR/"
# Exclude __pycache__ and .db files
find "$BUILD_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.db" -delete 2>/dev/null || true

echo "=== 4. Создание виртуального окружения ==="
cd "$BUILD_DIR"
python3 -m venv venv
source venv/bin/activate

echo "=== 5. Установка Buildozer и Cython ==="
pip install --upgrade pip setuptools wheel
pip install buildozer cython==3.0.11

echo "=== 6. Сборка APK (debug) ==="
cd "$BUILD_DIR"
buildozer android debug 2>&1 | tee build.log

echo ""
echo "=== ГОТОВО ==="
APK_PATH=$(find "$BUILD_DIR/bin" -name "*.apk" 2>/dev/null | head -1)
if [ -n "$APK_PATH" ]; then
    cp "$APK_PATH" "$APP_DIR/"
    echo "APK скопирован: $APP_DIR/$(basename $APK_PATH)"
    echo "Установите на телефон через adb:"
    echo "  adb install $(basename $APK_PATH)"
else
    echo "ОШИБКА: APK не найден. Смотри build.log"
fi
