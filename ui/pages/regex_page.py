import os

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import (
    QDragEnterEvent, QDropEvent, QTextCharFormat, QColor,
    QSyntaxHighlighter, QTextCursor
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QPlainTextEdit, QLineEdit,
    QCheckBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox
)

from tools import regex_tool
from core.i18n import i18n


class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(70)
        self.setMaximumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel("⇩")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        self.icon_lbl.setFixedWidth(30)

        self.text_lbl = QLabel(i18n.t("regex.drop_hint"))
        self.text_lbl.setObjectName("DropZoneText")
        self.text_lbl.setAutoFillBackground(False)

        layout.addStretch(1)
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl)
        layout.addStretch(1)

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


class MatchHighlighter(QSyntaxHighlighter):

    def __init__(self, document):
        super().__init__(document)
        self._spans: list[tuple[int, int, bool]] = []
        self._match_fmt = QTextCharFormat()
        self._match_fmt.setBackground(QColor("#5B7C99"))
        self._match_fmt.setForeground(QColor("#FFFFFF"))
        self._group_fmt = QTextCharFormat()
        self._group_fmt.setBackground(QColor("#7A9B6B"))
        self._group_fmt.setForeground(QColor("#FFFFFF"))

    def set_spans(self, spans: list[tuple[int, int, bool]]):
        self._spans = spans
        self.rehighlight()

    def highlightBlock(self, text: str):
        block_start = self.currentBlock().position()
        block_end = block_start + len(text)

        for (start, end, is_group) in self._spans:
            if end <= block_start or start >= block_end:
                continue
            overlap_start = max(start, block_start) - block_start
            overlap_end = min(end, block_end) - block_start
            if overlap_end <= overlap_start:
                continue
            fmt = self._group_fmt if is_group else self._match_fmt
            self.setFormat(overlap_start, overlap_end - overlap_start, fmt)


class RegexPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._last_matches = []
        self._replace_timer = QTimer(self)
        self._replace_timer.setSingleShot(True)
        self._replace_timer.setInterval(300)
        self._replace_timer.timeout.connect(self._update_replace_preview)
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
        top.setObjectName("RegexTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("regex.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("regex.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("RegexDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 8)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        pattern_host = QWidget()
        pattern_host.setObjectName("RegexPatternHost")
        pattern_host.setAutoFillBackground(False)
        pattern_layout = QVBoxLayout(pattern_host)
        pattern_layout.setContentsMargins(36, 0, 36, 8)
        pattern_layout.setSpacing(6)

        row = QHBoxLayout()
        row.setSpacing(8)

        lbl_re = QLabel("/")
        lbl_re.setObjectName("RegexSlash")
        lbl_re.setAutoFillBackground(False)

        self.pattern_input = QLineEdit()
        self.pattern_input.setObjectName("RegexInput")
        self.pattern_input.setPlaceholderText(i18n.t("regex.pattern_hint"))
        self.pattern_input.textChanged.connect(self._on_text_changed)

        lbl_re2 = QLabel("/")
        lbl_re2.setObjectName("RegexSlash")
        lbl_re2.setAutoFillBackground(False)

        row.addWidget(lbl_re)
        row.addWidget(self.pattern_input, 1)
        row.addWidget(lbl_re2)

        pattern_layout.addLayout(row)

        flags_row = QHBoxLayout()
        flags_row.setSpacing(14)

        self.flag_boxes: dict[str, QCheckBox] = {}
        for key, (label, _) in regex_tool.FLAGS.items():
            cb = QCheckBox(label)
            cb.setObjectName("RegexFlag")
            cb.setCursor(Qt.PointingHandCursor)
            cb.toggled.connect(self._on_text_changed)
            flags_row.addWidget(cb)
            self.flag_boxes[key] = cb

        flags_row.addStretch(1)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("RegexStatus")
        self.status_lbl.setAutoFillBackground(False)
        flags_row.addWidget(self.status_lbl)

        pattern_layout.addLayout(flags_row)

        card_layout.addWidget(pattern_host)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("RegexTabs")

        matches_tab = QWidget()
        matches_tab.setObjectName("RegexTabPage")
        matches_layout = QVBoxLayout(matches_tab)
        matches_layout.setContentsMargins(0, 8, 0, 0)
        matches_layout.setSpacing(8)

        split = QHBoxLayout()
        split.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(4)
        lbl_src = QLabel(i18n.t("regex.source"))
        lbl_src.setObjectName("RegexSectionLabel")
        lbl_src.setAutoFillBackground(False)
        left.addWidget(lbl_src)

        self.source_edit = QPlainTextEdit()
        self.source_edit.setObjectName("RegexSource")
        self.source_edit.setPlaceholderText(i18n.t("regex.source_hint"))
        self.source_edit.textChanged.connect(self._on_source_changed)

        self.highlighter = MatchHighlighter(self.source_edit.document())
        left.addWidget(self.source_edit, 1)

        right = QVBoxLayout()
        right.setSpacing(4)
        lbl_hits = QLabel(i18n.t("regex.matches"))
        lbl_hits.setObjectName("RegexSectionLabel")
        lbl_hits.setAutoFillBackground(False)
        right.addWidget(lbl_hits)

        self.matches_table = QTableWidget(0, 5)
        self.matches_table.setObjectName("RegexTable")
        self.matches_table.setHorizontalHeaderLabels([
            "#", i18n.t("regex.col.pos"), i18n.t("regex.col.len"),
            i18n.t("regex.col.text"), i18n.t("regex.col.groups"),
        ])
        self.matches_table.verticalHeader().setVisible(False)
        self.matches_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.matches_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.matches_table.setAlternatingRowColors(True)
        hdr = self.matches_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.matches_table.itemSelectionChanged.connect(self._on_match_selected)
        right.addWidget(self.matches_table, 1)

        split.addLayout(left, 3)
        split.addLayout(right, 2)
        matches_layout.addLayout(split)

        self.tabs.addTab(matches_tab, i18n.t("regex.tab.matches"))

        replace_tab = QWidget()
        replace_tab.setObjectName("RegexTabPage")
        replace_layout = QVBoxLayout(replace_tab)
        replace_layout.setContentsMargins(0, 8, 0, 0)
        replace_layout.setSpacing(8)

        repl_row = QHBoxLayout()
        repl_row.setSpacing(8)
        lbl_repl = QLabel(i18n.t("regex.replacement"))
        lbl_repl.setObjectName("RegexSectionLabel")
        lbl_repl.setAutoFillBackground(False)

        self.replacement_input = QLineEdit()
        self.replacement_input.setObjectName("RegexInput")
        self.replacement_input.setPlaceholderText(r"\1 — первая группа, \g<name> — именованная, \n — перевод строки")
        self.replacement_input.textChanged.connect(self._schedule_replace_preview)

        repl_row.addWidget(lbl_repl)
        repl_row.addWidget(self.replacement_input, 1)
        replace_layout.addLayout(repl_row)

        self.replace_preview = QPlainTextEdit()
        self.replace_preview.setObjectName("RegexSource")
        self.replace_preview.setReadOnly(True)
        self.replace_preview.setPlaceholderText(i18n.t("regex.replace_preview_hint"))
        replace_layout.addWidget(self.replace_preview, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self.btn_copy_result = QToolButton()
        self.btn_copy_result.setObjectName("InfoBrowseBtn")
        self.btn_copy_result.setText(i18n.t("regex.copy_result"))
        self.btn_copy_result.setCursor(Qt.PointingHandCursor)
        self.btn_copy_result.clicked.connect(self._copy_result)
        self.btn_copy_result.setEnabled(False)

        self.btn_save_result = QToolButton()
        self.btn_save_result.setObjectName("ConvertRunBtn")
        self.btn_save_result.setText(i18n.t("regex.save_result"))
        self.btn_save_result.setCursor(Qt.PointingHandCursor)
        self.btn_save_result.clicked.connect(self._save_result)
        self.btn_save_result.setEnabled(False)

        btn_row.addWidget(self.btn_copy_result)
        btn_row.addWidget(self.btn_save_result)
        replace_layout.addLayout(btn_row)

        self.tabs.addTab(replace_tab, i18n.t("regex.tab.replace"))

        help_tab = QWidget()
        help_tab.setObjectName("RegexTabPage")
        help_layout = QVBoxLayout(help_tab)
        help_layout.setContentsMargins(0, 8, 0, 0)

        help_lbl = QLabel(i18n.t("regex.help_text"))
        help_lbl.setObjectName("RegexHelp")
        help_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        help_lbl.setWordWrap(True)
        help_lbl.setAutoFillBackground(False)
        help_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        help_layout.addWidget(help_lbl)
        help_layout.addStretch(1)

        self.tabs.addTab(help_tab, i18n.t("regex.tab.help"))

        card_layout.addWidget(self.tabs, 1)

        self._last_replace_result = ""

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("regex.browse"), start,
            "Текстовые файлы (*.txt *.log *.json *.xml *.csv *.md *.py *.js *.html);;Все файлы (*)"
        )
        if path:
            self._load_file(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._load_file(path)

    def _load_file(self, path: str):
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except OSError as e:
            QMessageBox.warning(self, i18n.t("regex.error"), str(e))
            return

        self._current_path = path
        self.source_edit.setPlainText(text)
        # Автоматически пересчитываем
        self._update_matches()

    def _on_text_changed(self):
        self._update_matches()

    def _on_source_changed(self):
        self._update_matches()

    def _selected_flags(self) -> list[str]:
        return [k for k, cb in self.flag_boxes.items() if cb.isChecked()]

    def _update_matches(self):
        pattern_text = self.pattern_input.text()
        source = self.source_edit.toPlainText()

        self.highlighter.set_spans([])
        self.matches_table.setRowCount(0)
        self._last_matches = []

        if not pattern_text:
            self._set_status("", "")
            return

        try:
            pattern = regex_tool.compile_pattern(pattern_text, self._selected_flags())
        except Exception as e:
            self._set_status(i18n.t("regex.bad_pattern"), "err")
            return

        matches = regex_tool.find_all(pattern, source)
        self._last_matches = matches

        info = regex_tool.humanize_pattern(pattern_text)
        info_text = i18n.t("regex.info").format(
            count=len(matches),
            groups=info["capturing"],
            named=info["named"],
        )
        self._set_status(info_text, "ok" if matches else "")

        spans = []
        for m in matches:
            spans.append((m.start, m.end, False))
            for (idx, name, val) in m.groups:
                if val is not None and m.end > m.start:
                    pass
        self.highlighter.set_spans(spans)

        self.matches_table.setRowCount(len(matches))
        for i, m in enumerate(matches):
            self.matches_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.matches_table.setItem(i, 1, QTableWidgetItem(str(m.start)))
            self.matches_table.setItem(i, 2, QTableWidgetItem(str(m.end - m.start)))
            preview = m.text if len(m.text) <= 200 else m.text[:197] + "..."
            preview = preview.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
            self.matches_table.setItem(i, 3, QTableWidgetItem(preview))
            if m.groups:
                gsummary = " | ".join(
                    f"{idx}:{name or '—'}={(v if v is not None else '∅')[:30]}"
                    for (idx, name, v) in m.groups[:4]
                )
                if len(m.groups) > 4:
                    gsummary += f" …+{len(m.groups)-4}"
            else:
                gsummary = "—"
            self.matches_table.setItem(i, 4, QTableWidgetItem(gsummary))

        self._schedule_replace_preview()

    def _set_status(self, text: str, state: str):
        self.status_lbl.setText(text)
        self.status_lbl.setProperty("state", state)
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

    def _on_match_selected(self):
        rows = self.matches_table.selectionModel().selectedRows()
        if not rows:
            return
        idx = rows[0].row()
        if idx < 0 or idx >= len(self._last_matches):
            return
        m = self._last_matches[idx]

        cursor = self.source_edit.textCursor()
        cursor.setPosition(m.start)
        cursor.setPosition(m.end, QTextCursor.KeepAnchor)
        self.source_edit.setTextCursor(cursor)
        self.source_edit.ensureCursorVisible()

    def _schedule_replace_preview(self):
        self._replace_timer.start()

    def _update_replace_preview(self):
        pattern_text = self.pattern_input.text()
        source = self.source_edit.toPlainText()
        replacement = self.replacement_input.text()

        self.replace_preview.setPlainText("")
        self._last_replace_result = ""
        self.btn_copy_result.setEnabled(False)
        self.btn_save_result.setEnabled(False)

        if not pattern_text:
            return

        try:
            pattern = regex_tool.compile_pattern(pattern_text, self._selected_flags())
        except Exception:
            return

        try:
            new_text, count = regex_tool.substitute(pattern, replacement, source)
        except ValueError as e:
            self.replace_preview.setPlainText(str(e))
            return

        preview = new_text if len(new_text) <= 20000 else new_text[:20000] + "\n\n…(обрезано)"
        self.replace_preview.setPlainText(preview)
        self._last_replace_result = new_text
        self.btn_copy_result.setEnabled(True)
        self.btn_save_result.setEnabled(True)

        self._set_status(i18n.t("regex.info_replace").format(count=count), "ok")

    def _copy_result(self):
        from PySide6.QtGui import QGuiApplication
        QGuiApplication.clipboard().setText(self._last_replace_result)

    def _save_result(self):
        if not self._last_replace_result:
            return
        start = self.settings.reports_dir or os.path.expanduser("~")
        default_name = "regex_result.txt"
        if self._current_path:
            base, ext = os.path.splitext(os.path.basename(self._current_path))
            default_name = f"{base}.replaced{ext or '.txt'}"
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("regex.save_result"),
            os.path.join(start, default_name)
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._last_replace_result)
        except OSError as e:
            QMessageBox.warning(self, i18n.t("regex.error"), str(e))

    def retranslate(self):
        self.btn_browse.setText(i18n.t("regex.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("regex.drop_hint"))
        self.btn_copy_result.setText(i18n.t("regex.copy_result"))
        self.btn_save_result.setText(i18n.t("regex.save_result"))
        self.tabs.setTabText(0, i18n.t("regex.tab.matches"))
        self.tabs.setTabText(1, i18n.t("regex.tab.replace"))
        self.tabs.setTabText(2, i18n.t("regex.tab.help"))