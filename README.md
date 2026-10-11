<h1 align="center">
  <img src="core/icon.png" width="64" alt="SemeryFiles">
  <br>
  SemeryFiles
</h1>

<p align="center">
  <b>Инструменты для работы с файлами</b><br>
  Анализ, хеширование, метаданные, сравнение, поиск дубликатов
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue">
  <img src="https://img.shields.io/badge/python-3.10+-green">
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey">
  <img src="https://img.shields.io/badge/license-MIT-green">
</p>

---

> [!NOTE]
> SemeryFiles — это лёгкое десктопное приложение на Python + PySide6.
> Работает офлайн, не отправляет данные никуда.

> [!IMPORTANT]
> Приложение **не выполняет** код из файлов. Оно только читает,
> анализирует и конвертирует. Безопасно запускать на любых файлах.

> [!WARNING]
> При работе с большими файлами (несколько гигабайт) расчёт хешей
> может занимать длительное время. Интерфейс не блокируется —
> операция идёт в фоне.

## Возможности

- ℹ **Информация о файле** — размер, тип, даты, права
- # **Хеширование** — SHA-256, SHA-512, MD5, BLAKE3
- ☷ **Метаданные** — EXIF, ID3, PDF, Office
- ▦ **Hex-просмотр** — содержимое в hex
- ⇋ **Конвертация** — кодировки, форматы, base64
- ⚿ **Права доступа** — Unix/Windows
- .* **Regex-тестер** — поиск и замена
- ▤ **SQLite Viewer** — просмотр и редактирование баз
- ⚷ **Генератор паролей** — пароли, UUID, фразы
- ƒ **Просмотр шрифтов** — TTF, OTF, TTC, WOFF
- ⌦ **Санитайзер EXIF** — удаление GPS и метаданных
- ▩ **QR-коды** — генерация и декодирование
- ◐ **Стеганография** — скрытие данных в PNG

## Установка

Скачайте последний релиз со страницы [Releases](https://github.com/.../releases).

Или соберите из исходников:

```bash
git clone https://github.com/.../SemeryFiles.git
cd SemeryFiles
pip install -r requirements.txt
python main.py
