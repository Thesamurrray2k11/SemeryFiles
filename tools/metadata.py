import os
from datetime import datetime

try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff",
    ".bmp", ".gif", ".heic", ".heif", ".avif",
}


_EXIF_LABELS = {
    "Make":             "Производитель камеры",
    "Model":            "Модель камеры",
    "Software":         "Программа",
    "DateTime":         "Дата изменения",
    "DateTimeOriginal": "Дата съёмки",
    "DateTimeDigitized":"Дата оцифровки",
    "Artist":           "Автор",
    "Copyright":        "Копирайт",
    "ExposureTime":     "Выдержка",
    "FNumber":          "Диафрагма",
    "ISOSpeedRatings":  "ISO",
    "ShutterSpeedValue":"Выдержка (APEX)",
    "ApertureValue":    "Диафрагма (APEX)",
    "ExposureBiasValue":"Экспокоррекция",
    "FocalLength":      "Фокусное расстояние",
    "FocalLengthIn35mmFilm": "Фокусное (35мм экв.)",
    "Flash":            "Вспышка",
    "MeteringMode":     "Режим замера",
    "WhiteBalance":     "Баланс белого",
    "ExposureProgram":  "Программа экспозиции",
    "Orientation":      "Ориентация",
    "ColorSpace":       "Цветовое пространство",
    "XResolution":      "Разрешение по X",
    "YResolution":      "Разрешение по Y",
    "ResolutionUnit":   "Единица разрешения",
    "ExifImageWidth":   "Ширина (EXIF)",
    "ExifImageHeight":  "Высота (EXIF)",
    "LensModel":        "Модель объектива",
    "LensMake":         "Производитель объектива",
    "BodySerialNumber": "Серийный номер камеры",
    "LensSerialNumber": "Серийный номер объектива",
    "UserComment":      "Комментарий",
    "ImageDescription": "Описание",
    "SubjectDistance":  "Дистанция до объекта",
    "DigitalZoomRatio": "Цифровой зум",
    "SceneCaptureType": "Тип сцены",
    "Contrast":         "Контраст",
    "Saturation":       "Насыщенность",
    "Sharpness":        "Резкость",
}


# GPS-поля
_GPS_LABELS = {
    "GPSLatitudeRef":  "Широта (напр.)",
    "GPSLatitude":     "Широта",
    "GPSLongitudeRef": "Долгота (напр.)",
    "GPSLongitude":    "Долгота",
    "GPSAltitudeRef":  "Высота (напр.)",
    "GPSAltitude":     "Высота",
    "GPSTimeStamp":    "Время GPS",
    "GPSDateStamp":    "Дата GPS",
    "GPSSpeedRef":     "Скорость (ед.)",
    "GPSSpeed":        "Скорость",
    "GPSImgDirectionRef": "Направление (ед.)",
    "GPSImgDirection":    "Направление камеры",
    "GPSProcessingMethod": "Метод定位",
    "GPSMapDatum":     "Геод. система",
}


def is_image(path: str) -> bool:
    ext = os.path.splitext(path)[1].lower()
    return ext in IMAGE_EXTENSIONS


def _fmt_size(size: int) -> str:
    f = float(size)
    for suf in ["Б", "KiB", "MiB", "GiB", "TiB"]:
        if f < 1024:
            return f"{int(f)} {suf}" if suf == "Б" else f"{f:.2f} {suf}"
        f /= 1024
    return f"{f:.2f} PiB"


def _fmt_date(s: str) -> str:
    if not isinstance(s, str):
        return str(s)
    try:
        dt = datetime.strptime(s, "%Y:%m:%d %H:%M:%S")
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except ValueError:
        return s


def _rational(v) -> str:
    if isinstance(v, tuple) and len(v) == 2:
        num, den = v
        if den == 0:
            return str(num)
        if den == 1:
            return str(num)
        return f"{num}/{den}  ({num/den:.4g})"
    return str(v)


def _gps_to_decimal(coord, ref: str) -> float | None:
    try:
        values = []
        for part in coord:
            if isinstance(part, tuple) and len(part) == 2:
                values.append(part[0] / part[1] if part[1] else 0)
            else:
                values.append(float(part))
        deg, min_, sec = values[:3]
        result = deg + min_ / 60 + sec / 3600
        if ref in ("S", "W"):
            result = -result
        return result
    except Exception:
        return None


def _extract_exif(path: str) -> dict:
    if not PIL_AVAILABLE:
        return {}

    result = {}
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return {}

            # Основные теги
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, str(tag_id))

                if tag == "GPSInfo":
                    continue
                if tag in ("ExifOffset", "GPSInfo", "InteroperabilityOffset",
                           "MakerNote", "UserComment"):
                    continue

                label = _EXIF_LABELS.get(tag, tag)
                if tag in ("ExposureTime", "FNumber", "FocalLength"):
                    result[label] = _rational(value)
                elif tag in ("DateTime", "DateTimeOriginal", "DateTimeDigitized"):
                    result[label] = _fmt_date(value)
                else:
                    result[label] = str(value)

            try:
                exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
                for tag_id, value in exif_ifd.items():
                    tag = ExifTags.TAGS.get(tag_id, str(tag_id))
                    if tag in ("MakerNote", "UserComment", "GPSInfo"):
                        continue
                    label = _EXIF_LABELS.get(tag, tag)
                    if tag in ("ExposureTime", "FNumber", "FocalLength",
                               "ShutterSpeedValue", "ApertureValue",
                               "ExposureBiasValue"):
                        result[label] = _rational(value)
                    elif tag in ("DateTimeOriginal", "DateTimeDigitized"):
                        result[label] = _fmt_date(value)
                    else:
                        result[label] = str(value)
            except Exception:
                pass
            try:
                gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
                if gps_ifd:
                    for tag_id, value in gps_ifd.items():
                        tag = ExifTags.GPSTAGS.get(tag_id, str(tag_id))
                        label = _GPS_LABELS.get(tag, tag)
                        if tag in ("GPSLatitude", "GPSLongitude"):
                            # оставим как есть, отдельно сделаем десятичные
                            result[f"{label} (DMS)"] = str(value)
                        elif tag in ("GPSAltitude", "GPSSpeed",
                                     "GPSImgDirection"):
                            result[label] = _rational(value)
                        else:
                            result[label] = str(value)
            except Exception:
                pass

    except Exception as e:
        result["Ошибка EXIF"] = str(e)

    return result


def _extract_gps(path: str) -> dict:
    if not PIL_AVAILABLE:
        return {}

    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return {}
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            if not gps_ifd:
                return {}

            data = {}
            lat = _gps_to_decimal(
                gps_ifd.get(ExifTags.GPS.GPSLatitude),
                str(gps_ifd.get(ExifTags.GPS.GPSLatitudeRef, "N")),
            )
            lon = _gps_to_decimal(
                gps_ifd.get(ExifTags.GPS.GPSLongitude),
                str(gps_ifd.get(ExifTags.GPS.GPSLongitudeRef, "E")),
            )
            if lat is not None:
                data["lat"] = lat
            if lon is not None:
                data["lon"] = lon

            alt = gps_ifd.get(ExifTags.GPS.GPSAltitude)
            if alt is not None:
                if isinstance(alt, tuple) and len(alt) == 2:
                    data["alt"] = alt[0] / alt[1] if alt[1] else 0
                else:
                    data["alt"] = float(alt)
            return data
    except Exception:
        return {}


def collect_metadata(path: str, units: str = "binary") -> dict:
    if not path or not os.path.isfile(path):
        return {"ok": False, "error": "file_not_found", "groups": [], "gps": None}

    if not is_image(path):
        return {"ok": False, "error": "not_image", "groups": [], "gps": None}

    if not PIL_AVAILABLE:
        return {"ok": False, "error": "no_pillow", "groups": [], "gps": None}

    try:
        st = os.stat(path)
    except OSError as e:
        return {"ok": False, "error": str(e), "groups": [], "gps": None}

    groups = []
    general = [
        ("Имя", os.path.basename(path)),
        ("Размер", _fmt_size(st.st_size)),
        ("Расширение", os.path.splitext(path)[1].lstrip(".").upper()),
    ]
    try:
        with Image.open(path) as img:
            general.append(("Формат", img.format or "—"))
            general.append(("Размер", f"{img.width} × {img.height} px"))
            general.append(("Режим", img.mode))
            megapixels = (img.width * img.height) / 1_000_000
            general.append(("Мегапиксели", f"{megapixels:.2f} Мп"))
    except Exception:
        pass

    groups.append({"title_key": "meta.group.general", "rows": general})

    exif_data = _extract_exif(path)
    if exif_data:
        camera_keys = {
            "Производитель камеры", "Модель камеры", "Модель объектива",
            "Производитель объектива", "Серийный номер камеры",
            "Серийный номер объектива", "Программа", "Автор", "Копирайт",
        }
        shoot_keys = {
            "Выдержка", "Диафрагма", "ISO", "Выдержка (APEX)",
            "Диафрагма (APEX)", "Экспокоррекция", "Фокусное расстояние",
            "Фокусное (35мм экв.)", "Вспышка", "Режим замера",
            "Баланс белого", "Программа экспозиции", "Дистанция до объекта",
            "Цифровой зум", "Тип сцены", "Контраст", "Насыщенность",
            "Резкость",
        }
        datetime_keys = {
            "Дата съёмки", "Дата изменения", "Дата оцифровки",
        }

        camera_rows, shoot_rows, datetime_rows, other_rows = [], [], [], []
        for label, value in exif_data.items():
            if label in camera_keys:
                camera_rows.append((label, value))
            elif label in shoot_keys:
                shoot_rows.append((label, value))
            elif label in datetime_keys:
                datetime_rows.append((label, value))
            elif label.startswith("GPS"):
                continue
            else:
                other_rows.append((label, value))

        if camera_rows:
            groups.append({"title_key": "meta.group.camera", "rows": camera_rows})
        if shoot_rows:
            groups.append({"title_key": "meta.group.shooting", "rows": shoot_rows})
        if datetime_rows:
            groups.append({"title_key": "meta.group.datetime", "rows": datetime_rows})
        if other_rows:
            groups.append({"title_key": "meta.group.exif_other", "rows": other_rows})

    gps = _extract_gps(path)
    if gps.get("lat") is not None and gps.get("lon") is not None:
        rows = [
            ("Широта (дес.)", f"{gps['lat']:.6f}"),
            ("Долгота (дес.)", f"{gps['lon']:.6f}"),
        ]
        if "alt" in gps:
            rows.append(("Высота", f"{gps['alt']:.1f} м"))
        rows.append(("OpenStreetMap",
                     f"https://www.openstreetmap.org/?mlat={gps['lat']}&mlon={gps['lon']}#map=16/{gps['lat']}/{gps['lon']}"))
        rows.append(("Google Maps",
                     f"https://www.google.com/maps?q={gps['lat']},{gps['lon']}"))
        groups.append({"title_key": "meta.group.gps", "rows": rows})

    return {
        "ok": True,
        "error": None,
        "groups": groups,
        "gps": gps if gps else None,
    }