from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QScrollArea, QFrame, QSizePolicy, QPushButton, QButtonGroup
)

from tools.registry import get_tool, search_tools, list_groups
from .theme import LIGHT


class ToolCard(QFrame):

    clicked = Signal(str)

    def __init__(self, tool: dict, colors: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("ToolCard")
        self.setCursor(Qt.PointingHandCursor)
        self._tool = tool
        self._colors = colors or LIGHT
        self._build()

    def _build(self):
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(14)

        badge = QLabel(self._tool["icon"])
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(36, 36)

        color = (
            self._colors.get(self._tool.get("color"))
            or self._colors.get("accent")
            or "#5B7C99"
        )
        badge.setStyleSheet(
            f"background-color: {color}; color: #FFFFFF; "
            f"border-radius: 10px; font-size: 16px; font-weight: 600;"
        )

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)

        name = QLabel(self._tool["name"])
        name.setObjectName("ToolCardName")
        name.setAutoFillBackground(False)

        desc = QLabel(self._tool["desc"])
        desc.setObjectName("ToolCardDesc")
        desc.setWordWrap(True)
        desc.setAutoFillBackground(False)

        text_col.addWidget(name)
        text_col.addWidget(desc)

        group = QLabel(self._tool.get("group", ""))
        group.setObjectName("ToolCardGroup")
        group.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        group.setAutoFillBackground(False)

        row.addWidget(badge)
        row.addLayout(text_col, 1)
        row.addWidget(group)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._tool["id"])
        super().mousePressEvent(event)


class SearchPage(QWidget):

    tool_chosen = Signal(str, str)

    ALL_LABEL_KEY = "search.filter.all"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._colors = LIGHT
        self._current_group: str | None = None
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)

        card = QFrame()
        card.setObjectName("WorkspaceCard")
        outer.addWidget(card)

        inner = QVBoxLayout(card)
        inner.setContentsMargins(36, 32, 36, 32)
        inner.setSpacing(14)

        title = QLabel("Поиск инструментов")
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)
        inner.addWidget(title)

        hint = QLabel(
            "Введите название или ключевое слово. "
            "Например: «хеш», «метаданные», «кодировка»."
        )
        hint.setObjectName("WorkspaceHint")
        hint.setWordWrap(True)
        hint.setAutoFillBackground(False)
        inner.addWidget(hint)

        self.input = QLineEdit()
        self.input.setObjectName("SearchInput")
        self.input.setPlaceholderText("Поиск…")
        self.input.setClearButtonEnabled(True)
        self.input.textChanged.connect(self._refresh)
        inner.addWidget(self.input)

        self.chips_host = QWidget()
        self.chips_host.setObjectName("SearchChipsHost")
        self.chips_host.setAutoFillBackground(False)

        self.chips_layout = QHBoxLayout(self.chips_host)
        self.chips_layout.setContentsMargins(0, 0, 0, 0)
        self.chips_layout.setSpacing(8)

        self._chip_group = QButtonGroup(self)
        self._chip_group.setExclusive(True)
        self._chips: list[QPushButton] = []

        self._add_chip(self.ALL_LABEL_KEY, None)
        for group in list_groups():
            self._add_chip(group, group)

        inner.addWidget(self.chips_host)

        scroll = QScrollArea()
        scroll.setObjectName("SearchScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.list_host = QWidget()
        self.list_host.setObjectName("SearchListHost")
        self.list_host.setAutoFillBackground(False)

        self.list_layout = QVBoxLayout(self.list_host)
        self.list_layout.setContentsMargins(0, 0, 8, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch(1)

        scroll.setWidget(self.list_host)
        inner.addWidget(scroll, 1)

        self._scroll = scroll
        self._refresh("")

    def _add_chip(self, label_or_key: str, group_value: str | None):
        from core.i18n import i18n

        if label_or_key.startswith("search."):
            text = i18n.t(label_or_key)
        else:
            text = label_or_key

        btn = QPushButton(text)
        btn.setObjectName("SearchChip")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("group_value", group_value)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._chip_group.addButton(btn)
        self.chips_layout.addWidget(btn)
        self._chips.append(btn)

        if group_value is None:
            btn.setChecked(True)

        btn.toggled.connect(self._on_chip_toggled)
        return btn

    def _on_chip_toggled(self, checked: bool):
        if not checked:
            return
        sender = self.sender()
        if sender is None:
            return
        self._current_group = sender.property("group_value")
        self._refresh(self.input.text())

    def _refresh(self, text: str):
        # Очистка списка
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        results = search_tools(text, group=self._current_group)

        if not results:
            empty = QLabel("Ничего не найдено")
            empty.setObjectName("SearchEmpty")
            empty.setAlignment(Qt.AlignCenter)
            empty.setAutoFillBackground(False)
            self.list_layout.insertWidget(0, empty)
            return

        colors = self._colors or LIGHT
        for tool in results:
            card = ToolCard(tool, colors)
            card.clicked.connect(self._on_card_clicked)
            self.list_layout.insertWidget(self.list_layout.count() - 1, card)

    def _on_card_clicked(self, tool_id: str):
        t = get_tool(tool_id)
        if t:
            self.tool_chosen.emit(t["id"], t["name"])

    def apply_colors(self, colors: dict):
        self._colors = colors or LIGHT
        self._refresh(self.input.text())

    def retranslate(self):
        from core.i18n import i18n
        if self._chips:
            self._chips[0].setText(i18n.t(self.ALL_LABEL_KEY))
        self._refresh(self.input.text())