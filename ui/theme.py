from PySide6.QtCore import QObject, Signal


LIGHT = {
    "bg":         "#F6F3EE",
    "sidebar":    "#EFEBE3",
    "card":       "#FCFAF6",
    "card_alt":   "#F3EFE8",

    "border":     "#DED8CC",
    "border_hi":  "#C8C1B2",

    "text":       "#2B2A28",
    "text_dim":   "#7C766B",
    "text_mute":  "#A8A196",

    "accent":     "#5B7C99",
    "accent_hi":  "#7A9AB5",
    "accent_lo":  "#E4EAEF",

    "c_info":     "#6B8CA8",
    "c_hash":     "#8A7BA8",
    "c_meta":     "#B58A6B",
    "c_hex":      "#7A9B8E",
    "c_compare":  "#A8896B",
    "c_search":   "#8A9B6B",
    "c_convert":  "#B57A8E",
    "c_report":   "#6B8A9B",
    "c_settings": "#8B8B8B",

    "success":    "#7A9B6B",
    "warning":    "#C9A76B",
    "danger":     "#B57A6B",
    "info":       "#6B8CA8",

    "tooltip_bg": "#2B2A28",
    "tooltip_fg": "#F6F3EE",
}


DARK = {

    "bg":         "#1E1F22",
    "sidebar":    "#24262A",
    "card":       "#2A2C31",
    "card_alt":   "#232529",

    "border":     "#3A3D43",
    "border_hi":  "#4A4E55",

    "text":       "#E6E4DF",
    "text_dim":   "#9A968E",
    "text_mute":  "#6E6A63",

    "accent":     "#7A9AB5",
    "accent_hi":  "#9AB4C9",
    "accent_lo":  "#2F3842",

    "c_info":     "#8AABBF",
    "c_hash":     "#A89BC4",
    "c_meta":     "#D4A888",
    "c_hex":      "#96B8AA",
    "c_compare":  "#C4A98A",
    "c_search":   "#A8B888",
    "c_convert":  "#D19AAA",
    "c_report":   "#8AAABF",
    "c_settings": "#A8A8A8",

    "success":    "#96B8AA",
    "warning":    "#D4B888",
    "danger":     "#D19A88",
    "info":       "#8AABBF",

    "tooltip_bg": "#E6E4DF",
    "tooltip_fg": "#1E1F22",
}


class ThemeManager(QObject):

    changed = Signal(str)

    def __init__(self):
        super().__init__()
        self._current = "light"

    @property
    def current(self) -> str:
        return self._current

    @property
    def colors(self) -> dict:
        return LIGHT if self._current == "light" else DARK

    def set_theme(self, name: str):
        if name not in ("light", "dark") or name == self._current:
            return
        self._current = name
        self.changed.emit(name)

    def toggle(self):
        self.set_theme("dark" if self._current == "light" else "light")