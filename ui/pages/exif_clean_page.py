import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QScrollArea, QSizePolicy, QCheckBox,
    QMessageBox, QProgressBar
)

from tools import exif_sanitizer as es
from core.i18n import i18n


class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel("⌦")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("exifc.drop_hint"))
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


class ExifCleanPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._checkbox_map: dict[str, QCheckBox] = {}
        self._build()

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
        top.setObjectName("ExifTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("exifc.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("exifc.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)
        drop_host = QWidget()
        drop_host.setObjectName("ExifDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        main = QWidget()
        main.setObjectName("ExifMainHost")
        main.setAutoFillBackground(False)
        main_layout = QHBoxLayout(main)
        main_layout.setContentsMargins(36, 0, 36, 24)
        main_layout.setSpacing(20)

        left = QVBoxLayout()
        left.setSpacing(6)

        lbl_found = QLabel(i18n.t("exifc.found"))
        lbl_found.setObjectName("RegexSectionLabel")
        lbl_found.setAutoFillBackground(False)
        left.addWidget(lbl_found)

        scroll = QScrollArea()
        scroll.setObjectName("MetaScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.fields_host = QWidget()
        self.fields_host.setObjectName("MetaResultHost")
        self.fields_host.setAutoFillBackground(False)
        self.fields_layout = QVBoxLayout(self.fields_host)
        self.fields_layout.setContentsMargins(0, 0, 8, 0)
        self.fields_layout.setSpacing(14)
        self.fields_layout.addStretch(1)

        scroll.setWidget(self.fields_host)
        left.addWidget(scroll, 1)

        main_layout.addLayout(left, 1)

        right = QVBoxLayout()
        right.setSpacing(6)

        lbl_remove = QLabel(i18n.t("exifc.what_remove"))
        lbl_remove.setObjectName("RegexSectionLabel")
        lbl_remove.setAutoFillBackground(False)
        right.addWidget(lbl_remove)

        opts_host = QWidget()
        opts_host.setObjectName("ExifOptsHost")
        opts_host.setAutoFillBackground(False)
        opts_layout = QVBoxLayout(opts_host)
        opts_layout.setContentsMargins(0, 0, 0, 0)
        opts_layout.setSpacing(8)

        for key, label_key in [
            ("all_exif",  "exifc.opt.all"),
            ("gps",       "exifc.opt.gps"),
            ("datetime",  "exifc.opt.datetime"),
            ("camera",    "exifc.opt.camera"),
            ("author",    "exifc.opt.author"),
            ("software",  "exifc.opt.software"),
            ("thumbnail", "exifc.opt.thumbnail"),
        ]:
            cb = QCheckBox(i18n.t(label_key))
            cb.setObjectName("RegexFlag")
            cb.setCursor(Qt.PointingHandCursor)
            cb.setProperty("remove_key", key)

            if key == "all_exif":
                cb.toggled.connect(self._on_all_exif_toggled)

            opts_layout.addWidget(cb)
            self._checkbox_map[key] = cb

        self._checkbox_map["gps"].setChecked(True)
        self._checkbox_map["datetime"].setChecked(True)
        self._checkbox_map["camera"].setChecked(True)
        self._checkbox_map["author"].setChecked(True)

        opts_layout.addStretch(1)
        right.addWidget(opts_host, 1)

        self.btn_clean = QToolButton()
        self.btn_clean.setObjectName("ConvertRunBtn")
        self.btn_clean.setText(i18n.t("exifc.clean_save"))
        self.btn_clean.setCursor(Qt.PointingHandCursor)
        self.btn_clean.setEnabled(False)
        self.btn_clean.clicked.connect(self._clean_and_save)
        right.addWidget(self.btn_clean)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("ConvertStatus")
        self.status_lbl.setAutoFillBackground(False)
        self.status_lbl.setWordWrap(True)
        right.addWidget(self.status_lbl)

        right.addStretch(0)

        main_layout.addLayout(right, 1)
        card_layout.addWidget(main, 1)

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("exifc.browse"), start,
            "Изображения (*.jpg *.jpeg *.png *.webp *.tif *.tiff);;Все файлы (*)"
        )
        if path:
            if es.is_supported(path):
                self._load(path)
            else:
                QMessageBox.warning(self, i18n.t("exifc.error"),
                                    i18n.t("exifc.unsupported"))

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        elif es.is_supported(path):
            self._load(path)
        else:
            QMessageBox.warning(self, i18n.t("exifc.error"),
                                i18n.t("exifc.unsupported"))

    def _load(self, path: str):
        self._current_path = path
        self._clear_fields()

        result = es.list_exif_fields(path)

        if not result["ok"]:
            err = result.get("error", "unknown")
            lbl = QLabel(f"{i18n.t('exifc.error')}: {err}")
            lbl.setObjectName("MetaError")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setAutoFillBackground(False)
            self.fields_layout.insertWidget(0, lbl)
            self.btn_clean.setEnabled(False)
            return

        if result["count"] == 0:
            lbl = QLabel(i18n.t("exifc.no_exif"))
            lbl.setObjectName("MetaEmpty")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setAutoFillBackground(False)
            self.fields_layout.insertWidget(0, lbl)
            self.btn_clean.setEnabled(True)
            return

        summary = QLabel(
            i18n.t("exifc.summary").format(count=result["count"])
        )
        summary.setObjectName("MetaGroupTitle")
        summary.setAutoFillBackground(False)
        self.fields_layout.insertWidget(0, summary)

        GROUP_TITLES = {
            "gps":      "exifc.group.gps",
            "camera":   "exifc.group.camera",
            "datetime": "exifc.group.datetime",
            "author":   "exifc.group.author",
            "software": "exifc.group.software",
            "other":    "exifc.group.other",
        }
        for grp, title_key in GROUP_TITLES.items():
            tags = result["groups"].get(grp, [])
            if not tags:
                continue
            widget = self._build_group(i18n.t(title_key), tags, result["fields"])
            self.fields_layout.insertWidget(
                self.fields_layout.count() - 1, widget
            )

        self.btn_clean.setEnabled(True)
        self.status_lbl.setText("")

    def _clear_fields(self):
        while self.fields_layout.count() > 1:
            item = self.fields_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _build_group(self, title: str, tags: list[str], fields: dict) -> QWidget:
        host = QWidget()
        host.setObjectName("MetaGroup")
        host.setAutoFillBackground(False)

        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("MetaGroupTitle")
        title_lbl.setAutoFillBackground(False)
        layout.addWidget(title_lbl)

        for tag in tags:
            val = fields.get(tag, "")
            val_str = str(val)
            if len(val_str) > 80:
                val_str = val_str[:77] + "…"

            row = QLabel(
                f'<span style="color:#9A968E">{tag}:</span>  '
                f'<span style="color:#E6E4DF">{val_str}</span>'
            )
            row.setObjectName("MetaValue")
            row.setAutoFillBackground(False)
            row.setTextFormat(Qt.RichText)
            row.setTextInteractionFlags(Qt.TextSelectableByMouse)
            row.setWordWrap(True)
            layout.addWidget(row)

        return host

    def _on_all_exif_toggled(self, checked: bool):
        for key, cb in self._checkbox_map.items():
            if key == "all_exif":
                continue
            cb.setEnabled(not checked)
            if checked:
                cb.blockSignals(True)
                cb.setChecked(False)
                cb.blockSignals(False)

    def _selected_options(self) -> list[str]:
        return [
            key for key, cb in self._checkbox_map.items()
            if cb.isChecked()
        ]

    def _clean_and_save(self):
        if not self._current_path:
            return

        options = self._selected_options()
        if not options:
            QMessageBox.information(self, i18n.t("exifc.error"),
                                    i18n.t("exifc.no_options"))
            return

        start = self.settings.default_dir or os.path.dirname(self._current_path)
        base, ext = os.path.splitext(os.path.basename(self._current_path))
        default_name = f"{base}.clean{ext}"
        dst, _ = QFileDialog.getSaveFileName(
            self, i18n.t("exifc.save_as"),
            os.path.join(start, default_name),
            "Изображения (*.jpg *.jpeg *.png *.webp *.tif *.tiff);;Все файлы (*)"
        )
        if not dst:
            return

        result = es.sanitize(self._current_path, dst, options)

        if not result["ok"]:
            err = result.get("error", "unknown")
            self.status_lbl.setText(f"✕  {i18n.t('exifc.error')}: {err}")
            self.status_lbl.setProperty("state", "err")
        else:
            removed = result.get("removed", 0)
            self.status_lbl.setText(
                f"✓  {i18n.t('exifc.done')}:  {removed}  {i18n.t('exifc.fields_removed')}"
            )
            self.status_lbl.setProperty("state", "ok")
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

    def retranslate(self):
        self.btn_browse.setText(i18n.t("exifc.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("exifc.drop_hint"))
        self.btn_clean.setText(i18n.t("exifc.clean_save"))