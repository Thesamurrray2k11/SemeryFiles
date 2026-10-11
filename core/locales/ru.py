LANGUAGE_CODE = "ru"
LANGUAGE_NAME = "Русский"
LANGUAGE_NAME_EN = "Russian"

LOCALE = "ru_RU"

TRANSLATIONS = {
    "app.name":              "SemeryFiles",
    "app.version":           "0.1.0",
    "app.tagline":           "Инструменты для работы с файлами",

    "settings.title":        "Настройки",
    "settings.subtitle":     "Изменения применяются сразу.",

    "settings.theme":          "Тема оформления",
    "settings.theme.light":    "Светлая",
    "settings.theme.dark":     "Тёмная",
    "settings.theme.hint":     "Обе темы приглушённые — без резких контрастов.",

    "settings.remember_theme":      "Запоминать тему",
    "settings.remember_theme.hint": "Сохранять выбор между запусками.",

    "settings.section.appearance":  "Внешний вид",
    "settings.section.files":       "Файлы",
    "settings.section.format":      "Формат",

    "settings.dirs":          "Папки",
    "settings.default_dir":   "Папка по умолчанию",
    "settings.default_dir.hint": "Откуда открывать диалоги выбора файлов.",
    "settings.reports_dir":   "Папка для отчётов",
    "settings.reports_dir.hint": "Куда сохранять экспортированные отчёты.",
    "settings.browse":        "Обзор…",
    "settings.system_default":"По умолчанию системы",

    "settings.language":      "Язык интерфейса",

    "settings.units":         "Размерности",
    "settings.units.hint":    "KB = 1000 байт, KiB = 1024 байта.",
    "settings.units.binary":  "KiB / MiB / GiB",
    "settings.units.decimal": "KB / MB / GB",

    "settings.reset":         "Сбросить",
    "settings.github.tip":    "Страница проекта — исходный код, обновления, баг-трекер.",
    "settings.telegram.tip":  "Связь с разработчиком — вопросы, идеи, ошибки.",

    "home.title":             "SemeryFiles",
    "home.version_prefix":    "ВЕРСИЯ",
    "home.desc":              "Набор инструментов для разработчиков и всех, кто "
                              "работает с файлами. Анализ, хеширование, "
                              "метаданные, сравнение, поиск дубликатов — "
                              "в одном лёгком приложении.",
    "home.hint":              "Выберите инструмент на панели слева  •  или откройте поиск ⌘",

    "common.browse":          "Выбрать файл…",
    "common.drop_hint":       "Перетащите файл сюда или нажмите, чтобы выбрать",
    "common.empty":           "Файл не выбран",
    "common.error":           "Ошибка",
    "common.apply":           "Применить",
    "common.cancel":          "Отмена",
    "common.save":            "Сохранить",
    "common.open":            "Открыть",
    "common.close":           "Закрыть",
    "common.copy":            "Копировать",
    "common.copied":          "Скопировано",
    "common.done":            "Готово",

    "info.title":       "Информация о файле",
    "info.browse":      "Выбрать файл…",
    "info.drop_hint":   "Перетащите файл сюда или нажмите, чтобы выбрать",
    "info.empty":       "Файл не выбран",
    "info.error":       "Ошибка",

    "info.group.general":     "ОБЩЕЕ",
    "info.group.dates":       "ДАТЫ",
    "info.group.permissions": "ПРАВА ДОСТУПА",
    "info.group.hashes":      "ХЕШИ",

    "info.field.name":        "Имя",
    "info.field.path":        "Полный путь",
    "info.field.size":        "Размер",
    "info.field.size_bytes":  "Размер (байт)",
    "info.field.type_mime":   "MIME-тип",
    "info.field.type_ext":    "Расширение",
    "info.field.type_magic":  "Тип по сигнатуре",
    "info.field.created":     "Создан",
    "info.field.modified":    "Изменён",
    "info.field.accessed":    "Открыт",
    "info.field.permissions": "Права",
    "info.field.mode_octal":  "Режим (octal)",
    "info.field.readonly":    "Только чтение",

    "hash.title":       "Хеширование",
    "hash.browse":      "Выбрать файл…",
    "hash.drop_hint":   "Перетащите файл сюда или нажмите, чтобы выбрать",
    "hash.algorithms":  "АЛГОРИТМЫ",
    "hash.copy":        "Копировать",
    "hash.export":      "Экспорт",
    "hash.need_algo":   "Выберите хотя бы один алгоритм",
    "hash.error":       "Ошибка",

    "meta.title":       "Метаданные",
    "meta.browse":      "Выбрать фото…",
    "meta.drop_hint":   "Перетащите фото сюда или нажмите, чтобы выбрать\n"
                        "(JPG, PNG, WEBP, TIFF, BMP, GIF, HEIC)",
    "meta.empty":       "Файл не выбран",
    "meta.no_metadata": "Метаданные не найдены",
    "meta.no_exif":     "В этом файле нет EXIF-данных.\n"
                        "Возможные причины: фото сделано скриншотом, "
                        "прошло через мессенджер (Telegram, WhatsApp) "
                        "или экспортировано без метаданных.",
    "meta.only_images": "Поддерживаются только изображения",
    "meta.error":       "Ошибка",
    "meta.open_map":    "🗺  Открыть на карте",
    "meta.copy_coords": "⧉  Скопировать координаты",

    "meta.err.file_not_found": "Файл не найден",
    "meta.err.not_image":      "Это не изображение",
    "meta.err.no_pillow":      "Не установлена библиотека Pillow",

    "meta.group.general":     "ОБЩЕЕ",
    "meta.group.camera":      "КАМЕРА",
    "meta.group.shooting":    "ПАРАМЕТРЫ СЪЁМКИ",
    "meta.group.datetime":    "ДАТЫ",
    "meta.group.exif_other":  "ПРОЧЕЕ EXIF",
    "meta.group.gps":         "ГЕОЛОКАЦИЯ",

    "convert.title":        "Конвертация",
    "convert.browse":       "Выбрать файл…",
    "convert.drop_hint":    "Перетащите файл сюда или нажмите, чтобы выбрать",
    "convert.no_file":      "Файл не выбран",
    "convert.action":       "ДЕЙСТВИЕ",
    "convert.action.encoding":  "Смена кодировки текста",
    "convert.action.b64_enc":   "Кодировать в Base64",
    "convert.action.b64_dec":   "Декодировать из Base64",
    "convert.action.line_end":  "Заменить окончания строк",
    "convert.action.image":     "Конвертировать изображение",

    "convert.src_enc":      "Исходная кодировка",
    "convert.dst_enc":      "Целевая кодировка",
    "convert.line_target":  "Целевые окончания",
    "convert.img_format":   "Формат",
    "convert.img_quality":  "Качество",

    "convert.run":          "Конвертировать",
    "convert.save_as":      "Сохранить как…",
    "convert.done":         "Готово",
    "convert.error":        "Ошибка",

    "hex.title":       "Hex-просмотр",
    "hex.browse":      "Выбрать файл…",
    "hex.drop_hint":   "Перетащите файл сюда или нажмите, чтобы выбрать",
    "hex.offset":      "Позиция:",
    "hex.go":          "Перейти",
    "hex.width":       "Ширина:",
    "hex.page":        "Страница:",
    "hex.find":        "Найти",
    "hex.prev":        "Назад",
    "hex.next":        "Вперёд",
    "hex.showing":     "Показано",
    "hex.end_of_file": "Конец файла",
    "hex.error":       "Ошибка",
    "hex.bad_pattern": "Некорректный hex-паттерн",
    "hex.not_found":   "Не найдено",
    "hex.found_more":  "Найдено вхождений",

    "hex.mode.hex":    "Hex",
    "hex.mode.ascii":  "ASCII",

    "perm.title":       "Права доступа",
    "perm.browse":      "Выбрать файл…",
    "perm.drop_hint":   "Перетащите файл сюда или нажмите, чтобы выбрать",
    "perm.no_file":     "Файл не выбран",
    "perm.unix":        "ПРАВА UNIX (rwx)",
    "perm.win":         "АТРИБУТЫ WINDOWS",
    "perm.col.owner":   "Владелец",
    "perm.col.group":   "Группа",
    "perm.col.other":   "Остальные",
    "perm.row.read":    "Чтение (r)",
    "perm.row.write":   "Запись (w)",
    "perm.row.exec":    "Запуск (x)",
    "perm.octal":       "Восьмерично:",
    "perm.apply":       "Применить",
    "perm.done":        "Права применены",
    "perm.error":       "Ошибка",
    "perm.bad_octal":   "Некорректное восьмеричное значение",

    "perm.win.readonly": "Только чтение",
    "perm.win.hidden":   "Скрытый",
    "perm.win.system":   "Системный",
    "perm.win.archive":  "Архивный",

    "regex.title":       "Regex-тестер",
    "regex.browse":      "Открыть файл…",
    "regex.drop_hint":   "Перетащите текстовый файл сюда или нажмите, чтобы выбрать",
    "regex.pattern_hint":"Введите регулярное выражение…",
    "regex.source":      "ИСХОДНЫЙ ТЕКСТ",
    "regex.source_hint": "Введите текст сюда или откройте файл",
    "regex.matches":     "СОВПАДЕНИЯ",
    "regex.replacement": "ЗАМЕНА:",
    "regex.replace_preview_hint": "Превью результата появится здесь",
    "regex.copy_result":  "⧉  Копировать результат",
    "regex.save_result":  "💾  Сохранить как…",
    "regex.tab.matches":  "Совпадения",
    "regex.tab.replace":  "Замена",
    "regex.tab.help":     "Подсказка",
    "regex.col.pos":      "Позиция",
    "regex.col.len":      "Длина",
    "regex.col.text":     "Текст",
    "regex.col.groups":   "Группы",
    "regex.info":         "Найдено: {count}   •   Групп: {groups}   •   Именованных: {named}",
    "regex.info_replace": "Замен: {count}",
    "regex.bad_pattern":  "Некорректный паттерн",
    "regex.error":        "Ошибка",

    "regex.help_text": (
        "<b>Основы синтаксиса</b><br>"
        "<code>.</code> — любой символ (кроме перевода строки)<br>"
        "<code>\\d</code> — цифра, <code>\\w</code> — буква/цифра/_, <code>\\s</code> — пробел<br>"
        "<code>\\D</code>, <code>\\W</code>, <code>\\S</code> — отрицание<br>"
        "<code>[abc]</code> — один из символов, <code>[^abc]</code> — кроме них<br>"
        "<code>[a-z]</code> — диапазон, <code>[0-9A-F]</code> — hex<br>"
        "<br>"
        "<b>Квантификаторы</b><br>"
        "<code>*</code> — 0 или больше, <code>+</code> — 1 или больше, <code>?</code> — 0 или 1<br>"
        "<code>{n}</code> — ровно n, <code>{n,m}</code> — от n до m<br>"
        "<code>*?</code>, <code>+?</code> — ленивые (минимум символов)<br>"
        "<br>"
        "<b>Группы</b><br>"
        "<code>(abc)</code> — захватывающая группа<br>"
        "<code>(?:abc)</code> — незахватывающая<br>"
        "<code>(?P&lt;name&gt;abc)</code> — именованная<br>"
        "<code>(?=abc)</code> — опережающая проверка<br>"
        "<code>(?&lt;=abc)</code> — ретроспективная проверка<br>"
        "<br>"
        "<b>Якоря</b><br>"
        "<code>^</code> — начало строки, <code>$</code> — конец строки<br>"
        "<code>\\b</code> — граница слова, <code>\\B</code> — не граница<br>"
        "<br>"
        "<b>Замена</b><br>"
        "<code>\\1</code>, <code>\\2</code> — ссылки на группы<br>"
        "<code>\\g&lt;name&gt;</code> — на именованную группу<br>"
        "<code>\\n</code>, <code>\\t</code> — перевод строки, таб<br>"
    ),

    "enc.title":       "Определение кодировки",
    "enc.browse":      "Выбрать файл…",
    "enc.drop_hint":   "Перетащите текстовый файл сюда или нажмите, чтобы выбрать",
    "enc.no_file":     "Файл не выбран",
    "enc.preview":     "ПРЕВЬЮ ТЕКСТА",
    "enc.confidence":  "Уверенность",
    "enc.convert_to":  "Перекодировать в:",
    "enc.convert":     "Перекодировать",
    "enc.save_as":     "Сохранить как…",
    "enc.done":        "Файл перекодирован",
    "enc.error":       "Ошибка",

    "sqlite.title":     "SQLite Viewer",
    "sqlite.browse":    "Открыть базу…",
    "sqlite.drop_hint": "Перетащите файл .db / .sqlite / .sqlite3 или нажмите, чтобы выбрать",
    "sqlite.tables":    "ТАБЛИЦЫ",
    "sqlite.tab.data":  "Данные",
    "sqlite.tab.schema":"Схема",
    "sqlite.tab.sql":   "SQL",
    "sqlite.per_page":  "Строк:",
    "sqlite.page_info": "{start}–{end} из {total}",
    "sqlite.export_csv":"Экспорт в CSV…",
    "sqlite.export_done":"Экспорт завершён",
    "sqlite.col.name":  "Имя",
    "sqlite.col.type":  "Тип",
    "sqlite.sql_hint":  "SELECT * FROM таблица WHERE ...",
    "sqlite.run":       "▶  Выполнить",
    "sqlite.sql_rows":  "Возвращено строк: {n}",
    "sqlite.sql_affected": "Изменено строк: {n}",
    "sqlite.error":     "Ошибка",
    "sqlite.not_sqlite":"Это не файл SQLite",
    "sqlite.no_pk":     "В таблице нет первичного ключа. Редактирование запрещено.",

    "pwd.title":       "Генератор паролей",
    "pwd.generate":    "⟳  Сгенерировать",
    "pwd.copy":        "⧉  Копировать",
    "pwd.length":      "Длина:",
    "pwd.sets":        "НАБОРЫ СИМВОЛОВ",
    "pwd.set.lower":   "Строчные (abc)",
    "pwd.set.upper":   "Прописные (ABC)",
    "pwd.set.digits":  "Цифры (012)",
    "pwd.set.symbols": "Спецсимволы (!@#$)",
    "pwd.extra":       "ДОПОЛНИТЕЛЬНО",
    "pwd.opt.require": "Обязательно по одному из каждого набора",
    "pwd.opt.no_similar":   "Исключить похожие (il1Lo0O)",
    "pwd.opt.no_ambiguous": "Исключить неоднозначные ({}[]()…)",
    "pwd.opt.autocopy":     "Копировать при генерации",
    "pwd.tab.password": "Пароль",
    "pwd.tab.phrase":   "Парольная фраза",
    "pwd.tab.history":  "История",
    "pwd.uuid.generate":"⟳  Сгенерировать UUID",
    "pwd.uuid.count":   "Количество:",
    "pwd.phrase.generate":   "⟳  Сгенерировать фразу",
    "pwd.phrase.words":      "Слов:",
    "pwd.phrase.capitalize": "Заглавные буквы",
    "pwd.phrase.digit":      "Добавить число в конце",
    "pwd.history.clear":     "Очистить историю",

    "search.title":     "Поиск инструментов",
    "search.hint":      "Введите название или ключевое слово. "
                        "Например: «хеш», «метаданные», «кодировка».",
    "search.placeholder": "Поиск…",
    "search.empty":     "Ничего не найдено",
    "fonts.title": "Просмотр шрифтов",
    "fonts.browse": "Выбрать шрифт…",
    "fonts.drop_hint": "Перетащите TTF / OTF / TTC / WOFF сюда или нажмите, чтобы выбрать",
    "fonts.error": "Ошибка",
    "fonts.in_file": "Шрифтов в файле:",
    "fonts.method": "Метод",
    "fonts.method.fonttools": "fontTools",
    "fonts.method.qt": "Qt (упрощённо)",

    "fonts.tab.info": "Информация",
    "fonts.tab.preview": "Превью",
    "fonts.tab.tables": "Таблицы и юникод",

    "fonts.preview_text": "Текст для превью:",
    "fonts.preview_size": "Размер:",
    "fonts.preview_no_font": "Шрифт не загружен в Qt для превью",

    "fonts.unicode": "ПОДДЕРЖКА ЮНИКОДА",
    "fonts.tables": "ТАБЛИЦЫ ШРИФТА",
    "fonts.no_unicode": "Данные о юникоде недоступны",
    "fonts.no_tables": "Данные о таблицах недоступны",

    "fonts.group.names": "ИМЕНА",
    "fonts.group.metrics": "МЕТРИКИ",
    "fonts.group.license": "ЛИЦЕНЗИЯ И АВТОР",

    "fonts.metric.upm": "Units per em",
    "fonts.metric.ascender": "Ascender",
    "fonts.metric.descender": "Descender",
    "fonts.metric.line_gap": "Line gap",
    "fonts.metric.weight": "Вес",
    "fonts.metric.bold": "Жирный",
    "fonts.metric.italic": "Курсив",
    "fonts.metric.glyphs": "Глифов",

    "info.field.family": "Семейство",
    "info.field.subfamily": "Начертание",
    "info.field.full_name": "Полное имя",
    "info.field.postscript": "PostScript имя",
    "info.field.version": "Версия",
    "info.field.unique_id": "Уникальный ID",
    "info.field.copyright": "Copyright",
    "info.field.trademark": "Торговая марка",
    "info.field.manufacturer": "Производитель",
    "info.field.designer": "Дизайнер",
    "info.field.description": "Описание",
    "info.field.vendor_url": "URL производителя",
    "info.field.designer_url": "URL дизайнера",
    "info.field.license": "Лицензия",
    "info.field.license_url": "URL лицензии",
    "fonts.preview_fallback": "Qt подставил другой шрифт: {name}",
    "search.filter.all": "Все",
    "search.filter.title": "Группа",
    "search.filter.hint": "Ограничьте список одной группой инструментов.",

    "exifc.title": "Санитайзер EXIF",
    "exifc.browse": "Выбрать фото…",
    "exifc.drop_hint": "Перетащите фото сюда или нажмите, чтобы выбрать (JPG, PNG, WEBP, TIFF)",
    "exifc.found": "НАЙДЕННЫЕ EXIF-ПОЛЯ",
    "exifc.what_remove": "ЧТО УДАЛИТЬ",
    "exifc.clean_save": "⌦  Очистить и сохранить",
    "exifc.save_as": "Сохранить как…",
    "exifc.error": "Ошибка",
    "exifc.no_exif": "В файле нет EXIF-данных",
    "exifc.no_options": "Выберите хотя бы один пункт для удаления",
    "exifc.summary": "Найдено полей: {count}",
    "exifc.done": "Готово",
    "exifc.fields_removed": "полей удалено",
    "exifc.unsupported": "Формат не поддерживается для очистки",

    "exifc.opt.all": "Удалить весь EXIF",
    "exifc.opt.gps": "Удалить GPS-координаты",
    "exifc.opt.datetime": "Удалить даты съёмки",
    "exifc.opt.camera": "Удалить сведения о камере",
    "exifc.opt.author": "Удалить автора и копирайт",
    "exifc.opt.software": "Удалить программу обработки",
    "exifc.opt.thumbnail": "Удалить встроенный thumbnail",

    "exifc.group.gps": "GPS-КООРДИНАТЫ",
    "exifc.group.camera": "КАМЕРА",
    "exifc.group.datetime": "ДАТЫ",
    "exifc.group.author": "АВТОР",
    "exifc.group.software": "ПРОГРАММЫ",
    "exifc.group.other": "ПРОЧЕЕ",

    "qr.title": "QR-коды",
    "qr.data": "ДАННЫЕ",
    "qr.data_hint": "Введите ссылку или текст…",
    "qr.preview": "ПРЕВЬЮ",
    "qr.size": "Размер:",
    "qr.level": "Коррекция ошибок:",
    "qr.fg": "Цвет:",
    "qr.bg": "Фон:",
    "qr.color": "Выберите цвет",

    "qr.save_png": "💾  Сохранить PNG",
    "qr.save_svg": "💾  Сохранить SVG",
    "qr.copy_image": "⧉  Копировать изображение",
    "qr.copy_text": "⧉  Копировать текст",
    "qr.open_url": "🌐  Открыть ссылку",

    "qr.tab.generate": "Генерация",
    "qr.tab.decode": "Декодирование",

    "qr.empty_data": "Введите текст или ссылку",
    "qr.error": "Ошибка",
    "qr.no_qrcode": "Библиотека qrcode не установлена.\nУстановите: pip install \"qrcode[pil]\"",
    "qr.no_decoder": "Декодирование недоступно: не установлена pyzbar.\nУстановите: pip install pyzbar (требует zbar)",
    "qr.no_codes": "QR-коды не найдены на изображении",
    "qr.drop_hint": "Перетащите изображение с QR-кодом или нажмите, чтобы выбрать",
    "qr.decode_browse": "Выбрать изображение…",

    "stego.title": "Стеганография",
    "stego.tab.hide": "Спрятать",
    "stego.tab.extract": "Извлечь",
    "stego.drop_image": "Перетащите PNG-обложку или нажмите, чтобы выбрать",
    "stego.drop_stego": "Перетащите изображение со скрытыми данными или нажмите, чтобы выбрать",
    "stego.no_cover": "Обложка не выбрана",
    "stego.no_stego": "Файл не выбран",
    "stego.only_png": "Поддерживается только PNG — формат без потерь",
    "stego.capacity": "Максимум для скрытия: {cap}",
    "stego.what_text": "Спрятать текст",
    "stego.what_file": "Спрятать файл",
    "stego.text_hint": "Введите текст, который нужно спрятать…",
    "stego.no_payload_file": "Файл не выбран",
    "stego.pick_payload": "Выбрать файл…",
    "stego.protection": "ЗАЩИТА",
    "stego.no_password": "Без пароля",
    "stego.with_password": "С паролем (AES-256)",
    "stego.password": "Пароль:",
    "stego.password_hint": "Введите пароль…",
    "stego.hide": "◐  Спрятать и сохранить",
    "stego.save_stego": "Сохранить как…",
    "stego.extract": "◐  Извлечь",
    "stego.result": "РЕЗУЛЬТАТ",
    "stego.result_hint": "Здесь появится извлечённый текст",
    "stego.copy_result": "⧉  Копировать",
    "stego.save_result": "💾  Сохранить как…",
    "stego.done": "Готово",
    "stego.extracted": "Извлечено",
    "stego.error": "Ошибка",
    "stego.too_big": "Слишком большой payload: {payload} (максимум {cap})",
    "stego.binary_data": "Бинарные данные ({size}). Сохраните как файл.",
    "stego.no_pillow": "Pillow не установлен.\nУстановите: pip install Pillow",
    "stego.err.no_magic": "Это не стеганограмма или данные повреждены",
    "stego.err.password_required": "Файл зашифрован — нужен пароль",
    "stego.err.wrong_password": "Неверный пароль",
    "stego.err.corrupted": "Данные повреждены или неполные",

    "stego.density": "ПЛОТНОСТЬ ЗАПИСИ",
    "stego.density.1bit": "1 бит на канал — незаметно, базовая вместимость",
    "stego.density.2bit": "2 бита на канал — вместимость ×2, лёгкий шум",
    "stego.density.hint": "1 бит — невидимо даже на градиентах. "
                          "2 бита — вдвое больше данных, но может быть заметно "
                          "на однотонных участках.",

    "sidebar.logo.tip": "SemeryFiles — О программе и список возможностей",
    "sidebar.search.name": "Поиск инструментов",
    "sidebar.search.desc": "Найдите инструмент по названию или описанию.",
    "sidebar.settings.name": "Настройки",
    "sidebar.settings.desc": "Тема, язык, папки и другие параметры.",

    "tool.info.name": "Информация о файле",
    "tool.info.desc": "Размер, тип, даты, владелец и права доступа.",

    "tool.hash.name": "Хеширование",
    "tool.hash.desc": "SHA-256, SHA-512, MD5, BLAKE3 — контрольные суммы.",

    "tool.meta.name": "Метаданные",
    "tool.meta.desc": "EXIF, ID3, свойства PDF и Office-документов.",

    "tool.hex.name": "Hex-просмотр",
    "tool.hex.desc": "Содержимое файла в шестнадцатеричном виде.",

    "tool.compare.name": "Сравнение",
    "tool.compare.desc": "Побайтовое сравнение, по хешу или метаданным.",

    "tool.search_dup.name": "Поиск дубликатов",
    "tool.search_dup.desc": "Находит одинаковые файлы по хешу и размеру.",

    "tool.convert.name": "Конвертация",
    "tool.convert.desc": "Кодировка, формат, пересчёт контрольных сумм.",

    "tool.report.name": "Отчёты",
    "tool.report.desc": "Экспорт результатов в JSON, CSV или HTML.",

    "tool.encoding.name": "Определение кодировки",
    "tool.encoding.desc": "Распознаёт UTF-8, UTF-16, Windows-1251 и другие.",

    "tool.entropy.name": "Энтропия",
    "tool.entropy.desc": "Оценка энтропии файла — признак шифрования или сжатия.",

    "tool.strings.name": "Извлечение строк",
    "tool.strings.desc": "Поиск читаемых строк внутри бинарного файла.",

    "tool.magic.name": "Определение типа",
    "tool.magic.desc": "Реальный тип файла по сигнатуре, а не по расширению.",

    "tool.split_join.name": "Разбиение / склейка",
    "tool.split_join.desc": "Разбивает файл на части или собирает обратно.",

    "tool.wipe.name": "Безопасное удаление",
    "tool.wipe.desc": "Затирает файл так, чтобы его нельзя было восстановить.",

    "tool.base64.name": "Base64",
    "tool.base64.desc": "Кодирование и декодирование файлов в Base64.",

    "tool.random.name": "Генератор файлов",
    "tool.random.desc": "Создаёт случайные или тестовые файлы заданного размера.",

    "tool.permissions.name": "Права доступа",
    "tool.permissions.desc": "Просмотр и изменение прав файла (Unix/Windows).",

    "tool.timestamps.name": "Временные метки",
    "tool.timestamps.desc": "Просмотр и изменение дат создания/изменения.",

    "tool.regex.name": "Regex-тестер",
    "tool.regex.desc": "Поиск и замена по регулярным выражениям.",

    "tool.sqlite.name": "SQLite Viewer",
    "tool.sqlite.desc": "Просмотр и редактирование SQLite баз данных.",

    "tool.password.name": "Генератор паролей",
    "tool.password.desc": "Пароли, UUID, парольные фразы и hex-строки.",

    "tool.fonts.name": "Просмотр шрифтов",
    "tool.fonts.desc": "Разбор TTF, OTF, TTC, WOFF: имена, метрики, глифы.",

    "tool.exif_clean.name": "Санитайзер EXIF",
    "tool.exif_clean.desc": "Удаление GPS, дат, камеры и автора из фото.",

    "tool.qr.name": "QR-коды",
    "tool.qr.desc": "Генерация и декодирование QR-кодов.",

    "tool.stego.name": "Стеганография",
    "tool.stego.desc": "Скрытие текста или файла в PNG (LSB).",

    "b64.title": "Base64",
    "b64.tab.text": "Текст",
    "b64.tab.file_enc": "Файл → Base64",
    "b64.tab.file_dec": "Base64 → Файл",
    "b64.input": "ВВОД",
    "b64.output": "ВЫВОД",
    "b64.text_hint": "Введите текст или вставьте Base64…",
    "b64.output_hint": "Здесь появится результат",
    "b64.preview": "ПРЕВЬЮ",
    "b64.preview_hint": "Здесь появится Base64",
    "b64.encode": "Кодировать в Base64",
    "b64.decode": "Декодировать из Base64",
    "b64.encode_file": "Кодировать файл",
    "b64.decode_to_file": "Декодировать в файл",
    "b64.decode_from_text": "Декодировать вставленный текст",
    "b64.urlsafe": "URL-safe (без + / =)",
    "b64.line_width": "Длина строки:",
    "b64.chars": "симв.",
    "b64.no_wrap": "без переносов",
    "b64.copy": "⧉  Копировать",
    "b64.save_as": "💾  Сохранить как…",
    "b64.swap": "⇅  Поменять ввод/вывод",
    "b64.pick_file": "Выбрать файл…",
    "b64.pick_b64": "Выбрать Base64-файл…",
    "b64.no_file": "Файл не выбран",
    "b64.no_b64_file": "Base64-файл не выбран",
    "b64.or_paste": "ИЛИ ВСТАВЬТЕ BASE64",
    "b64.paste_hint": "Вставьте Base64-строку сюда…",
    "b64.file_enc_hint": "Выберите файл — он будет закодирован в Base64",
    "b64.file_dec_hint": "Выберите Base64-файл или вставьте строку — получите исходные данные",
    "b64.done": "Готово",
    "b64.error": "Ошибка",
}