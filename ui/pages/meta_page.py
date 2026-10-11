import os

from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDesktopServices
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QScrollArea, QSizePolicy, QMessageBox
)

from tools.metadata import collect_metadata, is_image, IMAGE_EXTENSIONS
from core.i18n import i18n


class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel("🖼")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("meta.drop_hint"))
        self.text_lbl.setObjectName("DropZoneText")
        self.text_lbl.setAlignment(Qt.AlignCenter)
        self.text_lbl.setAutoFillBackground(False)
        layout.addWidget(self.text_lbl)

    def _accepts(self, path: str) -> bool:
        return os.path.isfile(path) and is_image(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and self._accepts(urls[0].toLocalFile()):
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
            if self._accepts(path):
                self.file_dropped.emit(path)
            else:
                QMessageBox.warning(
                    self, i18n.t("meta.error"),
                    i18n.t("meta.only_images")
                )
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.file_dropped.emit("__browse__")
        super().mousePressEvent(event)


class MetaPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._gps: dict | None = None
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
        top.setObjectName("MetaTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("meta.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("meta.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("MetaDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        scroll = QScrollArea()
        scroll.setObjectName("MetaScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.result_host = QWidget()
        self.result_host.setObjectName("MetaResultHost")
        self.result_host.setAutoFillBackground(False)

        self.result_layout = QVBoxLayout(self.result_host)
        self.result_layout.setContentsMargins(36, 8, 36, 24)
        self.result_layout.setSpacing(20)
        self.result_layout.addStretch(1)

        scroll.setWidget(self.result_host)
        card_layout.addWidget(scroll, 1)

        self._scroll = scroll

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        filters = "Изображения (*.jpg *.jpeg *.png *.webp *.tif *.tiff *.bmp *.gif *.heic *.heif *.avif);;Все файлы (*)"
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("meta.browse"), start, filters
        )
        if path:
            if is_image(path):
                self.show_file(path)
            else:
                QMessageBox.warning(self, i18n.t("meta.error"),
                                    i18n.t("meta.only_images"))

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self.show_file(path)

    def show_file(self, path: str):
        self._current_path = path
        data = collect_metadata(path, units=self.settings.size_units)

        self._clear_results()
        self._gps = data.get("gps")

        if not data["ok"]:
            err = data.get("error", "unknown")
            key = f"meta.err.{err}"
            text = i18n.t(key, err)
            self._show_error(text)
            return

        if not data["groups"]:
            self._show_empty(i18n.t("meta.no_metadata"))
            return

        for group in data["groups"]:
            widget = self._build_group(group)
            self.result_layout.insertWidget(
                self.result_layout.count() - 1,
                widget
            )

    def _show_empty(self, text: str = None):
        self._clear_results()
        if text is None:
            text = i18n.t("meta.empty")
        lbl = QLabel(text)
        lbl.setObjectName("MetaEmpty")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setAutoFillBackground(False)
        lbl.setWordWrap(True)
        self.result_layout.insertWidget(0, lbl)

    def _show_error(self, err: str):
        lbl = QLabel(f"{i18n.t('meta.error')}: {err}")
        lbl.setObjectName("MetaError")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setAutoFillBackground(False)
        self.result_layout.insertWidget(0, lbl)

    def _build_group(self, group: dict) -> QWidget:
        host = QWidget()
        host.setObjectName("MetaGroup")
        host.setAutoFillBackground(False)

        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title_key = group["title_key"]
        title = QLabel(i18n.t(title_key, title_key))
        title.setObjectName("MetaGroupTitle")
        title.setAutoFillBackground(False)
        layout.addWidget(title)

        if title_key == "meta.group.gps" and self._gps:
            btn_row = QHBoxLayout()
            btn_row.setContentsMargins(0, 4, 0, 4)

            btn_map = QToolButton()
            btn_map.setObjectName("InfoBrowseBtn")
            btn_map.setText(i18n.t("meta.open_map"))
            btn_map.setCursor(Qt.PointingHandCursor)
            btn_map.clicked.connect(self._open_map)
            btn_row.addWidget(btn_map)

            btn_copy = QToolButton()
            btn_copy.setObjectName("InfoBrowseBtn")
            btn_copy.setText(i18n.t("meta.copy_coords"))
            btn_copy.setCursor(Qt.PointingHandCursor)
            btn_copy.clicked.connect(self._copy_coords)
            btn_row.addWidget(btn_copy)

            btn_row.addStretch(1)
            layout.addLayout(btn_row)

        grid_host = QWidget()
        grid_host.setObjectName("MetaGrid")
        grid_host.setAutoFillBackground(False)

        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        for i, (key, value) in enumerate(group["rows"]):
            key_lbl = QLabel(str(key))
            key_lbl.setObjectName("MetaKey")
            key_lbl.setAutoFillBackground(False)
            key_lbl.setMinimumWidth(180)
            key_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            key_lbl.setWordWrap(True)

            val_lbl = QLabel(str(value))
            val_lbl.setObjectName("MetaValue")
            val_lbl.setAutoFillBackground(False)
            val_lbl.setWordWrap(True)
            val_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

            grid.addWidget(key_lbl, i, 0)
            grid.addWidget(val_lbl, i, 1)

        layout.addWidget(grid_host)
        return host

    def _open_map(self):
        if not self._gps or self._gps.get("lat") is None:
            return
        lat, lon = self._gps["lat"], self._gps["lon"]
        url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=16/{lat}/{lon}"
        QDesktopServices.openUrl(QUrl(url))

    def _copy_coords(self):
        if not self._gps:
            return
        from PySide6.QtGui import QGuiApplication
        lat, lon = self._gps.get("lat"), self._gps.get("lon")
        QGuiApplication.clipboard().setText(f"{lat}, {lon}")

    def _clear_results(self):
        while self.result_layout.count() > 1:
            item = self.result_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def retranslate(self):
        self.btn_browse.setText(i18n.t("meta.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("meta.drop_hint"))
        if self._current_path:
            self.show_file(self._current_path)