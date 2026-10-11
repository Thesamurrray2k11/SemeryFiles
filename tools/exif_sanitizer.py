import os
import io

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

REMOVAL_OPTIONS = {
    "all_exif":      "Удалить весь EXIF",
    "gps":           "Удалить GPS-координаты",
    "datetime":      "Удалить даты съёмки",
    "camera":        "Удалить сведения о камере",
    "author":        "Удалить автора и копирайт",
    "software":      "Удалить программу обработки",
    "thumbnail":     "Удалить встроенный thumbnail",
}

TAG_GROUPS = {
    "gps": {
        "GPSInfo", "GPSLatitude", "GPSLongitude", "GPSAltitude",
        "GPSLatitudeRef", "GPSLongitudeRef", "GPSAltitudeRef",
        "GPSTimeStamp", "GPSDateStamp", "GPSSpeed", "GPSSpeedRef",
        "GPSImgDirection", "GPSImgDirectionRef", "GPSMapDatum",
        "GPSProcessingMethod", "GPSDestLatitude", "GPSDestLongitude",
    },
    "datetime": {
        "DateTime", "DateTimeOriginal", "DateTimeDigitized",
        "SubsecTime", "SubsecTimeOriginal", "SubsecTimeDigitized",
        "OffsetTime", "OffsetTimeOriginal", "OffsetTimeDigitized",
        "GPSDateStamp", "GPSTimeStamp",
    },
    "camera": {
        "Make", "Model", "LensMake", "LensModel", "LensSerialNumber",
        "BodySerialNumber", "CameraOwnerName", "SerialNumber",
        "FocalLength", "FocalLengthIn35mmFilm", "ExposureTime",
        "FNumber", "ISOSpeedRatings", "PhotographicSensitivity",
        "ShutterSpeedValue", "ApertureValue", "ExposureProgram",
        "ExposureBiasValue", "MeteringMode", "Flash", "WhiteBalance",
        "ColorSpace", "Orientation",
    },
    "author": {
        "Artist", "Copyright", "XPAuthor", "XPComment",
        "ImageDescription", "UserComment",
    },
    "software": {
        "Software", "ProcessingSoftware", "HostComputer",
        "XMPToolkit", "CreatorTool",
    },
    "thumbnail": {
        "thumbnail", "Thumbnail", "JPEGThumbnail", "TIFFThumbnail",
    },
}


def is_supported(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTENSIONS


def _read_exif_safe(img: "Image.Image") -> dict:
    try:
        from PIL import ExifTags
        exif = img.getexif()
        if not exif:
            return {}
        result = {}
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
            result[tag] = value

        try:
            exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
            for tag_id, value in exif_ifd.items():
                tag = ExifTags.TAGS.get(tag_id, str(tag_id))
                result[tag] = value
        except Exception:
            pass

        try:
            gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)
            for tag_id, value in gps_ifd.items():
                tag = ExifTags.GPSTAGS.get(tag_id, str(tag_id))
                result[f"GPS.{tag}"] = value
        except Exception:
            pass

        return result
    except Exception:
        return {}


def list_exif_fields(path: str) -> dict:
    if not PIL_AVAILABLE:
        return {"ok": False, "error": "no_pillow", "fields": {},
                "groups": {}, "count": 0}

    if not path or not os.path.isfile(path):
        return {"ok": False, "error": "file_not_found", "fields": {},
                "groups": {}, "count": 0}

    try:
        with Image.open(path) as img:
            fields = _read_exif_safe(img)
    except Exception as e:
        return {"ok": False, "error": str(e), "fields": {},
                "groups": {}, "count": 0}

    groups = {"gps": [], "camera": [], "datetime": [],
              "author": [], "software": [], "other": []}

    for tag in fields:
        placed = False
        if tag.startswith("GPS."):
            groups["gps"].append(tag)
            continue
        for grp_name, grp_tags in TAG_GROUPS.items():
            if grp_name == "thumbnail":
                continue
            if tag in grp_tags:
                groups[grp_name].append(tag)
                placed = True
                break
        if not placed:
            groups["other"].append(tag)

    for k in groups:
        groups[k].sort()

    return {
        "ok": True, "error": None,
        "fields": fields, "groups": groups,
        "count": len(fields),
    }


def _tag_ids_for_removal(remove_keys: list[str]) -> set[int]:
    from PIL import ExifTags

    ids = set()
    for key in remove_keys:
        if key == "all_exif":
            return None

        if key == "gps":
            ids.add(ExifTags.IFD.GPSInfo if hasattr(ExifTags, "IFD") else 0x8825)
            ids.add(0x8825)
        elif key == "datetime":
            for name in TAG_GROUPS["datetime"]:
                for tid, tag in ExifTags.TAGS.items():
                    if tag == name:
                        ids.add(tid)
        elif key == "camera":
            for name in TAG_GROUPS["camera"]:
                for tid, tag in ExifTags.TAGS.items():
                    if tag == name:
                        ids.add(tid)
        elif key == "author":
            for name in TAG_GROUPS["author"]:
                for tid, tag in ExifTags.TAGS.items():
                    if tag == name:
                        ids.add(tid)
        elif key == "software":
            for name in TAG_GROUPS["software"]:
                for tid, tag in ExifTags.TAGS.items():
                    if tag == name:
                        ids.add(tid)
        elif key == "thumbnail":
            pass

    return ids


def sanitize(
    src: str,
    dst: str,
    remove_keys: list[str],
    keep_orientation: bool = True,
    jpeg_quality: int = 95,
) -> dict:
    if not PIL_AVAILABLE:
        return {"ok": False, "error": "no_pillow", "removed": 0}

    if not os.path.isfile(src):
        return {"ok": False, "error": "file_not_found", "removed": 0}

    if not remove_keys:
        return {"ok": False, "error": "no_options", "removed": 0}

    try:
        with Image.open(src) as img:
            fmt = img.format or "JPEG"
            if fmt == "MPO":
                fmt = "JPEG"

            if "all_exif" in remove_keys:
                clean = img.copy()
                removed = len(_read_exif_safe(img))

                save_kwargs = _save_kwargs(fmt, jpeg_quality)
                clean.save(dst, format=fmt, **save_kwargs)
                return {"ok": True, "error": None, "removed": removed}

            exif = img.getexif()
            if exif is None:
                img.save(dst, format=fmt, **_save_kwargs(fmt, jpeg_quality))
                return {"ok": True, "error": None, "removed": 0}

            ids_to_remove = _tag_ids_for_removal(remove_keys)
            removed = 0

            if ids_to_remove is None:
                exif = {}
            else:
                top_tags = list(exif.keys())
                for tid in top_tags:
                    if tid in ids_to_remove:
                        try:
                            del exif[tid]
                            removed += 1
                        except Exception:
                            pass

            if "gps" in remove_keys:
                try:
                    GPS_TAG_ID = 0x8825
                    if GPS_TAG_ID in exif:
                        del exif[GPS_TAG_ID]
                        removed += 1
                except Exception:
                    pass

            if "thumbnail" in remove_keys:
                pass

            if keep_orientation:
                pass

            clean = img.copy()
            exif_bytes = b""
            try:
                exif_bytes = exif.tobytes()
            except Exception:
                exif_bytes = b""

            save_kwargs = _save_kwargs(fmt, jpeg_quality)
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes

            clean.save(dst, format=fmt, **save_kwargs)

            return {"ok": True, "error": None, "removed": removed}

    except Exception as e:
        return {"ok": False, "error": str(e), "removed": 0}


def _save_kwargs(fmt: str, jpeg_quality: int) -> dict:
    fmt = (fmt or "").upper()
    if fmt == "JPEG":
        return {"quality": jpeg_quality, "optimize": True}
    if fmt == "PNG":
        return {"optimize": True}
    if fmt == "WEBP":
        return {"quality": jpeg_quality}
    if fmt in ("TIFF", "TIF"):
        return {}
    return {}