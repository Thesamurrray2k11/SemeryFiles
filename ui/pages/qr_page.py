import os
from io import BytesIO

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import (
    QGuiApplication, QPixmap, QImage, QDragEnterEvent, QDropEvent
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QPlainTextEdit, QComboBox,
    QSpinBox, QTabWidget, QMessageBox, QColorDialog, QScrollArea
)

from tools import qr_tool as qr
from core.i18n import i18n


class ColorButton(QToolButton):
    color_changed = Signal(str)

    def __init__(self, color: str = "#000000", parent=None):
        super().__init__(parent)
        self.setObjectName("QrColorBtn")
        self.setCursor(Qt.PointingHandCursor)
        self._color = color
        self.setFixedSize(40, 28)
        self.clicked.connect(self._pick)
        self._update_style()

    @property
    def color(self) -> str:
        return self._color

    def set_color(self, color: str):
        self._color = color
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(
            f"QToolButton#QrColorBtn {{"
            f"  background-color: {self._color};"
            f"  border: 1px solid #888;"
            f"  border-radius: 6px;"
            f"}}"
        )

    def _pick(self):
        c = QColorDialog.getColor(
            self._color_to_qcolor(),
            self,
            i18n.t("qr.color"),
        )
        if c.isValid():
            self._color = c.name()
            self._update_style()
            self.color_changed.emit(self._color)

    def _color_to_qcolor(self):
        from PySide6.QtGui import QColor
        return QColor(self._color)


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

        self.icon_lbl = QLabel("▩")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("qr.drop_hint"))
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


class QrPage(QWidget):

    LIVE_DELAY_MS = 400

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_image = None
        self._build()
        self._setup_live_timer()
        self._update_qr()

    def _setup_live_timer(self):
        self._live_timer = QTimer(self)
        self._live_timer.setSingleShot(True)
        self._live_timer.setInterval(self.LIVE_DELAY_MS)
        self._live_timer.timeout.connect(self._update_qr)

    def _schedule_update(self):
        self._live_timer.start()

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
        top.setObjectName("QrTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("qr.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        top_layout.addWidget(title)
        top_layout.addStretch(1)

        card_layout.addWidget(top)

        if not qr.is_available():
            warn = QLabel(i18n.t("qr.no_qrcode"))
            warn.setObjectName("MetaError")
            warn.setAlignment(Qt.AlignCenter)
            warn.setAutoFillBackground(False)
            warn.setWordWrap(True)
            card_layout.addWidget(warn)
            return

        self.tabs = QTabWidget()
        self.tabs.setObjectName("RegexTabs")

        gen_tab = QWidget()
        gen_tab.setObjectName("RegexTabPage")
        gen_layout = QHBoxLayout(gen_tab)
        gen_layout.setContentsMargins(36, 8, 36, 24)
        gen_layout.setSpacing(20)

        left = QVBoxLayout()
        left.setSpacing(10)

        lbl_data = QLabel(i18n.t("qr.data"))
        lbl_data.setObjectName("ConvertSectionTitle")
        lbl_data.setAutoFillBackground(False)
        left.addWidget(lbl_data)

        self.data_input = QPlainTextEdit()
        self.data_input.setObjectName("SqliteSqlInput")
        self.data_input.setFixedHeight(110)
        self.data_input.setPlaceholderText(i18n.t("qr.data_hint"))
        self.data_input.textChanged.connect(self._schedule_update)
        left.addWidget(self.data_input)

        settings_grid = QGridLayout()
        settings_grid.setHorizontalSpacing(14)
        settings_grid.setVerticalSpacing(8)

        lbl_size = QLabel(i18n.t("qr.size"))
        lbl_size.setObjectName("HexLabel")
        lbl_size.setAutoFillBackground(False)

        self.size_spin = QSpinBox()
        self.size_spin.setObjectName("ConvertSpin")
        self.size_spin.setRange(128, 2048)
        self.size_spin.setValue(512)
        self.size_spin.setSingleStep(64)
        self.size_spin.setSuffix(" px")
        self.size_spin.valueChanged.connect(self._schedule_update)

        settings_grid.addWidget(lbl_size, 0, 0)
        settings_grid.addWidget(self.size_spin, 0, 1)

        lbl_level = QLabel(i18n.t("qr.level"))
        lbl_level.setObjectName("HexLabel")
        lbl_level.setAutoFillBackground(False)

        self.level_combo = QComboBox()
        self.level_combo.setObjectName("ConvertCombo")
        for key, (label, _) in qr.ERROR_LEVELS.items():
            self.level_combo.addItem(f"{key} — {label}", key)
        self.level_combo.setCurrentIndex(1)  # M
        self.level_combo.currentIndexChanged.connect(self._schedule_update)

        settings_grid.addWidget(lbl_level, 1, 0)
        settings_grid.addWidget(self.level_combo, 1, 1)

        lbl_fg = QLabel(i18n.t("qr.fg"))
        lbl_fg.setObjectName("HexLabel")
        lbl_fg.setAutoFillBackground(False)
        self.color_fg = ColorButton("#000000")
        self.color_fg.color_changed.connect(self._schedule_update)

        lbl_bg = QLabel(i18n.t("qr.bg"))
        lbl_bg.setObjectName("HexLabel")
        lbl_bg.setAutoFillBackground(False)
        self.color_bg = ColorButton("#FFFFFF")
        self.color_bg.color_changed.connect(self._schedule_update)

        colors_row = QHBoxLayout()
        colors_row.setSpacing(8)
        colors_row.addWidget(lbl_fg)
        colors_row.addWidget(self.color_fg)
        colors_row.addSpacing(12)
        colors_row.addWidget(lbl_bg)
        colors_row.addWidget(self.color_bg)
        colors_row.addStretch(1)

        settings_grid.addLayout(colors_row, 2, 0, 1, 2)

        left.addLayout(settings_grid)
        left.addStretch(1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_save_png = QToolButton()
        self.btn_save_png.setObjectName("ConvertRunBtn")
        self.btn_save_png.setText(i18n.t("qr.save_png"))
        self.btn_save_png.setCursor(Qt.PointingHandCursor)
        self.btn_save_png.clicked.connect(lambda: self._save("PNG"))

        self.btn_save_svg = QToolButton()
        self.btn_save_svg.setObjectName("InfoBrowseBtn")
        self.btn_save_svg.setText(i18n.t("qr.save_svg"))
        self.btn_save_svg.setCursor(Qt.PointingHandCursor)
        self.btn_save_svg.clicked.connect(lambda: self._save("SVG"))

        self.btn_copy_img = QToolButton()
        self.btn_copy_img.setObjectName("InfoBrowseBtn")
        self.btn_copy_img.setText(i18n.t("qr.copy_image"))
        self.btn_copy_img.setCursor(Qt.PointingHandCursor)
        self.btn_copy_img.clicked.connect(self._copy_to_clipboard)

        btn_row.addWidget(self.btn_save_png)
        btn_row.addWidget(self.btn_save_svg)
        btn_row.addWidget(self.btn_copy_img)
        btn_row.addStretch(1)

        left.addLayout(btn_row)

        gen_layout.addLayout(left, 1)

        right = QVBoxLayout()
        right.setSpacing(6)

        lbl_preview = QLabel(i18n.t("qr.preview"))
        lbl_preview.setObjectName("ConvertSectionTitle")
        lbl_preview.setAutoFillBackground(False)
        right.addWidget(lbl_preview)

        self.preview_host = QFrame()
        self.preview_host.setObjectName("QrPreviewHost")
        self.preview_layout = QVBoxLayout(self.preview_host)
        self.preview_layout.setContentsMargins(20, 20, 20, 20)
        self.preview_layout.setAlignment(Qt.AlignCenter)

        self.preview_label = QLabel()
        self.preview_label.setObjectName("QrPreview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setAutoFillBackground(False)
        self.preview_label.setMinimumSize(300, 300)
        self.preview_label.setScaledContents(False)

        self.preview_layout.addWidget(self.preview_label)
        right.addWidget(self.preview_host, 1)

        gen_layout.addLayout(right, 1)

        self.tabs.addTab(gen_tab, i18n.t("qr.tab.generate"))

        dec_tab = QWidget()
        dec_tab.setObjectName("RegexTabPage")
        dec_layout = QVBoxLayout(dec_tab)
        dec_layout.setContentsMargins(36, 8, 36, 24)
        dec_layout.setSpacing(10)

        if not qr.is_decoder_available():
            warn = QLabel(i18n.t("qr.no_decoder"))
            warn.setObjectName("MetaError")
            warn.setAlignment(Qt.AlignCenter)
            warn.setAutoFillBackground(False)
            warn.setWordWrap(True)
            dec_layout.addWidget(warn)
        else:
            self.decode_drop = DropZone()
            self.decode_drop.file_dropped.connect(self._decode_file)
            dec_layout.addWidget(self.decode_drop)

            self.decode_results_host = QWidget()
            self.decode_results_host.setObjectName("MetaResultHost")
            self.decode_results_host.setAutoFillBackground(False)
            self.decode_results_layout = QVBoxLayout(self.decode_results_host)
            self.decode_results_layout.setContentsMargins(0, 8, 0, 0)
            self.decode_results_layout.setSpacing(10)
            dec_layout.addWidget(self.decode_results_host, 1)

        self.tabs.addTab(dec_tab, i18n.t("qr.tab.decode"))

        card_layout.addWidget(self.tabs, 1)

    def _update_qr(self):
        data = self.data_input.toPlainText().strip()

        if not data:
            self.preview_label.clear()
            self.preview_label.setText(i18n.t("qr.empty_data"))
            self._current_image = None
            return

        try:
            img = qr.generate_qr(
                data=data,
                size_px=self.size_spin.value(),
                error_level=self.level_combo.currentData(),
                fg_color=self.color_fg.color,
                bg_color=self.color_bg.color,
                border=4,
            )
        except Exception as e:
            self.preview_label.clear()
            self.preview_label.setText(f"{i18n.t('qr.error')}: {e}")
            self._current_image = None
            return

        if img is None:
            self.preview_label.clear()
            self.preview_label.setText(i18n.t("qr.error"))
            self._current_image = None
            return

        self._current_image = img
        self._show_pil_image(img)

    def _show_pil_image(self, img):
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        qimg = QImage()
        qimg.loadFromData(buf.read(), "PNG")
        pix = QPixmap.fromImage(qimg)

        max_side = min(self.preview_host.width(), self.preview_host.height()) - 40
        if max_side < 100:
            max_side = 300
        if pix.width() > max_side:
            pix = pix.scaled(
                max_side, max_side,
                Qt.KeepAspectRatio,
                Qt.FastTransformation,
            )
        self.preview_label.setPixmap(pix)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._current_image is not None:
            self._show_pil_image(self._current_image)

    def _save(self, fmt: str):
        if self._current_image is None:
            QMessageBox.information(self, i18n.t("qr.error"), i18n.t("qr.empty_data"))
            return

        start = self.settings.reports_dir or os.path.expanduser("~")
        base = "qr_code"
        if fmt.upper() == "SVG":
            default = os.path.join(start, f"{base}.svg")
            filters = "SVG (*.svg)"
        else:
            default = os.path.join(start, f"{base}.png")
            filters = "PNG (*.png)"

        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("qr.save_png" if fmt == "PNG" else "qr.save_svg"),
            default, filters
        )
        if not path:
            return

        ok, err = qr.save_qr(self._current_image, path, fmt=fmt)
        if not ok:
            QMessageBox.warning(self, i18n.t("qr.error"), err or "")

    def _copy_to_clipboard(self):
        if self._current_image is None:
            return
        buf = BytesIO()
        self._current_image.save(buf, format="PNG")
        buf.seek(0)

        qimg = QImage()
        qimg.loadFromData(buf.read(), "PNG")
        QGuiApplication.clipboard().setImage(qimg)

    def _decode_file(self, path: str):
        if path == "__browse__":
            start = self.settings.default_dir or os.path.expanduser("~")
            path, _ = QFileDialog.getOpenFileName(
                self, i18n.t("qr.decode_browse"), start,
                "Изображения (*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tiff);;Все файлы (*)"
            )
            if not path:
                return

        while self.decode_results_layout.count():
            item = self.decode_results_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        result = qr.decode_qr(path)

        if not result["ok"]:
            err = result.get("error", "unknown")
            lbl = QLabel(f"{i18n.t('qr.error')}: {err}")
            lbl.setObjectName("MetaError")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setAutoFillBackground(False)
            self.decode_results_layout.addWidget(lbl)
            return

        if not result["results"]:
            lbl = QLabel(i18n.t("qr.no_codes"))
            lbl.setObjectName("MetaEmpty")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setAutoFillBackground(False)
            self.decode_results_layout.addWidget(lbl)
            return

        for i, item in enumerate(result["results"]):
            widget = self._build_decoded_card(i + 1, item)
            self.decode_results_layout.addWidget(widget)

        self.decode_results_layout.addStretch(1)

    def _build_decoded_card(self, idx: int, item: dict) -> QWidget:
        host = QFrame()
        host.setObjectName("QrResultCard")
        host.setAutoFillBackground(False)

        layout = QVBoxLayout(host)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        x, y, w, h = item["rect"]
        header = QLabel(
            f"#{idx}  •  {item['type']}  •  ({x}, {y})  {w}×{h}"
        )
        header.setObjectName("MetaGroupTitle")
        header.setAutoFillBackground(False)
        layout.addWidget(header)

        val = item["data"]
        val_lbl = QLabel(val)
        val_lbl.setObjectName("MetaValue")
        val_lbl.setAutoFillBackground(False)
        val_lbl.setWordWrap(True)
        val_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(val_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        btn_copy = QToolButton()
        btn_copy.setObjectName("InfoBrowseBtn")
        btn_copy.setText(i18n.t("qr.copy_text"))
        btn_copy.setCursor(Qt.PointingHandCursor)
        btn_copy.clicked.connect(lambda _, v=val: QGuiApplication.clipboard().setText(v))
        btn_row.addWidget(btn_copy)

        if val.startswith(("http://", "https://")):
            btn_open = QToolButton()
            btn_open.setObjectName("InfoBrowseBtn")
            btn_open.setText(i18n.t("qr.open_url"))
            btn_open.setCursor(Qt.PointingHandCursor)
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            btn_open.clicked.connect(lambda _, v=val: QDesktopServices.openUrl(QUrl(v)))
            btn_row.addWidget(btn_open)

        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        return host

    def retranslate(self):
        self.tabs.setTabText(0, i18n.t("qr.tab.generate"))
        self.tabs.setTabText(1, i18n.t("qr.tab.decode"))
        self.btn_save_png.setText(i18n.t("qr.save_png"))
        self.btn_save_svg.setText(i18n.t("qr.save_svg"))
        self.btn_copy_img.setText(i18n.t("qr.copy_image"))