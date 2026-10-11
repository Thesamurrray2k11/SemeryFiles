import os

from PySide6.QtCore import (
    Qt, Signal, QUrl, QSize, Property, QPropertyAnimation,
    QEasingCurve, QRectF
)
from PySide6.QtGui import (
    QDesktopServices, QIcon, QPixmap, QPainter, QColor, QBrush
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QToolButton,
    QFrame, QSizePolicy, QLineEdit, QFileDialog, QButtonGroup,
    QRadioButton, QScrollArea, QAbstractButton
)

from core.settings import AppSettings
from core.i18n import i18n
from core.locales import available_languages


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(BASE_DIR, "assets", "icons")


class RoundLinkButton(QToolButton):
    def __init__(self, icon_path: str, bg_color: str, icon_color: str = "#FFFFFF",
                 size: int = 56, icon_size: int = 26,
                 tooltip: str = "", parent=None):
        super().__init__(parent)
        self._icon_path = icon_path
        self._bg = bg_color
        self._icon_color = icon_color
        self._size = size
        self._icon_size = icon_size

        self.setObjectName("RoundLinkButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setAutoRaise(True)
        self.setFixedSize(size, size)
        self.setToolTip(tooltip)
        self.setIconSize(QSize(icon_size, icon_size))
        self._apply()

    def set_colors(self, bg_color: str, icon_color: str):
        self._bg = bg_color
        self._icon_color = icon_color
        self._apply()

    def set_tooltip(self, text: str):
        self.setToolTip(text)

    def _apply(self):
        self.setIcon(self._load_icon(self._icon_color))
        self._apply_bg(self._bg)

    def _load_icon(self, color: str) -> QIcon:
        if not os.path.exists(self._icon_path):
            return QIcon()
        renderer = QSvgRenderer(self._icon_path)
        pm = QPixmap(self._icon_size * 2, self._icon_size * 2)
        pm.fill(Qt.transparent)
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.Antialiasing, True)
        renderer.render(painter)
        painter.end()

        tinted = QPixmap(pm.size())
        tinted.fill(Qt.transparent)
        p2 = QPainter(tinted)
        p2.drawPixmap(0, 0, pm)
        p2.setCompositionMode(QPainter.CompositionMode_SourceIn)
        p2.fillRect(tinted.rect(), QColor(color))
        p2.end()
        return QIcon(tinted)

    def _apply_bg(self, color: str):
        r = self._size // 2
        dark = self._is_dark(color)
        hover = self._lighten(color, 18) if dark else self._darken(color, 8)
        pressed = self._darken(color, 12) if dark else self._darken(color, 18)
        self.setStyleSheet(
            f"QToolButton#RoundLinkButton {{"
            f"  background-color: {color}; border: none; border-radius: {r}px;"
            f"}}"
            f"QToolButton#RoundLinkButton:hover {{ background-color: {hover}; }}"
            f"QToolButton#RoundLinkButton:pressed {{ background-color: {pressed}; }}"
        )

    @staticmethod
    def _is_dark(hex_color: str) -> bool:
        c = QColor(hex_color)
        return (c.red() + c.green() + c.blue()) / 3 < 128

    @staticmethod
    def _lighten(hex_color: str, amount: int) -> str:
        return QColor(hex_color).lighter(100 + amount).name()

    @staticmethod
    def _darken(hex_color: str, amount: int) -> str:
        return QColor(hex_color).darker(100 + amount).name()


class ToggleSwitch(QAbstractButton):

    toggled_on = Signal(bool)

    WIDTH = 44
    HEIGHT = 24
    PADDING = 3
    DURATION = 180

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("ToggleSwitch")
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        self._bg_off = QColor("#D6D6D2")
        self._bg_on = QColor("#7A9B6B")
        self._knob = QColor("#FFFFFF")

        self._t = 1.0 if checked else 0.0

        self._anim = QPropertyAnimation(self, b"t", self)
        self._anim.setDuration(self.DURATION)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self.toggled.connect(self._on_toggled)

    def get_t(self) -> float:
        return self._t

    def set_t(self, value: float):
        self._t = max(0.0, min(1.0, value))
        self.update()

    t = Property(float, get_t, set_t)

    def _on_toggled(self, checked: bool):
        self._anim.stop()
        self._anim.setStartValue(self._t)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()
        self.toggled_on.emit(checked)

    def set_palette(self, bg_off: str, bg_on: str, knob: str):
        self._bg_off = QColor(bg_off)
        self._bg_on = QColor(bg_on)
        self._knob = QColor(knob)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w = self.width()
        h = self.height()
        r = h / 2

        bg = QColor(
            int(self._bg_off.red()   * (1 - self._t) + self._bg_on.red()   * self._t),
            int(self._bg_off.green() * (1 - self._t) + self._bg_on.green() * self._t),
            int(self._bg_off.blue()  * (1 - self._t) + self._bg_on.blue()  * self._t),
        )

        p.setBrush(QBrush(bg))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)

        knob_d = h - self.PADDING * 2
        x_min = self.PADDING
        x_max = w - self.PADDING - knob_d
        x = x_min + (x_max - x_min) * self._t

        p.setBrush(QBrush(self._knob))
        p.drawEllipse(QRectF(x, self.PADDING, knob_d, knob_d))

        p.end()


class SettingRow(QWidget):
    def __init__(self, title_key: str, hint_key: str = None, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self._title_key = title_key
        self._hint_key = hint_key
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("SettingsLabel")
        self.title_lbl.setAutoFillBackground(False)
        text_col.addWidget(self.title_lbl)

        self.hint_lbl = QLabel()
        self.hint_lbl.setObjectName("SettingsHint")
        self.hint_lbl.setWordWrap(True)
        self.hint_lbl.setAutoFillBackground(False)
        text_col.addWidget(self.hint_lbl)

        row.addLayout(text_col, 1)

        self.control_host = QWidget()
        self.control_host.setObjectName("SettingControlHost")
        self.control_host.setAutoFillBackground(False)
        self.control_host.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.control_layout = QHBoxLayout(self.control_host)
        self.control_layout.setContentsMargins(0, 0, 0, 0)
        self.control_layout.setSpacing(0)
        row.addWidget(self.control_host)

        outer.addLayout(row)
        self.retranslate()

    def add_control(self, w: QWidget):
        self.control_layout.addWidget(w)

    def retranslate(self):
        self.title_lbl.setText(i18n.t(self._title_key))
        if self._hint_key:
            self.hint_lbl.setText(i18n.t(self._hint_key))
            self.hint_lbl.setVisible(True)
        else:
            self.hint_lbl.setVisible(False)


class PathPicker(QWidget):
    path_changed = Signal(str)

    def __init__(self, initial: str = "", parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self._build(initial)

    def _build(self, initial):
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self.line = QLineEdit()
        self.line.setObjectName("PathInput")
        self.line.setText(initial)
        self.line.setReadOnly(True)
        self.line.setMinimumWidth(240)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("PathBrowseBtn")
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._browse)

        self.btn_clear = QToolButton()
        self.btn_clear.setObjectName("PathClearBtn")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        self.btn_clear.clicked.connect(self._clear)

        row.addWidget(self.line)
        row.addWidget(self.btn_browse)
        row.addWidget(self.btn_clear)

    def retranslate(self):
        self.btn_browse.setText(i18n.t("settings.browse"))
        self.btn_clear.setText("×")
        self.btn_clear.setToolTip(i18n.t("settings.system_default"))
        self.line.setPlaceholderText(i18n.t("settings.system_default"))

    def _browse(self):
        start = self.line.text() or os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(self, i18n.t("settings.browse"), start)
        if path:
            self.line.setText(path)
            self.path_changed.emit(path)

    def _clear(self):
        self.line.setText("")
        self.path_changed.emit("")

    def value(self) -> str:
        return self.line.text()

    def set_value(self, v: str):
        self.line.setText(v or "")


class ThemeSwitcher(QWidget):
    theme_changed = Signal(str)

    ORDER = ["light", "dark"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(False)
        self._current = "light"
        self._build()

    def _build(self):
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self.btn_prev = self._make_arrow("‹")
        self.btn_prev.clicked.connect(lambda: self._step(-1))

        self.value = QLabel()
        self.value.setObjectName("ThemeValue")
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setFixedSize(96, 30)
        self.value.setAutoFillBackground(False)

        self.btn_next = self._make_arrow("›")
        self.btn_next.clicked.connect(lambda: self._step(+1))

        row.addWidget(self.btn_prev)
        row.addWidget(self.value)
        row.addWidget(self.btn_next)
        self.retranslate()

    def _make_arrow(self, text: str) -> QToolButton:
        btn = QToolButton()
        btn.setObjectName("ThemeArrow")
        btn.setText(text)
        btn.setAutoRaise(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(30, 30)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return btn

    def _step(self, direction: int):
        idx = self.ORDER.index(self._current)
        idx = (idx + direction) % len(self.ORDER)
        self._set(idx, emit=True)

    def _set(self, idx: int, emit: bool = False):
        new_theme = self.ORDER[idx]
        if new_theme == self._current:
            return
        self._current = new_theme
        self._refresh_label()
        if emit:
            self.theme_changed.emit(new_theme)

    def _refresh_label(self):
        self.value.setText(i18n.t(f"settings.theme.{self._current}"))

    def set_theme(self, name: str, emit: bool = False):
        if name not in self.ORDER or name == self._current:
            return
        idx = self.ORDER.index(name)
        self._set(idx, emit=emit)

    def retranslate(self):
        self._refresh_label()

    @property
    def current(self) -> str:
        return self._current



class SettingsPage(QWidget):
    theme_requested = Signal(str)
    language_changed = Signal(str)

    GITHUB_URL = "https://github.com/Thesamurrray2k11/SemeryFiles"
    TELEGRAM_URL = "https://t.me/semeryfiles"

    GITHUB_BG_LIGHT = "#2B2B2B"
    GITHUB_BG_DARK = "#FFFFFF"
    GITHUB_ICON_LIGHT = "#FFFFFF"
    GITHUB_ICON_DARK = "#1E1F22"
    TELEGRAM_BG = "#3FA9E0"
    TELEGRAM_ICON = "#FFFFFF"

    ICON_GITHUB = os.path.join(ICONS_DIR, "github.svg")
    ICON_TELEGRAM = os.path.join(ICONS_DIR, "telegram.svg")

    def __init__(self, settings: AppSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._rows: list[SettingRow] = []
        self._lang_buttons: dict[str, QRadioButton] = {}
        self._build()
        self._load_from_settings()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)

        card = QFrame()
        card.setObjectName("WorkspaceCard")
        outer.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("SettingsHeader")
        header.setAutoFillBackground(False)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(40, 32, 40, 8)
        header_layout.setSpacing(6)

        self.title_lbl = QLabel()
        self.title_lbl.setObjectName("WorkspaceTitle")
        self.title_lbl.setAutoFillBackground(False)
        header_layout.addWidget(self.title_lbl)

        self.subtitle_lbl = QLabel()
        self.subtitle_lbl.setObjectName("WorkspaceHint")
        self.subtitle_lbl.setAutoFillBackground(False)
        header_layout.addWidget(self.subtitle_lbl)

        card_layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setObjectName("SettingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        body = QWidget()
        body.setObjectName("SettingsBody")
        body.setAutoFillBackground(False)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(40, 8, 40, 24)
        body_layout.setSpacing(18)

        self._section(body_layout, "settings.section.appearance")

        row_theme = SettingRow("settings.theme", "settings.theme.hint")
        self.theme_switcher = ThemeSwitcher()
        self.theme_switcher.theme_changed.connect(self._on_theme_pick)
        row_theme.add_control(self.theme_switcher)
        body_layout.addWidget(row_theme)
        self._rows.append(row_theme)

        row_remember = SettingRow("settings.remember_theme", "settings.remember_theme.hint")
        self.toggle_remember_theme = ToggleSwitch()
        self.toggle_remember_theme.toggled_on.connect(self._on_remember_theme)
        row_remember.add_control(self.toggle_remember_theme)
        body_layout.addWidget(row_remember)
        self._rows.append(row_remember)

        row_lang = SettingRow("settings.language", None)
        lang_host = QWidget()
        lang_host.setObjectName("RadioHost")
        lang_host.setAutoFillBackground(False)
        lang_layout = QHBoxLayout(lang_host)
        lang_layout.setContentsMargins(0, 0, 0, 0)
        lang_layout.setSpacing(12)

        self._lang_group = QButtonGroup(self)
        for i, lang in enumerate(available_languages()):
            rb = QRadioButton(lang["name"])
            rb.setObjectName("LangRadio")
            rb.setAutoFillBackground(False)
            rb.setProperty("lang_code", lang["code"])
            self._lang_group.addButton(rb, i)
            lang_layout.addWidget(rb)
            self._lang_buttons[lang["code"]] = rb
            rb.toggled.connect(self._on_language_change)

        row_lang.add_control(lang_host)
        body_layout.addWidget(row_lang)
        self._rows.append(row_lang)

        self._section(body_layout, "settings.section.files")

        row_default = SettingRow("settings.default_dir", "settings.default_dir.hint")
        self.picker_default = PathPicker()
        self.picker_default.retranslate()
        self.picker_default.path_changed.connect(
            lambda p: self.settings.set("default_dir", p)
        )
        row_default.add_control(self.picker_default)
        body_layout.addWidget(row_default)
        self._rows.append(row_default)

        row_reports = SettingRow("settings.reports_dir", "settings.reports_dir.hint")
        self.picker_reports = PathPicker()
        self.picker_reports.retranslate()
        self.picker_reports.path_changed.connect(
            lambda p: self.settings.set("reports_dir", p)
        )
        row_reports.add_control(self.picker_reports)
        body_layout.addWidget(row_reports)
        self._rows.append(row_reports)

        self._section(body_layout, "settings.section.format")

        row_units = SettingRow("settings.units", "settings.units.hint")
        units_host = QWidget()
        units_host.setObjectName("RadioHost")
        units_host.setAutoFillBackground(False)
        units_layout = QHBoxLayout(units_host)
        units_layout.setContentsMargins(0, 0, 0, 0)
        units_layout.setSpacing(12)

        self.rb_units_bin = QRadioButton()
        self.rb_units_dec = QRadioButton()
        self.rb_units_bin.setObjectName("LangRadio")
        self.rb_units_dec.setObjectName("LangRadio")
        self.rb_units_bin.setAutoFillBackground(False)
        self.rb_units_dec.setAutoFillBackground(False)
        self._units_group = QButtonGroup(self)
        self._units_group.addButton(self.rb_units_bin, 0)
        self._units_group.addButton(self.rb_units_dec, 1)
        self.rb_units_bin.toggled.connect(self._on_units_change)

        units_layout.addWidget(self.rb_units_bin)
        units_layout.addWidget(self.rb_units_dec)
        row_units.add_control(units_host)
        body_layout.addWidget(row_units)
        self._rows.append(row_units)

        body_layout.addStretch(1)

        links_row = QHBoxLayout()
        links_row.setContentsMargins(0, 8, 0, 0)
        links_row.setSpacing(28)
        links_row.addStretch(1)

        self.btn_github = RoundLinkButton(
            icon_path=self.ICON_GITHUB,
            bg_color=self.GITHUB_BG_LIGHT,
            icon_color=self.GITHUB_ICON_LIGHT,
            size=56, icon_size=28,
        )
        self.btn_github.clicked.connect(lambda: self._open(self.GITHUB_URL))

        self.btn_telegram = RoundLinkButton(
            icon_path=self.ICON_TELEGRAM,
            bg_color=self.TELEGRAM_BG,
            icon_color=self.TELEGRAM_ICON,
            size=56, icon_size=28,
        )
        self.btn_telegram.clicked.connect(lambda: self._open(self.TELEGRAM_URL))

        links_row.addWidget(self.btn_github)
        links_row.addWidget(self.btn_telegram)
        links_row.addStretch(1)
        body_layout.addLayout(links_row)

        scroll.setWidget(body)
        card_layout.addWidget(scroll, 1)

        self._retranslate()

    def _section(self, layout: QVBoxLayout, title_key: str):
        sep = QFrame()
        sep.setObjectName("SettingsSep")
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        lbl = QLabel(i18n.t(title_key))
        lbl.setObjectName("SettingsSection")
        lbl.setAutoFillBackground(False)
        layout.addWidget(lbl)

    def _load_from_settings(self):
        s = self.settings

        self.theme_switcher.set_theme(s.theme, emit=False)

        self.toggle_remember_theme.blockSignals(True)
        self.toggle_remember_theme.setChecked(s.remember_theme)
        self.toggle_remember_theme.set_t(1.0 if s.remember_theme else 0.0)
        self.toggle_remember_theme.blockSignals(False)

        rb = self._lang_buttons.get(s.language)
        if rb:
            rb.setChecked(True)

        # Папки
        self.picker_default.set_value(s.default_dir)
        self.picker_reports.set_value(s.reports_dir)

        if s.size_units == "decimal":
            self.rb_units_dec.setChecked(True)
        else:
            self.rb_units_bin.setChecked(True)

        self.apply_theme(s.theme)

    def _on_theme_pick(self, name: str):
        self.theme_requested.emit(name)
        if self.settings.remember_theme:
            self.settings.set("theme", name)

    def _on_remember_theme(self, value: bool):
        self.settings.set("remember_theme", value)
        if value:
            self.settings.set("theme", self.theme_switcher.current)

    def _on_language_change(self):
        for code, rb in self._lang_buttons.items():
            if rb.isChecked() and code != self.settings.language:
                self.settings.set("language", code)
                i18n.set_language(code)
                self.language_changed.emit(code)
                self._retranslate()
                break

    def _on_units_change(self):
        if not self.rb_units_bin.isChecked() and not self.rb_units_dec.isChecked():
            return
        value = "binary" if self.rb_units_bin.isChecked() else "decimal"
        if value == self.settings.size_units:
            return
        self.settings.set("size_units", value)

    def _retranslate(self):
        self.title_lbl.setText(i18n.t("settings.title"))
        self.subtitle_lbl.setText(i18n.t("settings.subtitle"))

        self.rb_units_bin.setText(i18n.t("settings.units.binary"))
        self.rb_units_dec.setText(i18n.t("settings.units.decimal"))

        for row in self._rows:
            row.retranslate()
        self.theme_switcher.retranslate()
        self.picker_default.retranslate()
        self.picker_reports.retranslate()

        self.btn_github.set_tooltip(i18n.t("settings.github.tip"))
        self.btn_telegram.set_tooltip(i18n.t("settings.telegram.tip"))

    def _open(self, url: str):
        QDesktopServices.openUrl(QUrl(url))

    def sync_theme(self, name: str):
        self.theme_switcher.set_theme(name, emit=False)
        self.apply_theme(name)

    def apply_theme(self, name: str):
        if name == "dark":
            self.btn_github.set_colors(self.GITHUB_BG_DARK, self.GITHUB_ICON_DARK)
        else:
            self.btn_github.set_colors(self.GITHUB_BG_LIGHT, self.GITHUB_ICON_LIGHT)
        self.btn_telegram.set_colors(self.TELEGRAM_BG, self.TELEGRAM_ICON)

    def update_toggle_palette(self, colors: dict):
        if not hasattr(self, "toggle_remember_theme"):
            return
        self.toggle_remember_theme.set_palette(
            bg_off=colors.get("border", "#D6D6D2"),
            bg_on=colors.get("success", "#7A9B6B"),
            knob="#FFFFFF",
        )