from PySide6.QtCore import Qt, QEvent, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QStatusBar, QLabel,
    QGraphicsOpacityEffect, QApplication
)

from .title_bar import TitleBar
from .sidebar import Sidebar
from .workspace import Workspace
from .theme import ThemeManager
from .styles import qss_for
from core.settings import AppSettings
from core.i18n import i18n


class MainWindow(QWidget):
    THEME_FADE_MS = 220

    def __init__(self):
        super().__init__()

        self.setWindowTitle("SemeryFiles")
        self.setMinimumSize(900, 560)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.app_settings = AppSettings()
        i18n.set_language(self.app_settings.language)

        initial_theme = (
            self.app_settings.theme
            if self.app_settings.remember_theme
            else "light"
        )
        self.theme = ThemeManager()
        self.theme._current = initial_theme
        self.theme.changed.connect(self._apply_theme_smooth)
        self.setStyleSheet(qss_for(initial_theme))

        self._overlay = None
        self._overlay_anim = None

        self._nav_history: list[tuple[str, str]] = []
        self._nav_index: int = -1
        self._nav_locked: bool = False

        self._build()
        self.workspace.apply_colors(self.theme.colors, initial_theme)
        self._apply_initial_geometry()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.title_bar = TitleBar("SemeryFiles", self)
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self._toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        root.addWidget(self.title_bar)

        self._content = QWidget()
        self._content.setObjectName("ContentRoot")
        content_row = QHBoxLayout(self._content)
        content_row.setContentsMargins(0, 0, 0, 0)
        content_row.setSpacing(0)

        self.sidebar = Sidebar()
        self.workspace = Workspace(self.app_settings)

        content_row.addWidget(self.sidebar)
        content_row.addWidget(self.workspace, 1)
        root.addWidget(self._content, 1)

        self.status = QStatusBar()
        root.addWidget(self.status)

        self.sidebar.tool_selected.connect(self._navigate_to)
        self.sidebar.home_requested.connect(self._show_home)
        self.workspace.theme_requested.connect(self.theme.set_theme)
        self.workspace.language_changed.connect(self._on_language_changed)


        if hasattr(self.workspace, "tool_opened"):
            self.workspace.tool_opened.connect(self._on_workspace_opened)
    def _on_language_changed(self, code: str):
        self.setWindowTitle(i18n.t("app.name"))

        self.workspace.retranslate_all()

        if hasattr(self.sidebar, "retranslate"):
            self.sidebar.retranslate()

        self.status.showMessage(i18n.t("common.done"), 1500)
    def _apply_initial_geometry(self):
        screen = self.screen() or QApplication.primaryScreen()
        if screen is None:
            self.resize(1400, 900)
            return
        avail = screen.availableGeometry()
        w = max(int(avail.width() * 0.9), self.minimumWidth())
        h = max(int(avail.height() * 0.9), self.minimumHeight())
        x = avail.x() + (avail.width() - w) // 2
        y = avail.y() + (avail.height() - h) // 2
        self.setGeometry(x, y, w, h)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def _show_home(self):
        self._push_history("home", "Главная")
        self.sidebar.clear_selection()
        self.workspace.show_tool("home", "Главная")

    def _navigate_to(self, tool_id: str, tool_name: str):
        self._push_history(tool_id, tool_name)
        self.workspace.show_tool(tool_id, tool_name)

    def _on_workspace_opened(self, tool_id: str, tool_name: str):
        self._push_history(tool_id, tool_name)

    def _push_history(self, tool_id: str, tool_name: str):
        if self._nav_locked:
            return
        if self._nav_index < len(self._nav_history) - 1:
            self._nav_history = self._nav_history[: self._nav_index + 1]
        if self._nav_history and self._nav_history[-1][0] == tool_id:
            return
        self._nav_history.append((tool_id, tool_name))
        self._nav_index = len(self._nav_history) - 1

    def _go_back(self):
        if self._nav_index <= 0:
            return
        self._nav_index -= 1
        self._apply_history()
        self.status.showMessage(f"← {self._nav_history[self._nav_index][1]}", 1500)

    def _go_forward(self):
        if self._nav_index >= len(self._nav_history) - 1:
            return
        self._nav_index += 1
        self._apply_history()
        self.status.showMessage(f"→ {self._nav_history[self._nav_index][1]}", 1500)

    def _apply_history(self):
        tool_id, tool_name = self._nav_history[self._nav_index]
        self._nav_locked = True
        try:
            self.sidebar.clear_selection()
            self.workspace.show_tool(tool_id, tool_name)
        finally:
            self._nav_locked = False

    def mousePressEvent(self, event):
        btn = event.button()
        if btn == Qt.BackButton:
            self._go_back()
            event.accept()
            return
        if btn == Qt.ForwardButton:
            self._go_forward()
            event.accept()
            return
        super().mousePressEvent(event)

    def _apply_theme_smooth(self, name: str):
        self._remove_overlay()
        central = self._content
        pixmap = central.grab()

        overlay = QLabel(central)
        overlay.setPixmap(pixmap)
        overlay.setScaledContents(True)
        overlay.setGeometry(central.rect())
        overlay.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        overlay.show()
        overlay.raise_()

        eff = QGraphicsOpacityEffect(overlay)
        eff.setOpacity(1.0)
        overlay.setGraphicsEffect(eff)
        self._overlay = overlay

        self.setStyleSheet(qss_for(name))
        self.workspace.sync_theme(name)
        self.workspace.apply_colors(self.theme.colors, name)

        anim = QPropertyAnimation(eff, b"opacity", self)
        anim.setDuration(self.THEME_FADE_MS)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(self._remove_overlay)
        anim.start()
        self._overlay_anim = anim

    def _remove_overlay(self):
        if self._overlay_anim is not None:
            self._overlay_anim.stop()
            self._overlay_anim = None
        if self._overlay is not None:
            self._overlay.hide()
            self._overlay.deleteLater()
            self._overlay = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._overlay is not None:
            self._overlay.setGeometry(self._content.rect())