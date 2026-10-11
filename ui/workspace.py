from PySide6.QtCore import Qt, Signal, QVariantAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QStackedWidget, QToolButton
)


from .settings_page import SettingsPage
from .search_page import SearchPage
from .pages.file_info_page import FileInfoPage
from .pages.hash_page import HashPage
from .pages.meta_page import MetaPage
from .pages.convert_page import ConvertPage
from .pages.hex_page import HexPage
from .pages.permissions_page import PermissionsPage
from .pages.regex_page import RegexPage
from .pages.encoding_page import EncodingPage
from .pages.sqlite_page import SqlitePage
from .pages.password_page import PasswordPage
from core.settings import AppSettings
from .pages.font_page import FontPage
from .pages.exif_clean_page import ExifCleanPage
from .pages.qr_page import QrPage
from .pages.stego_page import StegoPage
from .pages.base64_page import Base64Page


class HomePage(QWidget):

    VERSION = "1.0.0"
    CARDS_COUNT = 6
    COLS = 3

    tool_chosen = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._colors: dict | None = None
        self._cards: list[QuickToolCard] = []
        self._build()
        self._fill_cards()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("WorkspaceCard")
        outer.addWidget(card)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(48, 40, 48, 32)
        inner.setSpacing(0)

        title = QLabel("SemeryFiles")
        title.setObjectName("HomeTitle")
        title.setAlignment(Qt.AlignCenter)
        title.setAutoFillBackground(False)
        inner.addWidget(title)

        version = QLabel(f"ВЕРСИЯ  {self.VERSION}")
        version.setObjectName("HomeVersion")
        version.setAlignment(Qt.AlignCenter)
        version.setAutoFillBackground(False)
        inner.addSpacing(6)
        inner.addWidget(version)

        desc = QLabel(
            "Набор инструментов для разработчиков, работающих "
            "с файлом или системой файлов.\nМы имеем 20+ инструментов, которые впоследствии пригодятся вам) "
        )
        desc.setObjectName("HomeDesc")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setAutoFillBackground(False)
        inner.addSpacing(20)
        inner.addWidget(desc)

        grid_title = QLabel("БЫСТРЫЙ ДОСТУП")
        grid_title.setObjectName("HomeSection")
        grid_title.setAutoFillBackground(False)
        inner.addSpacing(28)
        inner.addWidget(grid_title)

        self.grid_host = QWidget()
        self.grid_host.setObjectName("QuickGridHost")
        self.grid_host.setAutoFillBackground(False)

        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(0, 12, 0, 0)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)

        inner.addWidget(self.grid_host)

        inner.addStretch(1)

        hint = QLabel(
            "Выберите инструмент на панели инструментов  •  или откройте поиск ⌕"
        )
        hint.setObjectName("HomeHint")
        hint.setAlignment(Qt.AlignCenter)
        hint.setAutoFillBackground(False)
        inner.addSpacing(20)
        inner.addWidget(hint)

    def _fill_cards(self):
        import random
        from tools.registry import ALL_TOOLS

        implemented = [t for t in ALL_TOOLS if t.get("impl")]

        if not implemented:
            return

        n = min(self.CARDS_COUNT, len(implemented))
        picked = random.sample(implemented, n)

        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        self._cards.clear()

        for i, tool in enumerate(picked):
            row = i // self.COLS
            col = i % self.COLS

            card = QuickToolCard(tool)
            card.clicked.connect(self._on_card_clicked)
            if self._colors:
                card.apply_theme(self._colors)

            self.grid.addWidget(card, row, col)
            self._cards.append(card)

        for c in range(self.COLS):
            self.grid.setColumnStretch(c, 1)

    def _on_card_clicked(self, tool_id: str):
        from tools.registry import get_tool
        t = get_tool(tool_id)
        if t:
            self.tool_chosen.emit(t["id"], t["name"])

    def apply_theme(self, colors: dict):
        self._colors = colors
        for card in self._cards:
            card.apply_theme(colors)


class PlaceholderPage(QWidget):
    def __init__(self, title: str, hint: str, color_key: str = None,
                 icon: str = None, subtitle: str = None, parent=None):
        super().__init__(parent)
        self._color_key = color_key
        self._build(title, hint, icon, subtitle)

    def _build(self, title, hint, icon, subtitle):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)

        card = QFrame()
        card.setObjectName("WorkspaceCard")
        outer.addWidget(card)

        card_row = QHBoxLayout(card)
        card_row.setContentsMargins(0, 0, 0, 0)
        card_row.setSpacing(0)

        if self._color_key:
            stripe = QFrame()
            stripe.setObjectName("AccentStripe")
            stripe.setFixedWidth(4)
            stripe.setProperty("colorKey", self._color_key)
            card_row.addWidget(stripe)

        content = QWidget()
        content.setObjectName("PlaceholderContent")
        content.setAutoFillBackground(False)
        card_row.addWidget(content, 1)

        inner = QVBoxLayout(content)
        inner.setContentsMargins(40, 40, 40, 40)
        inner.setSpacing(12)

        if icon:
            badge = QLabel(icon)
            badge.setObjectName("PageBadge")
            badge.setProperty("colorKey", self._color_key or "c_info")
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedSize(56, 56)
            inner.addWidget(badge, alignment=Qt.AlignCenter)

        t = QLabel(title)
        t.setObjectName("WorkspaceTitle")
        t.setAlignment(Qt.AlignCenter)
        t.setAutoFillBackground(False)

        h = QLabel(hint)
        h.setObjectName("WorkspaceHint")
        h.setAlignment(Qt.AlignCenter)
        h.setAutoFillBackground(False)

        inner.addStretch(1)
        inner.addWidget(t)
        inner.addWidget(h)
        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("WorkspaceSubtitle")
            s.setAlignment(Qt.AlignCenter)
            s.setAutoFillBackground(False)
            inner.addWidget(s)
        inner.addStretch(2)

    def apply_theme(self, colors: dict):
        if not self._color_key:
            return
        color = colors.get(self._color_key, colors.get("accent", "#5B7C99"))

        for stripe in self.findChildren(QFrame, "AccentStripe"):
            stripe.setStyleSheet(
                f"#AccentStripe {{ background-color: {color}; "
                f"border-top-left-radius: 14px; "
                f"border-bottom-left-radius: 14px; }}"
            )
        for badge in self.findChildren(QLabel, "PageBadge"):
            badge.setStyleSheet(
                f"#PageBadge {{ background-color: {color}; color: #FFFFFF; "
                f"border-radius: 28px; font-size: 24px; font-weight: 600; }}"
            )


class _TransitionOverlay(QWidget):
    DURATION = 240

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAutoFillBackground(False)
        self.hide()

        self._pixmap: QPixmap | None = None
        self._offset_x = 0
        self._anim: QVariantAnimation | None = None

    def start(self, pixmap: QPixmap, direction: int):
        self._pixmap = pixmap
        self._offset_x = 0
        self.setGeometry(self.parentWidget().rect())
        self.show()
        self.raise_()

        anim = QVariantAnimation(self)
        anim.setDuration(self.DURATION)
        anim.setStartValue(0)
        anim.setEndValue(-direction * self.width())
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.valueChanged.connect(self._on_offset)
        anim.finished.connect(self._on_finished)
        anim.start()
        self._anim = anim

    def _on_offset(self, value):
        self._offset_x = int(value)
        self.update()

    def _on_finished(self):
        self.hide()
        self._pixmap = None
        self._offset_x = 0
        self._anim = None

    def paintEvent(self, event):
        if self._pixmap is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.drawPixmap(self._offset_x, 0, self._pixmap)
        painter.end()


class Workspace(QWidget):
    theme_requested = Signal(str)
    language_changed = Signal(str)
    tool_opened = Signal(str, str)

    def __init__(self, app_settings: AppSettings, parent=None):
        super().__init__(parent)
        self.setObjectName("Workspace")

        self._app_settings = app_settings
        self._pages: dict[str, int] = {}
        self._order: list[str] = []
        self._busy = False
        self._colors: dict | None = None

        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.setSpacing(0)

        self._host = QWidget(self)
        self._host.setObjectName("WorkspaceHost")
        self._host.setAutoFillBackground(False)
        outer.addWidget(self._host)

        self.stack = QStackedWidget(self._host)
        self.stack.setGeometry(0, 0, 0, 0)

        self._overlay = _TransitionOverlay(self._host)

        from tools.registry import ALL_TOOLS

        self.home_page = HomePage()
        self.home_page.tool_chosen.connect(self._on_search_choice)
        self._add_page("home", self.home_page)

        for t in ALL_TOOLS:
            impl = t.get("impl")
            if impl == "info":
                page = FileInfoPage(self._app_settings)
            elif impl == "hash":
                page = HashPage(self._app_settings)
            elif impl == "meta":
                page = MetaPage(self._app_settings)
            elif impl == "convert":
                page = ConvertPage(self._app_settings)
            elif impl == "hex":
                page = HexPage(self._app_settings)
            elif impl == "permissions":
                page = PermissionsPage(self._app_settings)
            elif impl == "regex":
                page = RegexPage(self._app_settings)
            elif impl == "encoding":
                page = EncodingPage(self._app_settings)
            elif impl == "sqlite":
                page = SqlitePage(self._app_settings)
            elif impl == "password":
                page = PasswordPage(self._app_settings)
            elif impl == "fonts":
                page = FontPage(self._app_settings)
            elif impl == "exif_clean":
                page = ExifCleanPage(self._app_settings)
            elif impl == "qr":
                page = QrPage(self._app_settings)
            elif impl == "stego":
                page = StegoPage(self._app_settings)
            elif impl == "base64":
                page = Base64Page(self._app_settings)
            else:
                page = PlaceholderPage(
                    t["name"],
                    "Инструмент пока не реализован — идёт работа над интерфейсом.",
                    color_key=t["color"],
                    icon=t["icon"],
                    subtitle=t["desc"],
                )
            self._add_page(t["id"], page)

        self.search_page = SearchPage()
        self.search_page.tool_chosen.connect(self._on_search_choice)
        self._add_page("search", self.search_page)

        self.settings_page = SettingsPage(self._app_settings)
        self.settings_page.theme_requested.connect(self.theme_requested.emit)
        self.settings_page.language_changed.connect(self.language_changed.emit)
        self._add_page("settings", self.settings_page)

    def _add_page(self, key: str, widget: QWidget):
        self._pages[key] = self.stack.count()
        self._order.append(key)
        self.stack.addWidget(widget)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.stack.setGeometry(0, 0, self._host.width(), self._host.height())
        self._overlay.setGeometry(0, 0, self._host.width(), self._host.height())

    def show_tool(self, tool_id: str, tool_name: str):
        target = self._pages.get(tool_id)
        if target is None or target == self.stack.currentIndex():
            return
        if self._busy:
            self.stack.setCurrentIndex(target)
            return
        current_key = self._order[self.stack.currentIndex()]
        direction = 1 if self._order.index(tool_id) > self._order.index(current_key) else -1
        self._transition_to(target, direction)

    def sync_theme(self, name: str):
        self.settings_page.sync_theme(name)

    def apply_colors(self, colors: dict, theme_name: str = "light"):
        self._colors = colors
        for key in self._order:
            page = self.stack.widget(self._pages[key])
            if hasattr(page, "apply_theme"):
                page.apply_theme(colors)
            if hasattr(page, "retranslate"):
                page.retranslate()
        if hasattr(self, "settings_page"):
            self.settings_page.apply_theme(theme_name)
            if hasattr(self.settings_page, "update_toggle_palette"):
                self.settings_page.update_toggle_palette(colors)
        if hasattr(self, "search_page"):
            self.search_page.apply_colors(colors)

    def _on_search_choice(self, tool_id: str, tool_name: str):
        self.tool_opened.emit(tool_id, tool_name)
        self.show_tool(tool_id, tool_name)

    def _transition_to(self, index: int, direction: int):
        self._busy = True
        current = self.stack.currentWidget()
        pixmap = current.grab()

        self._overlay.setGeometry(0, 0, self._host.width(), self._host.height())
        self._overlay.start(pixmap, direction)
        self.stack.setCurrentIndex(index)

        QTimer.singleShot(_TransitionOverlay.DURATION + 10, self._on_done)

    def _on_done(self):
        self._busy = False
    def retranslate_all(self):
        for key in self._order:
            page = self.stack.widget(self._pages[key])
            if hasattr(page, "retranslate"):
                try:
                    page.retranslate()
                except Exception as e:
                    print(f"[i18n] retranslate error in {key}: {e}")
class QuickToolCard(QFrame):

    clicked = Signal(str)

    def __init__(self, tool: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("QuickCard")
        self.setCursor(Qt.PointingHandCursor)
        self._tool = tool
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.icon_lbl = QLabel(self._tool["icon"])
        self.icon_lbl.setObjectName("QuickCardIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setFixedSize(48, 48)
        self.icon_lbl.setAutoFillBackground(False)
        self.icon_lbl.setProperty("colorKey", self._tool.get("color", "c_info"))
        layout.addWidget(self.icon_lbl, alignment=Qt.AlignLeft)

        name = QLabel(self._tool["name"])
        name.setObjectName("QuickCardName")
        name.setAutoFillBackground(False)
        name.setWordWrap(True)
        layout.addWidget(name)

        desc = QLabel(self._tool["desc"])
        desc.setObjectName("QuickCardDesc")
        desc.setAutoFillBackground(False)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch(1)

    def apply_theme(self, colors: dict):
        color = colors.get(self._tool.get("color", "c_info"),
                           colors.get("accent", "#5B7C99"))
        self.icon_lbl.setStyleSheet(
            f"#QuickCardIcon {{"
            f"  background-color: {color};"
            f"  color: #FFFFFF;"
            f"  border-radius: 12px;"
            f"  font-size: 22px;"
            f"  font-weight: 700;"
            f"}}"
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._tool["id"])
        super().mousePressEvent(event)