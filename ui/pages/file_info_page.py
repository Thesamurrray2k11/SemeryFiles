import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QScrollArea, QSizePolicy
)

from tools.info import collect_info
from core.i18n import i18n


class DropZone(QFrame):

    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel("⇩")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("info.drop_hint"))
        self.text_lbl.setObjectName("DropZoneText")
        self.text_lbl.setAlignment(Qt.AlignCenter)
        self.text_lbl.setAutoFillBackground(False)
        layout.addWidget(self.text_lbl)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("hovered", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)

        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if path and os.path.isfile(path):
                self.file_dropped.emit(path)
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.file_dropped.emit("__browse__")
        super().mousePressEvent(event)


class FileInfoPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._build()
        self._show_empty()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)
        outer.setSpacing(0)

        card = QFrame()
        card.setObjectName("WorkspaceCard")
        outer.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        top = QWidget()
        top.setObjectName("InfoTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("info.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("info.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("InfoDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        scroll = QScrollArea()
        scroll.setObjectName("InfoScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.result_host = QWidget()
        self.result_host.setObjectName("InfoResultHost")
        self.result_host.setAutoFillBackground(False)

        self.result_layout = QVBoxLayout(self.result_host)
        self.result_layout.setContentsMargins(36, 8, 36, 24)
        self.result_layout.setSpacing(20)
        self.result_layout.addStretch(1)

        scroll.setWidget(self.result_host)
        card_layout.addWidget(scroll, 1)

        self._scroll = scroll

    def retranslate(self):
        self.btn_browse.setText(i18n.t("info.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("info.drop_hint"))
        if self._current_path:
            self.show_file(self._current_path)

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("info.browse"), start
        )
        if path:
            self.show_file(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self.show_file(path)

    def show_file(self, path: str):
        self._current_path = path
        data = collect_info(
            path,
            units=self.settings.size_units,
            hash_algo="sha256",
        )

        self._clear_results()

        if not data["ok"]:
            self._show_error(data.get("error", "unknown"))
            return

        for group in data["groups"]:
            self.result_layout.insertWidget(
                self.result_layout.count() - 1,
                self._build_group(group)
            )

    def _show_empty(self):
        self._clear_results()
        hint = QLabel(i18n.t("info.empty"))
        hint.setObjectName("InfoEmpty")
        hint.setAlignment(Qt.AlignCenter)
        hint.setAutoFillBackground(False)
        self.result_layout.insertWidget(0, hint)

    def _show_error(self, err: str):
        lbl = QLabel(f"{i18n.t('info.error')}: {err}")
        lbl.setObjectName("InfoError")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setAutoFillBackground(False)
        self.result_layout.insertWidget(0, lbl)

    def _build_group(self, group: dict) -> QWidget:
        host = QWidget()
        host.setObjectName("InfoGroup")
        host.setAutoFillBackground(False)

        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel(i18n.t(group["title_key"]))
        title.setObjectName("InfoGroupTitle")
        title.setAutoFillBackground(False)
        layout.addWidget(title)

        grid_host = QWidget()
        grid_host.setObjectName("InfoGrid")
        grid_host.setAutoFillBackground(False)

        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        for i, (label_key, value) in enumerate(group["rows"]):
            key_lbl = QLabel(self._tr_label(label_key))
            key_lbl.setObjectName("InfoKey")
            key_lbl.setAutoFillBackground(False)
            key_lbl.setMinimumWidth(160)
            key_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)

            val_lbl = QLabel(str(value))
            val_lbl.setObjectName("InfoValue")
            val_lbl.setAutoFillBackground(False)
            val_lbl.setWordWrap(True)
            val_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

            grid.addWidget(key_lbl, i, 0)
            grid.addWidget(val_lbl, i, 1)

        layout.addWidget(grid_host)
        return host

    def _tr_label(self, key_or_text: str) -> str:
        if key_or_text.startswith("info."):
            return i18n.t(key_or_text)
        return key_or_text

    def _clear_results(self):
        while self.result_layout.count() > 1:
            item = self.result_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()