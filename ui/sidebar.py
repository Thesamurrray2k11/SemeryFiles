from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton,
    QFrame, QSizePolicy
)

from tools.registry import MAIN_TOOLS


class Sidebar(QWidget):
    tool_selected = Signal(str, str)
    home_requested = Signal()

    WIDTH = 72
    LOGO_SIZE = 40
    TOOL_HEIGHT = 46

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(self.WIDTH)
        self._buttons: dict[str, QToolButton] = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.logo_btn = QToolButton()
        self.logo_btn.setObjectName("SidebarLogo")
        self.logo_btn.setText("SF")
        self.logo_btn.setCursor(Qt.PointingHandCursor)
        self.logo_btn.setAutoRaise(True)
        self.logo_btn.setFixedSize(self.LOGO_SIZE, self.LOGO_SIZE)
        self.logo_btn.setToolTip(
            "<b>SemeryFiles</b><br>О программе и список возможностей."
        )
        self.logo_btn.clicked.connect(self.home_requested.emit)

        logo_row = QHBoxLayout()
        logo_row.setContentsMargins(0, 14, 0, 8)
        logo_row.setSpacing(0)
        logo_row.addStretch(1)
        logo_row.addWidget(self.logo_btn)
        logo_row.addStretch(1)
        layout.addLayout(logo_row)

        sep = QFrame()
        sep.setObjectName("SidebarSep")
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)
        layout.addSpacing(4)

        for t in MAIN_TOOLS:
            btn = self._make_button(
                t["icon"],
                f"<b>{t['name']}</b><br>{t['desc']}"
            )
            btn.setProperty("colorKey", t["color"])
            btn.clicked.connect(
                lambda _=False, tid=t["id"], tname=t["name"]: self._select(tid, tname)
            )
            layout.addWidget(btn)
            self._buttons[t["id"]] = btn

        layout.addStretch(1)

        sep2 = QFrame()
        sep2.setObjectName("SidebarSep")
        sep2.setFrameShape(QFrame.HLine)
        layout.addWidget(sep2)
        layout.addSpacing(4)

        search_btn = self._make_button(
            "🔎",
            "<b>Поиск инструментов</b><br>Найдите инструмент по названию или описанию."
        )
        search_btn.setProperty("colorKey", "c_settings")
        search_btn.clicked.connect(lambda: self._select("search", "Поиск"))
        layout.addWidget(search_btn)
        self._buttons["search"] = search_btn

        settings_btn = self._make_button(
            "⚙",
            "<b>Настройки</b><br>Тема, язык, папки и другие параметры."
        )
        settings_btn.setProperty("colorKey", "c_settings")
        settings_btn.clicked.connect(lambda: self._select("settings", "Настройки"))
        layout.addWidget(settings_btn)
        self._buttons["settings"] = settings_btn

        layout.addSpacing(10)

    def _make_button(self, icon: str, tooltip: str) -> QToolButton:
        btn = QToolButton()
        btn.setObjectName("ToolButton")
        btn.setText(icon)
        btn.setCheckable(True)
        btn.setAutoRaise(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setFixedHeight(self.TOOL_HEIGHT)
        btn.setToolTip(tooltip)
        return btn

    def _select(self, tool_id: str, tool_name: str):
        for tid, btn in self._buttons.items():
            btn.setChecked(tid == tool_id)
        self.tool_selected.emit(tool_id, tool_name)

    def clear_selection(self):
        for btn in self._buttons.values():
            btn.setChecked(False)
    def retranslate(self):
        from core.i18n import i18n

        self.logo_btn.setToolTip(
            i18n.t("sidebar.logo.tip")
        )

        for t in MAIN_TOOLS:
            btn = self._buttons.get(t["id"])
            if btn is None:
                continue
            name = i18n.t(f"tool.{t['id']}.name", t["name"])
            desc = i18n.t(f"tool.{t['id']}.desc", t["desc"])
            btn.setToolTip(f"<b>{name}</b><br>{desc}")

        if "search" in self._buttons:
            self._buttons["search"].setToolTip(
                f"<b>{i18n.t('sidebar.search.name')}</b><br>"
                f"{i18n.t('sidebar.search.desc')}"
            )
        if "settings" in self._buttons:
            self._buttons["settings"].setToolTip(
                f"<b>{i18n.t('sidebar.settings.name')}</b><br>"
                f"{i18n.t('sidebar.settings.desc')}"
            )