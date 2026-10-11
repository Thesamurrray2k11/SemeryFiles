import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QPlainTextEdit,
    QComboBox, QMessageBox, QProgressBar
)

from tools import encoding as enc
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

        self.icon_lbl = QLabel("◎")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("enc.drop_hint"))
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


class EncodingPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
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
        top.setObjectName("EncTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("enc.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("enc.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("EncDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        result_host = QWidget()
        result_host.setObjectName("EncResultHost")
        result_host.setAutoFillBackground(False)
        result_layout = QVBoxLayout(result_host)
        result_layout.setContentsMargins(36, 0, 36, 12)
        result_layout.setSpacing(10)

        info_row = QHBoxLayout()
        info_row.setSpacing(12)

        self.file_lbl = QLabel(i18n.t("enc.no_file"))
        self.file_lbl.setObjectName("EncFileLabel")
        self.file_lbl.setAutoFillBackground(False)
        self.file_lbl.setWordWrap(True)

        self.enc_lbl = QLabel("")
        self.enc_lbl.setObjectName("EncResult")
        self.enc_lbl.setAutoFillBackground(False)

        self.conf_lbl = QLabel("")
        self.conf_lbl.setObjectName("EncConfidence")
        self.conf_lbl.setAutoFillBackground(False)

        info_row.addWidget(self.file_lbl, 1)
        info_row.addWidget(self.enc_lbl)
        info_row.addWidget(self.conf_lbl)

        result_layout.addLayout(info_row)

        self.conf_bar = QProgressBar()
        self.conf_bar.setObjectName("HashProgress")
        self.conf_bar.setTextVisible(False)
        self.conf_bar.setFixedHeight(4)
        self.conf_bar.setRange(0, 100)
        self.conf_bar.setValue(0)
        self.conf_bar.hide()
        result_layout.addWidget(self.conf_bar)

        self.candidates_host = QWidget()
        self.candidates_host.setObjectName("EncCandidatesHost")
        self.candidates_host.setAutoFillBackground(False)
        self.candidates_layout = QHBoxLayout(self.candidates_host)
        self.candidates_layout.setContentsMargins(0, 4, 0, 0)
        self.candidates_layout.setSpacing(16)
        result_layout.addWidget(self.candidates_host)

        card_layout.addWidget(result_host)

        preview_host = QWidget()
        preview_host.setObjectName("EncPreviewHost")
        preview_host.setAutoFillBackground(False)
        preview_layout = QVBoxLayout(preview_host)
        preview_layout.setContentsMargins(36, 0, 36, 12)
        preview_layout.setSpacing(6)

        preview_title = QLabel(i18n.t("enc.preview"))
        preview_title.setObjectName("ConvertSectionTitle")
        preview_title.setAutoFillBackground(False)
        preview_layout.addWidget(preview_title)

        self.preview = QPlainTextEdit()
        self.preview.setObjectName("EncPreview")
        self.preview.setReadOnly(True)
        preview_layout.addWidget(self.preview, 1)

        card_layout.addWidget(preview_host, 1)

        convert_host = QWidget()
        convert_host.setObjectName("EncConvertHost")
        convert_host.setAutoFillBackground(False)
        convert_layout = QHBoxLayout(convert_host)
        convert_layout.setContentsMargins(36, 0, 36, 24)
        convert_layout.setSpacing(10)

        lbl_target = QLabel(i18n.t("enc.convert_to"))
        lbl_target.setObjectName("HexLabel")
        lbl_target.setAutoFillBackground(False)

        self.target_combo = QComboBox()
        self.target_combo.setObjectName("ConvertCombo")
        for name, display, _ in enc.CANDIDATES:
            self.target_combo.addItem(display, name)
        idx_utf8 = next(
            (i for i in range(self.target_combo.count())
             if self.target_combo.itemData(i) == "utf-8"), 0
        )
        self.target_combo.setCurrentIndex(idx_utf8)

        self.btn_convert = QToolButton()
        self.btn_convert.setObjectName("ConvertRunBtn")
        self.btn_convert.setText(i18n.t("enc.convert"))
        self.btn_convert.setCursor(Qt.PointingHandCursor)
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self._convert)

        convert_layout.addWidget(lbl_target)
        convert_layout.addWidget(self.target_combo)
        convert_layout.addStretch(1)
        convert_layout.addWidget(self.btn_convert)

        card_layout.addWidget(convert_host)

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("enc.browse"), start,
            "Текстовые файлы (*.txt *.log *.json *.xml *.csv *.md *.py *.js *.html);;Все файлы (*)"
        )
        if path:
            self._load(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._load(path)

    def _load(self, path: str):
        self._current_path = path
        result = enc.detect_encoding(path)

        self.file_lbl.setText(os.path.basename(path))
        self.preview.setPlainText("")
        self.enc_lbl.setText("")
        self.conf_lbl.setText("")
        self.conf_bar.hide()
        self.btn_convert.setEnabled(False)

        while self.candidates_layout.count():
            item = self.candidates_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        if not result["ok"]:
            err = result.get("error", "unknown")
            self.file_lbl.setText(f"{i18n.t('enc.error')}: {err}")
            return

        self.enc_lbl.setText(result["display_name"])
        self.conf_lbl.setText(f"{i18n.t('enc.confidence')}: {result['confidence']}%")
        self.conf_bar.setValue(result["confidence"])
        self.conf_bar.show()
        self.preview.setPlainText(result["sample"])

        # Кандидаты
        for c in result["candidates"]:
            badge = QLabel(f"{c['display']}  {c['score']}")
            badge.setObjectName("EncCandidate")
            badge.setAutoFillBackground(False)
            badge.setCursor(Qt.PointingHandCursor)
            self.candidates_layout.addWidget(badge)
        self.candidates_layout.addStretch(1)

        self.btn_convert.setEnabled(True)

    def _convert(self):
        if not self._current_path:
            return

        start = self.settings.default_dir or os.path.dirname(self._current_path)
        base, ext = os.path.splitext(os.path.basename(self._current_path))
        default_name = f"{base}.utf8{ext or '.txt'}"
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("enc.save_as"),
            os.path.join(start, default_name)
        )
        if not path:
            return

        detected = self.enc_lbl.text().split("  ")[0].strip()
        src_enc = "utf-8"
        for name, display, _ in enc.CANDIDATES:
            if display == detected:
                src_enc = name
                break
        if "BOM" in self.enc_lbl.text():
            src_enc = "utf-8-sig" if "UTF-8" in detected else src_enc

        target_enc = self.target_combo.currentData()

        try:
            enc.convert_file(self._current_path, path, src_enc, target_enc)
        except Exception as e:
            QMessageBox.warning(self, i18n.t("enc.error"), str(e))
            return

        QMessageBox.information(self, i18n.t("enc.convert"), i18n.t("enc.done"))

    def retranslate(self):
        self.btn_browse.setText(i18n.t("enc.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("enc.drop_hint"))
        self.btn_convert.setText(i18n.t("enc.convert"))
        if not self._current_path:
            self.file_lbl.setText(i18n.t("enc.no_file"))