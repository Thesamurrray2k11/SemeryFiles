import os

try:
    from fontTools.ttLib import TTFont, TTCollection
    FONTTOOLS_AVAILABLE = True
except ImportError:
    FONTTOOLS_AVAILABLE = False


FONT_EXTENSIONS = {
    ".ttf", ".otf", ".ttc", ".woff", ".woff2",
    ".otc", ".eot",
}


def is_font_file(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in FONT_EXTENSIONS


def _read_name_table(font: "TTFont") -> dict:
    WANTED = {
        0: "copyright",
        1: "family",
        2: "subfamily",
        3: "unique_id",
        4: "full_name",
        5: "version",
        6: "postscript_name",
        7: "trademark",
        8: "manufacturer",
        9: "designer",
        10: "description",
        11: "vendor_url",
        12: "designer_url",
        13: "license",
        14: "license_url",
    }
    result = {}
    try:
        name_table = font["name"]
    except KeyError:
        return result
    for record in name_table.names:
        try:
            if record.nameID not in WANTED:
                continue
            try:
                text = record.toUnicode()
            except Exception:
                continue
            text = text.strip()
            if not text:
                continue

            key = WANTED[record.nameID]
            if key not in result:
                result[key] = text
            elif record.langID == 0x0409 and not result.get(f"_{key}_en"):
                result[key] = text
                result[f"_{key}_en"] = True
        except Exception:
            continue

    return result


def _read_unicode_ranges(font: "TTFont") -> dict:
    coverage = {
        "latin": False,
        "cyrillic": False,
        "greek": False,
        "cjk": False,
        "arabic": False,
        "hebrew": False,
    }
    total_glyphs = 0

    try:
        cmap = font.getBestCmap()
        if cmap:
            total_glyphs = len(cmap)
            for cp in cmap.keys():
                if not coverage["latin"] and (
                    0x0041 <= cp <= 0x007A or 0x00C0 <= cp <= 0x024F
                ):
                    coverage["latin"] = True
                if not coverage["cyrillic"] and (
                    0x0400 <= cp <= 0x04FF or 0x0500 <= cp <= 0x052F
                ):
                    coverage["cyrillic"] = True
                if not coverage["greek"] and 0x0370 <= cp <= 0x03FF:
                    coverage["greek"] = True
                if not coverage["cjk"] and (
                    0x4E00 <= cp <= 0x9FFF or 0x3000 <= cp <= 0x30FF
                ):
                    coverage["cjk"] = True
                if not coverage["arabic"] and 0x0600 <= cp <= 0x06FF:
                    coverage["arabic"] = True
                if not coverage["hebrew"] and 0x0590 <= cp <= 0x05FF:
                    coverage["hebrew"] = True
    except Exception:
        pass

    return {"coverage": coverage, "total_glyphs": total_glyphs}


def _read_head(font: "TTFont") -> dict:
    data = {}
    try:
        head = font["head"]
        data["units_per_em"] = head.unitsPerEm
        data["created"] = str(head.created)
        data["modified"] = str(head.modified)
        # Флаги
        mac_style = head.macStyle
        data["mac_style_bold"] = bool(mac_style & 0x01)
        data["mac_style_italic"] = bool(mac_style & 0x02)
    except Exception:
        pass

    try:
        hhea = font["hhea"]
        data["ascender"] = hhea.ascent
        data["descender"] = hhea.descent
        data["line_gap"] = hhea.lineGap
    except Exception:
        pass

    try:
        os2 = font["OS/2"]
        data["weight_class"] = os2.usWeightClass
        data["width_class"] = os2.usWidthClass
        data["fs_type"] = os2.fsType
    except Exception:
        pass

    return data


def _read_tables(font: "TTFont") -> list[str]:
    try:
        return sorted(font.keys())
    except Exception:
        return []


def _weight_label(weight: int) -> str:
    mapping = {
        100: "Thin", 200: "ExtraLight", 300: "Light",
        400: "Regular", 500: "Medium", 600: "SemiBold",
        700: "Bold", 800: "ExtraBold", 900: "Black",
    }
    return mapping.get(weight, str(weight))


def _humanize_bytes(n: int) -> str:
    f = float(n)
    for suf in ("Б", "KiB", "MiB", "GiB"):
        if f < 1024:
            return f"{int(f)} {suf}" if suf == "Б" else f"{f:.2f} {suf}"
        f /= 1024
    return f"{f:.2f} TiB"


def collect_font_info(path: str) -> dict:
    if not path or not os.path.isfile(path):
        return {"ok": False, "error": "file_not_found", "method": None, "fonts": []}

    if not is_font_file(path):
        return {"ok": False, "error": "not_font", "method": None, "fonts": []}

    if not FONTTOOLS_AVAILABLE:
        return _collect_via_qt(path)

    ext = os.path.splitext(path)[1].lower()

    fonts = []
    try:
        if ext in (".ttc", ".otc"):
            collection = TTCollection(path, lazy=True)
            for idx, font in enumerate(collection.fonts):
                fonts.append(_font_to_dict(font, idx))
            collection.close()
        else:
            font = TTFont(path, lazy=True, fontNumber=0)
            fonts.append(_font_to_dict(font, 0))
            font.close()
    except Exception as e:
        return {
            "ok": False, "error": f"parse_error: {e}",
            "method": "fonttools", "fonts": [],
        }

    if not fonts:
        return {"ok": False, "error": "no_fonts", "method": "fonttools", "fonts": []}

    return {"ok": True, "error": None, "method": "fonttools", "fonts": fonts}


def _font_to_dict(font: "TTFont", index: int) -> dict:
    names = _read_name_table(font)
    metrics = _read_head(font)
    uni = _read_unicode_ranges(font)
    tables = _read_tables(font)
    weight = metrics.get("weight_class", 400)
    metrics["weight_label"] = _weight_label(weight)

    return {
        "index": index,
        "names": names,
        "metrics": metrics,
        "unicode": uni,
        "tables": tables,
    }


def _collect_via_qt(path: str) -> dict:
    try:
        from PySide6.QtGui import QFontDatabase
    except ImportError:
        return {"ok": False, "error": "no_qt", "method": None, "fonts": []}

    font_id = QFontDatabase.addApplicationFont(path)
    if font_id < 0:
        return {"ok": False, "error": "qt_load_failed",
                "method": "qt", "fonts": []}

    families = QFontDatabase.applicationFontFamilies(font_id)
    styles = QFontDatabase.applicationFontStyles(font_id)

    fonts = []
    for i, family in enumerate(families):
        style = styles[i] if i < len(styles) else ""
        fonts.append({
            "index": i,
            "names": {
                "family": family,
                "subfamily": style,
                "full_name": f"{family} {style}".strip(),
            },
            "metrics": {},
            "unicode": {"coverage": {}, "total_glyphs": 0},
            "tables": [],
        })

    return {"ok": True, "error": None, "method": "qt", "fonts": fonts}


def register_for_preview(path: str) -> int:
    try:
        from PySide6.QtGui import QFontDatabase
        return QFontDatabase.addApplicationFont(path)
    except Exception:
        return -1
def register_renamed(path: str, suffix: str = "_sfview") -> tuple[int, str]:
    if not FONTTOOLS_AVAILABLE:
        return -1, ""

    import tempfile
    import os as _os

    try:
        from PySide6.QtGui import QFontDatabase
    except ImportError:
        return -1, ""

    try:
        font = TTFont(path)
    except Exception:
        return -1, ""

    try:
        family = None
        name_table = font["name"]
        for record in name_table.names:
            if record.nameID == 1:
                try:
                    family = record.toUnicode()
                    break
                except Exception:
                    continue

        if not family:
            font.close()
            return -1, ""

        new_family = family + suffix

        for record in name_table.names:
            if record.nameID in (1, 4, 6, 16):
                try:
                    old = record.toUnicode()
                    new_text = old.replace(family, new_family)
                    record.string = new_text.encode(record.getEncoding())
                except Exception:
                    continue

        tmp = tempfile.NamedTemporaryFile(suffix=".ttf", delete=False)
        tmp_path = tmp.name
        tmp.close()

        font.save(tmp_path)
        font.close()

        fid = QFontDatabase.addApplicationFont(tmp_path)
        return fid, new_family

    except Exception:
        try:
            font.close()
        except Exception:
            pass
        return -1, ""


def get_family_for_preview(font_id: int) -> str | None:
    """Возвращает имя первого семейства из зарегистрированного шрифта."""
    try:
        from PySide6.QtGui import QFontDatabase
        families = QFontDatabase.applicationFontFamilies(font_id)
        return families[0] if families else None
    except Exception:
        return None