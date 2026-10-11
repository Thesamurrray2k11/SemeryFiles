import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QPlainTextEdit,
    QLineEdit, QComboBox, QSpinBox, QMessageBox
)

from tools import hexview
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

        self.icon_lbl = QLabel("⇩")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("hex.drop_hint"))
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


class HexPage(QWidget):

    WIDTH_OPTIONS = [8, 16, 24, 32]

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._offset = 0
        self._bytes_per_row = 16
        self._page_size = hexview.DEFAULT_BLOCK
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
        top.setObjectName("HexTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("hex.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("hex.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("HexDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        ctrl_host = QWidget()
        ctrl_host.setObjectName("HexCtrlHost")
        ctrl_host.setAutoFillBackground(False)
        ctrl_layout = QHBoxLayout(ctrl_host)
        ctrl_layout.setContentsMargins(36, 0, 36, 12)
        ctrl_layout.setSpacing(10)

        lbl_off = QLabel(i18n.t("hex.offset"))
        lbl_off.setObjectName("HexLabel")
        lbl_off.setAutoFillBackground(False)
        self.offset_input = QLineEdit()
        self.offset_input.setObjectName("HexInput")
        self.offset_input.setFixedWidth(120)
        self.offset_input.setPlaceholderText("0x0")
        self.offset_input.returnPressed.connect(self._go_offset)

        btn_goto = QToolButton()
        btn_goto.setObjectName("InfoBrowseBtn")
        btn_goto.setText(i18n.t("hex.go"))
        btn_goto.setCursor(Qt.PointingHandCursor)
        btn_goto.clicked.connect(self._go_offset)

        lbl_w = QLabel(i18n.t("hex.width"))
        lbl_w.setObjectName("HexLabel")
        lbl_w.setAutoFillBackground(False)
        self.width_combo = QComboBox()
        self.width_combo.setObjectName("ConvertCombo")
        for w in self.WIDTH_OPTIONS:
            self.width_combo.addItem(str(w), w)
        self.width_combo.setCurrentIndex(1)   # 16
        self.width_combo.currentIndexChanged.connect(self._on_width_changed)

        lbl_pg = QLabel(i18n.t("hex.page"))
        lbl_pg.setObjectName("HexLabel")
        lbl_pg.setAutoFillBackground(False)
        self.page_spin = QSpinBox()
        self.page_spin.setObjectName("ConvertSpin")
        self.page_spin.setRange(1, 1024)
        self.page_spin.setValue(16)
        self.page_spin.setSuffix(" KB")
        self.page_spin.valueChanged.connect(self._on_page_changed)

        ctrl_layout.addWidget(lbl_off)
        ctrl_layout.addWidget(self.offset_input)
        ctrl_layout.addWidget(btn_goto)
        ctrl_layout.addSpacing(12)
        ctrl_layout.addWidget(lbl_w)
        ctrl_layout.addWidget(self.width_combo)
        ctrl_layout.addSpacing(12)
        ctrl_layout.addWidget(lbl_pg)
        ctrl_layout.addWidget(self.page_spin)
        ctrl_layout.addStretch(1)

        card_layout.addWidget(ctrl_host)

        search_host = QWidget()
        search_host.setObjectName("HexSearchHost")
        search_host.setAutoFillBackground(False)
        search_layout = QHBoxLayout(search_host)
        search_layout.setContentsMargins(36, 0, 36, 12)
        search_layout.setSpacing(10)

        self.search_mode = QComboBox()
        self.search_mode.setObjectName("ConvertCombo")
        self.search_mode.addItem(i18n.t("hex.mode.hex"), "hex")
        self.search_mode.addItem(i18n.t("hex.mode.ascii"), "ascii")

        self.search_input = QLineEdit()
        self.search_input.setObjectName("HexInput")
        self.search_input.setPlaceholderText("DE AD BE EF")
        self.search_input.returnPressed.connect(self._do_search)

        btn_find = QToolButton()
        btn_find.setObjectName("InfoBrowseBtn")
        btn_find.setText(i18n.t("hex.find"))
        btn_find.setCursor(Qt.PointingHandCursor)
        btn_find.clicked.connect(self._do_search)

        search_layout.addWidget(self.search_mode)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(btn_find)

        card_layout.addWidget(search_host)

        nav_host = QWidget()
        nav_host.setObjectName("HexNavHost")
        nav_host.setAutoFillBackground(False)
        nav_layout = QHBoxLayout(nav_host)
        nav_layout.setContentsMargins(36, 0, 36, 8)
        nav_layout.setSpacing(10)

        self.btn_prev = QToolButton()
        self.btn_prev.setObjectName("InfoBrowseBtn")
        self.btn_prev.setText("◀  " + i18n.t("hex.prev"))
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self._prev_page)

        self.info_lbl = QLabel("")
        self.info_lbl.setObjectName("HexInfo")
        self.info_lbl.setAutoFillBackground(False)
        self.info_lbl.setAlignment(Qt.AlignCenter)

        self.btn_next = QToolButton()
        self.btn_next.setObjectName("InfoBrowseBtn")
        self.btn_next.setText(i18n.t("hex.next") + "  ▶")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self._next_page)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.info_lbl, 1)
        nav_layout.addWidget(self.btn_next)

        card_layout.addWidget(nav_host)

        view_host = QWidget()
        view_host.setObjectName("HexViewHost")
        view_host.setAutoFillBackground(False)
        view_layout = QVBoxLayout(view_host)
        view_layout.setContentsMargins(36, 0, 36, 24)

        self.view = QPlainTextEdit()
        self.view.setObjectName("HexView")
        self.view.setReadOnly(True)
        self.view.setLineWrapMode(QPlainTextEdit.NoWrap)

        font = QFont("Consolas")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self.view.setFont(font)

        view_layout.addWidget(self.view)
        card_layout.addWidget(view_host, 1)

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("hex.browse"), start
        )
        if path:
            self._set_file(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._set_file(path)

    def _set_file(self, path: str):
        try:
            size = hexview.file_size(path)
        except OSError as e:
            QMessageBox.warning(self, i18n.t("hex.error"), str(e))
            return

        self._current_path = path
        self._offset = 0
        self._page_size = self.page_spin.value() * 1024

        name = os.path.basename(path)
        self.info_lbl.setText(f"{name}  •  {size:,} Б".replace(",", " "))
        self._render()

    def _on_width_changed(self):
        self._bytes_per_row = self.width_combo.currentData()
        self._render()

    def _on_page_changed(self, kb: int):
        self._page_size = kb * 1024
        self._render()

    def _prev_page(self):
        if not self._current_path:
            return
        self._offset = max(0, self._offset - self._page_size)
        self._render()

    def _next_page(self):
        if not self._current_path:
            return
        try:
            size = hexview.file_size(self._current_path)
        except OSError:
            return
        if self._offset + self._page_size >= size:
            return
        self._offset = min(size - 1, self._offset + self._page_size)
        self._render()

    def _go_offset(self):
        if not self._current_path:
            return
        text = self.offset_input.text().strip()
        try:
            value = int(text, 16) if text.lower().startswith("0x") else int(text, 16)
        except ValueError:
            try:
                value = int(text, 10)
            except ValueError:
                return
        try:
            size = hexview.file_size(self._current_path)
        except OSError:
            return
        self._offset = max(0, min(size - 1, value))
        self._render()

    def _do_search(self):
        if not self._current_path:
            return
        text = self.search_input.text().strip()
        if not text:
            return

        mode = self.search_mode.currentData()
        if mode == "hex":
            pattern = hexview.parse_hex_pattern(text)
            if pattern is None:
                QMessageBox.warning(self, i18n.t("hex.error"),
                                    i18n.t("hex.bad_pattern"))
                return
        else:
            pattern = hexview.parse_ascii_pattern(text)

        hits = hexview.find_pattern(
            self._current_path, pattern,
            start=0, max_hits=10,
        )

        if not hits:
            QMessageBox.information(self, i18n.t("hex.find"),
                                    i18n.t("hex.not_found"))
            return

        self._offset = (hits[0] // self._bytes_per_row) * self._bytes_per_row
        self._render()

        if len(hits) > 1:
            QMessageBox.information(
                self, i18n.t("hex.find"),
                f"{i18n.t('hex.found_more')}: {len(hits)}"
            )

    def _render(self):
        if not self._current_path:
            self.view.setPlainText("")
            return

        try:
            data = hexview.read_block(
                self._current_path, self._offset, self._page_size
            )
        except OSError as e:
            self.view.setPlainText(f"{i18n.t('hex.error')}: {e}")
            return

        if not data:
            self.view.setPlainText(i18n.t("hex.end_of_file"))
            return

        width = self._bytes_per_row
        lines = []

        header = "           " + "  ".join(
            f"{i:02X}" for i in range(width)
        ) + "   ASCII"
        lines.append(header)
        lines.append("─" * len(header))

        for row_start in range(0, len(data), width):
            row = data[row_start:row_start + width]
            addr = self._offset + row_start

            hex_part = "  ".join(f"{b:02X}" for b in row)
            hex_part = hex_part.ljust(width * 3 - 1)

            ascii_part = "".join(
                chr(b) if 32 <= b < 127 else "."
                for b in row
            )

            lines.append(f"{addr:08X}   {hex_part}   {ascii_part}")

        total = hexview.file_size(self._current_path)
        shown_end = self._offset + len(data)
        lines.append("")
        lines.append(
            f"{i18n.t('hex.showing')}: "
            f"0x{self._offset:X} – 0x{shown_end:X}  /  "
            f"{total:,} Б".replace(",", " ")
        )

        self.view.setPlainText("\n".join(lines))

    def retranslate(self):
        self.btn_browse.setText(i18n.t("hex.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("hex.drop_hint"))
        self.btn_prev.setText("◀  " + i18n.t("hex.prev"))
        self.btn_next.setText(i18n.t("hex.next") + "  ▶")
        if not self._current_path:
            self.info_lbl.setText("")