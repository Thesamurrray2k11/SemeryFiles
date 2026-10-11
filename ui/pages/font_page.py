import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, QFont, QFontDatabase
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QScrollArea, QSizePolicy, QPlainTextEdit,
    QComboBox, QTabWidget, QMessageBox
)

from tools import font_viewer as fv
from core.i18n import i18n

NAME_LABELS = {
    "family":          "info.field.family",
    "subfamily":       "info.field.subfamily",
    "full_name":       "info.field.full_name",
    "postscript_name": "info.field.postscript",
    "version":         "info.field.version",
    "unique_id":       "info.field.unique_id",
    "copyright":       "info.field.copyright",
    "trademark":       "info.field.trademark",
    "manufacturer":    "info.field.manufacturer",
    "designer":        "info.field.designer",
    "description":     "info.field.description",
    "vendor_url":      "info.field.vendor_url",
    "designer_url":    "info.field.designer_url",
    "license":         "info.field.license",
    "license_url":     "info.field.license_url",
}


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

        self.icon_lbl = QLabel("ƒ")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("fonts.drop_hint"))
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


class FontPage(QWidget):

    PREVIEW_TEXTS = [
        "Съешь же ещё этих мягких французских булок, да выпей чаю",
        "The quick brown fox jumps over the lazy dog",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "abcdefghijklmnopqrstuvwxyz",
        "0123456789 !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ]

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._fonts_data: list[dict] = []
        self._registered_ids: list[int] = []
        self._build()
        self._preview_families: list[str] = []

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
        top.setObjectName("FontTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("fonts.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("fonts.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("FontDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        selector_host = QWidget()
        selector_host.setObjectName("FontSelectorHost")
        selector_host.setAutoFillBackground(False)
        selector_layout = QHBoxLayout(selector_host)
        selector_layout.setContentsMargins(36, 0, 36, 8)
        selector_layout.setSpacing(8)

        self.lbl_fonts = QLabel(i18n.t("fonts.in_file"))
        self.lbl_fonts.setObjectName("HexLabel")
        self.lbl_fonts.setAutoFillBackground(False)

        self.font_selector = QComboBox()
        self.font_selector.setObjectName("ConvertCombo")
        self.font_selector.setMinimumWidth(280)
        self.font_selector.currentIndexChanged.connect(self._on_font_selected)

        self.method_lbl = QLabel("")
        self.method_lbl.setObjectName("EncConfidence")
        self.method_lbl.setAutoFillBackground(False)

        selector_layout.addWidget(self.lbl_fonts)
        selector_layout.addWidget(self.font_selector)
        selector_layout.addStretch(1)
        selector_layout.addWidget(self.method_lbl)

        card_layout.addWidget(selector_host)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("RegexTabs")

        info_tab = QWidget()
        info_tab.setObjectName("RegexTabPage")
        info_layout = QVBoxLayout(info_tab)
        info_layout.setContentsMargins(36, 8, 36, 24)

        info_scroll = QScrollArea()
        info_scroll.setObjectName("MetaScroll")
        info_scroll.setWidgetResizable(True)
        info_scroll.setFrameShape(QFrame.NoFrame)
        info_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.info_host = QWidget()
        self.info_host.setObjectName("MetaResultHost")
        self.info_host.setAutoFillBackground(False)

        self.info_layout = QVBoxLayout(self.info_host)
        self.info_layout.setContentsMargins(0, 0, 12, 0)
        self.info_layout.setSpacing(20)
        self.info_layout.addStretch(1)

        info_scroll.setWidget(self.info_host)
        info_layout.addWidget(info_scroll, 1)

        self.tabs.addTab(info_tab, i18n.t("fonts.tab.info"))

        preview_tab = QWidget()
        preview_tab.setObjectName("RegexTabPage")
        preview_layout = QVBoxLayout(preview_tab)
        preview_layout.setContentsMargins(36, 8, 36, 24)
        preview_layout.setSpacing(10)

        preview_ctrl_row = QHBoxLayout()
        preview_ctrl_row.setSpacing(8)

        lbl_text = QLabel(i18n.t("fonts.preview_text"))
        lbl_text.setObjectName("HexLabel")
        lbl_text.setAutoFillBackground(False)

        self.preview_input = QPlainTextEdit()
        self.preview_input.setObjectName("SqliteSqlInput")
        self.preview_input.setFixedHeight(70)
        self.preview_input.setPlainText(self.PREVIEW_TEXTS[0])
        self.preview_input.textChanged.connect(self._update_preview)

        preview_ctrl_row.addWidget(lbl_text)
        preview_ctrl_row.addWidget(self.preview_input, 1)

        size_col = QVBoxLayout()
        size_col.setSpacing(4)
        lbl_size = QLabel(i18n.t("fonts.preview_size"))
        lbl_size.setObjectName("HexLabel")
        lbl_size.setAutoFillBackground(False)

        self.size_selector = QComboBox()
        self.size_selector.setObjectName("ConvertCombo")
        for s in (12, 14, 16, 20, 24, 32, 48, 64, 96):
            self.size_selector.addItem(f"{s} pt", s)
        self.size_selector.setCurrentIndex(3)
        self.size_selector.currentIndexChanged.connect(self._update_preview)

        size_col.addWidget(lbl_size)
        size_col.addWidget(self.size_selector)
        size_col.addStretch(1)

        preview_ctrl_row.addLayout(size_col)
        preview_layout.addLayout(preview_ctrl_row)

        self.preview_host = QFrame()
        self.preview_host.setObjectName("FontPreviewHost")
        self.preview_layout = QVBoxLayout(self.preview_host)
        self.preview_layout.setContentsMargins(24, 24, 24, 24)
        self.preview_layout.setSpacing(14)

        preview_layout.addWidget(self.preview_host, 1)

        self.tabs.addTab(preview_tab, i18n.t("fonts.tab.preview"))

        tables_tab = QWidget()
        tables_tab.setObjectName("RegexTabPage")
        tables_layout = QVBoxLayout(tables_tab)
        tables_layout.setContentsMargins(36, 8, 36, 24)
        tables_layout.setSpacing(10)

        uni_title = QLabel(i18n.t("fonts.unicode"))
        uni_title.setObjectName("ConvertSectionTitle")
        uni_title.setAutoFillBackground(False)
        tables_layout.addWidget(uni_title)

        self.unicode_host = QWidget()
        self.unicode_host.setObjectName("FontUnicodeHost")
        self.unicode_host.setAutoFillBackground(False)
        self.unicode_layout = QVBoxLayout(self.unicode_host)
        self.unicode_layout.setContentsMargins(0, 0, 0, 0)
        self.unicode_layout.setSpacing(4)
        tables_layout.addWidget(self.unicode_host)

        tables_title = QLabel(i18n.t("fonts.tables"))
        tables_title.setObjectName("ConvertSectionTitle")
        tables_title.setAutoFillBackground(False)
        tables_layout.addWidget(tables_title)

        self.tables_view = QPlainTextEdit()
        self.tables_view.setObjectName("EncPreview")
        self.tables_view.setReadOnly(True)
        tables_layout.addWidget(self.tables_view, 1)

        self.tabs.addTab(tables_tab, i18n.t("fonts.tab.tables"))

        card_layout.addWidget(self.tabs, 1)

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("fonts.browse"), start,
            "Шрифты (*.ttf *.otf *.ttc *.otc *.woff *.woff2);;Все файлы (*)"
        )
        if path:
            self._load(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._load(path)

    def _load(self, path: str):
        self._unregister_previous()

        result = fv.collect_font_info(path)

        self.font_selector.blockSignals(True)
        self.font_selector.clear()
        self.font_selector.blockSignals(False)

        self._clear_info()
        self._clear_preview()

        if not result["ok"]:
            err = result.get("error", "unknown")
            self._show_error(err)
            return

        self._current_path = path
        self._fonts_data = result["fonts"]
        method = result.get("method") or "—"
        method_label = {
            "fonttools": i18n.t("fonts.method.fonttools"),
            "qt": i18n.t("fonts.method.qt"),
        }.get(method, method)
        self.method_lbl.setText(f"{i18n.t('fonts.method')}: {method_label}")

        self.font_selector.blockSignals(True)
        for f in self._fonts_data:
            name = f["names"].get("full_name") or f["names"].get("family") or f"Font #{f['index']}"
            self.font_selector.addItem(f"{f['index']}: {name}")
        self.font_selector.blockSignals(False)
        self.font_selector.setCurrentIndex(0)

        fid = fv.register_for_preview(path)
        self._preview_families = []
        if fid >= 0:
            self._registered_ids.append(fid)
            try:
                families = QFontDatabase.applicationFontFamilies(fid)
                self._preview_families = list(families)
            except Exception:
                self._preview_families = []
        else:
            self._preview_families = []

        self._on_font_selected(0)

    def _unregister_previous(self):
        for fid in self._registered_ids:
            try:
                QFontDatabase.removeApplicationFont(fid)
            except Exception:
                pass
        self._registered_ids.clear()

    def _on_font_selected(self, index: int):
        if index < 0 or index >= len(self._fonts_data):
            return
        font = self._fonts_data[index]
        self._fill_info(font)
        self._fill_unicode(font)
        self._fill_tables(font)
        self._update_preview()

    def _clear_info(self):
        while self.info_layout.count() > 1:
            item = self.info_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _show_error(self, err: str):
        lbl = QLabel(f"{i18n.t('fonts.error')}: {err}")
        lbl.setObjectName("MetaError")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setAutoFillBackground(False)
        self.info_layout.insertWidget(0, lbl)

    def _fill_info(self, font: dict):
        self._clear_info()

        names = font.get("names", {})
        metrics = font.get("metrics", {})

        general_rows = []
        for key in ("family", "subfamily", "full_name", "postscript_name",
                    "version", "unique_id"):
            val = names.get(key)
            if val:
                general_rows.append((i18n.t(NAME_LABELS[key]), val))

        if general_rows:
            self.info_layout.insertWidget(
                self.info_layout.count() - 1,
                self._build_group(i18n.t("fonts.group.names"), general_rows)
            )

        metric_rows = []
        if metrics.get("units_per_em"):
            metric_rows.append((i18n.t("fonts.metric.upm"), str(metrics["units_per_em"])))
        if "ascender" in metrics:
            metric_rows.append((i18n.t("fonts.metric.ascender"), str(metrics["ascender"])))
        if "descender" in metrics:
            metric_rows.append((i18n.t("fonts.metric.descender"), str(metrics["descender"])))
        if "line_gap" in metrics:
            metric_rows.append((i18n.t("fonts.metric.line_gap"), str(metrics["line_gap"])))
        if metrics.get("weight_class"):
            metric_rows.append((
                i18n.t("fonts.metric.weight"),
                f"{metrics['weight_class']}  ({metrics.get('weight_label', '')})"
            ))
        if metrics.get("mac_style_bold"):
            metric_rows.append((i18n.t("fonts.metric.bold"), "✓"))
        if metrics.get("mac_style_italic"):
            metric_rows.append((i18n.t("fonts.metric.italic"), "✓"))

        uni = font.get("unicode", {})
        if uni.get("total_glyphs"):
            metric_rows.append((
                i18n.t("fonts.metric.glyphs"),
                f"{uni['total_glyphs']:,}".replace(",", " ")
            ))

        if metric_rows:
            self.info_layout.insertWidget(
                self.info_layout.count() - 1,
                self._build_group(i18n.t("fonts.group.metrics"), metric_rows)
            )

        lic_rows = []
        for key in ("copyright", "trademark", "manufacturer", "designer",
                    "description", "vendor_url", "designer_url",
                    "license", "license_url"):
            val = names.get(key)
            if val:
                lic_rows.append((i18n.t(NAME_LABELS[key]), val))

        if lic_rows:
            self.info_layout.insertWidget(
                self.info_layout.count() - 1,
                self._build_group(i18n.t("fonts.group.license"), lic_rows)
            )


    def _fill_unicode(self, font: dict):
        while self.unicode_layout.count():
            item = self.unicode_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        coverage = (font.get("unicode") or {}).get("coverage", {})
        if not coverage:
            lbl = QLabel(i18n.t("fonts.no_unicode"))
            lbl.setObjectName("MetaEmpty")
            lbl.setAutoFillBackground(False)
            self.unicode_layout.addWidget(lbl)
            return

        CHECKS = [
            ("latin",    "Латиница"),
            ("cyrillic", "Кириллица"),
            ("greek",    "Греческий"),
            ("cjk",      "CJK (китайский/японский)"),
            ("arabic",   "Арабский"),
            ("hebrew",   "Иврит"),
        ]
        for key, human in CHECKS:
            has = coverage.get(key, False)
            mark = "✓" if has else "✕"
            color = "#7A9B6B" if has else "#B57A6B"

            row = QLabel(f'<span style="color:{color};font-weight:700">{mark}</span>  {human}')
            row.setObjectName("MetaValue")
            row.setAutoFillBackground(False)
            row.setTextFormat(Qt.RichText)
            self.unicode_layout.addWidget(row)

    def _fill_tables(self, font: dict):
        tables = font.get("tables", [])
        if not tables:
            self.tables_view.setPlainText(i18n.t("fonts.no_tables"))
            return
        lines = [f"{i+1:3}. {t}" for i, t in enumerate(tables)]
        self.tables_view.setPlainText("\n".join(lines))

    def _clear_preview(self):
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _update_preview(self):
        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        if not self._current_path or not self._registered_ids:
            self.preview_layout.addWidget(self._preview_note(
                i18n.t("fonts.preview_no_font")
            ))
            return

        fid = self._registered_ids[0]
        qt_families = list(QFontDatabase.applicationFontFamilies(fid))
        if not qt_families:
            self.preview_layout.addWidget(self._preview_note(
                i18n.t("fonts.preview_no_font")
            ))
            return

        idx = max(0, self.font_selector.currentIndex())
        family = qt_families[idx] if idx < len(qt_families) else qt_families[0]

        size = self.size_selector.currentData() or 20
        text = self.preview_input.toPlainText() or "Sample"

        title = QLabel(family)
        title.setObjectName("MetaGroupTitle")
        title.setAutoFillBackground(False)
        self.preview_layout.addWidget(title)

        body = QLabel(text)
        body.setObjectName("FontPreviewText")
        body.setAutoFillBackground(False)
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextSelectableByMouse)

        body.setStyleSheet(
            f"QLabel#FontPreviewText {{"
            f"  font-family: '{family}';"
            f"  font-size: {size}pt;"
            f"  color: #000000;"  
            f"}}"
        )

        self.preview_layout.addWidget(body)

        # Диагностика
        from PySide6.QtGui import QFontInfo
        info = QFontInfo(body.font())
        diag = QLabel(
            f"→  requested: {family!r}   applied: {info.family()!r}   {size} pt"
        )
        diag.setObjectName("MetaKey")
        diag.setAutoFillBackground(False)
        self.preview_layout.addWidget(diag)

        if info.family() != family:
            warn = QLabel(
                i18n.t("fonts.preview_fallback").replace("{name}", info.family())
            )
            warn.setObjectName("MetaError")
            warn.setAutoFillBackground(False)
            warn.setWordWrap(True)
            self.preview_layout.addWidget(warn)

        self.preview_layout.addStretch(1)

    def _preview_note(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("MetaEmpty")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setAutoFillBackground(False)
        lbl.setWordWrap(True)
        return lbl

    def _build_group(self, title: str, rows: list[tuple]) -> QWidget:
        host = QWidget()
        host.setObjectName("MetaGroup")
        host.setAutoFillBackground(False)

        layout = QVBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("MetaGroupTitle")
        title_lbl.setAutoFillBackground(False)
        layout.addWidget(title_lbl)

        grid_host = QWidget()
        grid_host.setObjectName("MetaGrid")
        grid_host.setAutoFillBackground(False)

        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        for i, (key, value) in enumerate(rows):
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

    def retranslate(self):
        self.btn_browse.setText(i18n.t("fonts.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("fonts.drop_hint"))
        self.tabs.setTabText(0, i18n.t("fonts.tab.info"))
        self.tabs.setTabText(1, i18n.t("fonts.tab.preview"))
        self.tabs.setTabText(2, i18n.t("fonts.tab.tables"))
        self.lbl_fonts.setText(i18n.t("fonts.in_file"))
        if self._current_path:
            self._on_font_selected(self.font_selector.currentIndex())