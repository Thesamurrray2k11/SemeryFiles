import os

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QPlainTextEdit, QCheckBox,
    QTabWidget, QMessageBox, QLineEdit, QProgressBar, QSpinBox
)

from tools import base64_tool as b64
from core.i18n import i18n


class EncodeFileWorker(QObject):
    progress = Signal(int, int)
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, path: str, line_width: int):
        super().__init__()
        self._path = path
        self._line_width = line_width
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            result = b64.encode_file(
                self._path,
                line_width=self._line_width,
                on_progress=lambda p, t: self.progress.emit(p, t),
                cancel_flag=lambda: self._cancel,
            )
            if not self._cancel:
                self.finished.emit(result)
        except InterruptedError:
            pass
        except Exception as e:
            self.failed.emit(str(e))


class DecodeFileWorker(QObject):
    progress = Signal(int, int)
    finished = Signal(int)
    failed = Signal(str)

    def __init__(self, src: str, dst: str):
        super().__init__()
        self._src = src
        self._dst = dst
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            written = b64.decode_file_to_file(
                self._src, self._dst,
                on_progress=lambda p, t: self.progress.emit(p, t),
                cancel_flag=lambda: self._cancel,
            )
            if not self._cancel:
                self.finished.emit(written)
        except InterruptedError:
            pass
        except Exception as e:
            self.failed.emit(str(e))


class Base64Page(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._thread: QThread | None = None
        self._worker = None
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
        top.setObjectName("B64TopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("b64.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        top_layout.addWidget(title)
        top_layout.addStretch(1)

        card_layout.addWidget(top)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("RegexTabs")

        text_tab = QWidget()
        text_tab.setObjectName("RegexTabPage")
        text_layout = QVBoxLayout(text_tab)
        text_layout.setContentsMargins(36, 8, 36, 24)
        text_layout.setSpacing(10)

        in_label = QLabel(i18n.t("b64.input"))
        in_label.setObjectName("ConvertSectionTitle")
        in_label.setAutoFillBackground(False)
        text_layout.addWidget(in_label)

        self.text_input = QPlainTextEdit()
        self.text_input.setObjectName("SqliteSqlInput")
        self.text_input.setFixedHeight(120)
        self.text_input.setPlaceholderText(i18n.t("b64.text_hint"))
        text_layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_encode_text = QToolButton()
        self.btn_encode_text.setObjectName("ConvertRunBtn")
        self.btn_encode_text.setText(i18n.t("b64.encode") + "  ↓")
        self.btn_encode_text.setCursor(Qt.PointingHandCursor)
        self.btn_encode_text.clicked.connect(self._encode_text)

        self.btn_decode_text = QToolButton()
        self.btn_decode_text.setObjectName("ConvertRunBtn")
        self.btn_decode_text.setText(i18n.t("b64.decode") + "  ↑")
        self.btn_decode_text.setCursor(Qt.PointingHandCursor)
        self.btn_decode_text.clicked.connect(self._decode_text)

        self.cb_urlsafe = QCheckBox(i18n.t("b64.urlsafe"))
        self.cb_urlsafe.setObjectName("RegexFlag")
        self.cb_urlsafe.setCursor(Qt.PointingHandCursor)

        btn_row.addWidget(self.btn_encode_text)
        btn_row.addWidget(self.btn_decode_text)
        btn_row.addSpacing(12)
        btn_row.addWidget(self.cb_urlsafe)
        btn_row.addStretch(1)
        text_layout.addLayout(btn_row)

        out_label = QLabel(i18n.t("b64.output"))
        out_label.setObjectName("ConvertSectionTitle")
        out_label.setAutoFillBackground(False)
        text_layout.addWidget(out_label)

        self.text_output = QPlainTextEdit()
        self.text_output.setObjectName("SqliteSqlInput")
        self.text_output.setReadOnly(True)
        self.text_output.setFixedHeight(140)
        self.text_output.setPlaceholderText(i18n.t("b64.output_hint"))
        text_layout.addWidget(self.text_output)

        res_row = QHBoxLayout()
        res_row.setSpacing(8)

        self.btn_copy_text = QToolButton()
        self.btn_copy_text.setObjectName("InfoBrowseBtn")
        self.btn_copy_text.setText(i18n.t("b64.copy"))
        self.btn_copy_text.setCursor(Qt.PointingHandCursor)
        self.btn_copy_text.clicked.connect(self._copy_text_output)

        self.btn_swap_text = QToolButton()
        self.btn_swap_text.setObjectName("InfoBrowseBtn")
        self.btn_swap_text.setText(i18n.t("b64.swap"))
        self.btn_swap_text.setCursor(Qt.PointingHandCursor)
        self.btn_swap_text.clicked.connect(self._swap_text)

        res_row.addWidget(self.btn_copy_text)
        res_row.addWidget(self.btn_swap_text)
        res_row.addStretch(1)
        text_layout.addLayout(res_row)

        self.text_status = QLabel("")
        self.text_status.setObjectName("ConvertStatus")
        self.text_status.setAutoFillBackground(False)
        self.text_status.setWordWrap(True)
        text_layout.addWidget(self.text_status)

        text_layout.addStretch(1)

        self.tabs.addTab(text_tab, i18n.t("b64.tab.text"))

        enc_tab = QWidget()
        enc_tab.setObjectName("RegexTabPage")
        enc_layout = QVBoxLayout(enc_tab)
        enc_layout.setContentsMargins(36, 8, 36, 24)
        enc_layout.setSpacing(10)

        hint = QLabel(i18n.t("b64.file_enc_hint"))
        hint.setObjectName("WorkspaceHint")
        hint.setAutoFillBackground(False)
        hint.setWordWrap(True)
        enc_layout.addWidget(hint)

        file_row = QHBoxLayout()
        file_row.setSpacing(8)

        self.enc_file_lbl = QLabel(i18n.t("b64.no_file"))
        self.enc_file_lbl.setObjectName("ConvertFileLabel")
        self.enc_file_lbl.setAutoFillBackground(False)
        self.enc_file_lbl.setWordWrap(True)

        self.btn_pick_file = QToolButton()
        self.btn_pick_file.setObjectName("InfoBrowseBtn")
        self.btn_pick_file.setText(i18n.t("b64.pick_file"))
        self.btn_pick_file.setCursor(Qt.PointingHandCursor)
        self.btn_pick_file.clicked.connect(self._pick_file)

        file_row.addWidget(self.enc_file_lbl, 1)
        file_row.addWidget(self.btn_pick_file)
        enc_layout.addLayout(file_row)

        opt_row = QHBoxLayout()
        opt_row.setSpacing(12)

        lbl_lw = QLabel(i18n.t("b64.line_width"))
        lbl_lw.setObjectName("HexLabel")
        lbl_lw.setAutoFillBackground(False)

        self.line_width_spin = QSpinBox()
        self.line_width_spin.setObjectName("ConvertSpin")
        self.line_width_spin.setRange(0, 200)
        self.line_width_spin.setValue(76)
        self.line_width_spin.setSuffix(" " + i18n.t("b64.chars"))
        self.line_width_spin.setSpecialValueText(i18n.t("b64.no_wrap"))

        opt_row.addWidget(lbl_lw)
        opt_row.addWidget(self.line_width_spin)
        opt_row.addStretch(1)
        enc_layout.addLayout(opt_row)

        enc_btn_row = QHBoxLayout()
        enc_btn_row.addStretch(1)

        self.btn_encode_file = QToolButton()
        self.btn_encode_file.setObjectName("ConvertRunBtn")
        self.btn_encode_file.setText(i18n.t("b64.encode_file"))
        self.btn_encode_file.setCursor(Qt.PointingHandCursor)
        self.btn_encode_file.clicked.connect(self._encode_file)
        self.btn_encode_file.setEnabled(False)

        enc_btn_row.addWidget(self.btn_encode_file)
        enc_layout.addLayout(enc_btn_row)

        self.enc_progress = QProgressBar()
        self.enc_progress.setObjectName("HashProgress")
        self.enc_progress.setTextVisible(False)
        self.enc_progress.setFixedHeight(6)
        self.enc_progress.hide()
        enc_layout.addWidget(self.enc_progress)

        prev_label = QLabel(i18n.t("b64.preview"))
        prev_label.setObjectName("ConvertSectionTitle")
        prev_label.setAutoFillBackground(False)
        enc_layout.addWidget(prev_label)

        self.enc_preview = QPlainTextEdit()
        self.enc_preview.setObjectName("EncPreview")
        self.enc_preview.setReadOnly(True)
        self.enc_preview.setPlaceholderText(i18n.t("b64.preview_hint"))
        enc_layout.addWidget(self.enc_preview, 1)

        enc_res_row = QHBoxLayout()
        enc_res_row.setSpacing(8)

        self.btn_copy_b64 = QToolButton()
        self.btn_copy_b64.setObjectName("InfoBrowseBtn")
        self.btn_copy_b64.setText(i18n.t("b64.copy"))
        self.btn_copy_b64.setCursor(Qt.PointingHandCursor)
        self.btn_copy_b64.clicked.connect(self._copy_b64_full)
        self.btn_copy_b64.setEnabled(False)

        self.btn_save_b64 = QToolButton()
        self.btn_save_b64.setObjectName("InfoBrowseBtn")
        self.btn_save_b64.setText(i18n.t("b64.save_as"))
        self.btn_save_b64.setCursor(Qt.PointingHandCursor)
        self.btn_save_b64.clicked.connect(self._save_b64_file)
        self.btn_save_b64.setEnabled(False)

        enc_res_row.addWidget(self.btn_copy_b64)
        enc_res_row.addWidget(self.btn_save_b64)
        enc_res_row.addStretch(1)
        enc_layout.addLayout(enc_res_row)

        self.enc_status = QLabel("")
        self.enc_status.setObjectName("ConvertStatus")
        self.enc_status.setAutoFillBackground(False)
        self.enc_status.setWordWrap(True)
        enc_layout.addWidget(self.enc_status)

        self.tabs.addTab(enc_tab, i18n.t("b64.tab.file_enc"))

        dec_tab = QWidget()
        dec_tab.setObjectName("RegexTabPage")
        dec_layout = QVBoxLayout(dec_tab)
        dec_layout.setContentsMargins(36, 8, 36, 24)
        dec_layout.setSpacing(10)

        hint2 = QLabel(i18n.t("b64.file_dec_hint"))
        hint2.setObjectName("WorkspaceHint")
        hint2.setAutoFillBackground(False)
        hint2.setWordWrap(True)
        dec_layout.addWidget(hint2)

        b64_row = QHBoxLayout()
        b64_row.setSpacing(8)

        self.dec_file_lbl = QLabel(i18n.t("b64.no_b64_file"))
        self.dec_file_lbl.setObjectName("ConvertFileLabel")
        self.dec_file_lbl.setAutoFillBackground(False)
        self.dec_file_lbl.setWordWrap(True)

        self.btn_pick_b64 = QToolButton()
        self.btn_pick_b64.setObjectName("InfoBrowseBtn")
        self.btn_pick_b64.setText(i18n.t("b64.pick_b64"))
        self.btn_pick_b64.setCursor(Qt.PointingHandCursor)
        self.btn_pick_b64.clicked.connect(self._pick_b64_file)

        b64_row.addWidget(self.dec_file_lbl, 1)
        b64_row.addWidget(self.btn_pick_b64)
        dec_layout.addLayout(b64_row)

        paste_label = QLabel(i18n.t("b64.or_paste"))
        paste_label.setObjectName("ConvertSectionTitle")
        paste_label.setAutoFillBackground(False)
        dec_layout.addWidget(paste_label)

        self.dec_paste = QPlainTextEdit()
        self.dec_paste.setObjectName("SqliteSqlInput")
        self.dec_paste.setFixedHeight(100)
        self.dec_paste.setPlaceholderText(i18n.t("b64.paste_hint"))
        dec_layout.addWidget(self.dec_paste)

        dec_btn_row = QHBoxLayout()
        dec_btn_row.setSpacing(8)
        dec_btn_row.addStretch(1)

        self.btn_decode_from_text = QToolButton()
        self.btn_decode_from_text.setObjectName("ConvertRunBtn")
        self.btn_decode_from_text.setText(i18n.t("b64.decode_from_text"))
        self.btn_decode_from_text.setCursor(Qt.PointingHandCursor)
        self.btn_decode_from_text.clicked.connect(self._decode_from_text)

        self.btn_decode_file = QToolButton()
        self.btn_decode_file.setObjectName("ConvertRunBtn")
        self.btn_decode_file.setText(i18n.t("b64.decode_to_file"))
        self.btn_decode_file.setCursor(Qt.PointingHandCursor)
        self.btn_decode_file.clicked.connect(self._decode_file)
        self.btn_decode_file.setEnabled(False)

        dec_btn_row.addWidget(self.btn_decode_from_text)
        dec_btn_row.addWidget(self.btn_decode_file)
        dec_layout.addLayout(dec_btn_row)

        self.dec_progress = QProgressBar()
        self.dec_progress.setObjectName("HashProgress")
        self.dec_progress.setTextVisible(False)
        self.dec_progress.setFixedHeight(6)
        self.dec_progress.hide()
        dec_layout.addWidget(self.dec_progress)

        self.dec_status = QLabel("")
        self.dec_status.setObjectName("ConvertStatus")
        self.dec_status.setAutoFillBackground(False)
        self.dec_status.setWordWrap(True)
        dec_layout.addWidget(self.dec_status)

        dec_layout.addStretch(1)

        self.tabs.addTab(dec_tab, i18n.t("b64.tab.file_dec"))

        card_layout.addWidget(self.tabs, 1)

    def _encode_text(self):
        text = self.text_input.toPlainText()
        if not text:
            return
        result = b64.encode_text(text, urlsafe=self.cb_urlsafe.isChecked())
        self.text_output.setPlainText(result)
        self._set_status(
            self.text_status,
            f"✓ {i18n.t('b64.done')}: {len(text)} → {len(result)}",
            "ok"
        )

    def _decode_text(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        ok, result = b64.decode_text(text)
        if not ok:
            self._set_status(
                self.text_status,
                f"✕ {i18n.t('b64.error')}: {result}",
                "err"
            )
            return
        self.text_output.setPlainText(result)
        self._set_status(
            self.text_status,
            f"✓ {i18n.t('b64.done')}: {len(text)} → {len(result)}",
            "ok"
        )

    def _copy_text_output(self):
        text = self.text_output.toPlainText()
        if text:
            QGuiApplication.clipboard().setText(text)

    def _swap_text(self):
        in_text = self.text_input.toPlainText()
        out_text = self.text_output.toPlainText()
        self.text_input.setPlainText(out_text)
        self.text_output.setPlainText(in_text)

    def _pick_file(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("b64.pick_file"), start,
            "Все файлы (*)"
        )
        if path:
            self._enc_file_path = path
            size = os.path.getsize(path)
            self.enc_file_lbl.setText(
                f"{os.path.basename(path)}  •  {b64.format_size(size)}"
            )
            self.btn_encode_file.setEnabled(True)
            self._set_status(self.enc_status, "", "")

    def _encode_file(self):
        path = getattr(self, "_enc_file_path", None)
        if not path:
            return

        self.enc_progress.show()
        self.enc_progress.setValue(0)
        self.btn_encode_file.setEnabled(False)

        self._thread = QThread(self)
        self._worker = EncodeFileWorker(path, self.line_width_spin.value())
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_enc_progress)
        self._worker.finished.connect(self._on_enc_finished)
        self._worker.failed.connect(self._on_enc_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)

        self._thread.start()

    def _on_enc_progress(self, processed: int, total: int):
        if total > 0:
            self.enc_progress.setValue(int(processed * 100 / total))

    def _on_enc_finished(self, result: str):
        self._enc_progress_done()
        self._enc_b64_result = result

        # Превью — первые 4000 символов
        preview = result if len(result) <= 4000 else result[:4000] + "\n\n…(обрезано)"
        self.enc_preview.setPlainText(preview)

        self.btn_copy_b64.setEnabled(True)
        self.btn_save_b64.setEnabled(True)

        self._set_status(
            self.enc_status,
            f"✓ {i18n.t('b64.done')}: {b64.format_size(len(result))} base64",
            "ok"
        )

    def _on_enc_failed(self, err: str):
        self._enc_progress_done()
        self._set_status(self.enc_status, f"✕ {i18n.t('b64.error')}: {err}", "err")

    def _enc_progress_done(self):
        self.enc_progress.hide()
        self.enc_progress.setValue(0)
        self.btn_encode_file.setEnabled(True)

    def _copy_b64_full(self):
        if hasattr(self, "_enc_b64_result"):
            QGuiApplication.clipboard().setText(self._enc_b64_result)

    def _save_b64_file(self):
        if not hasattr(self, "_enc_b64_result"):
            return
        start = self.settings.reports_dir or os.path.expanduser("~")
        src = getattr(self, "_enc_file_path", "file")
        base = os.path.basename(src)
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("b64.save_as"),
            os.path.join(start, f"{base}.b64.txt"),
            "Base64 (*.b64 *.txt);;Все файлы (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="ascii") as f:
                f.write(self._enc_b64_result)
        except OSError as e:
            QMessageBox.warning(self, i18n.t("b64.error"), str(e))

    def _pick_b64_file(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("b64.pick_b64"), start,
            "Base64 (*.b64 *.txt);;Все файлы (*)"
        )
        if path:
            self._dec_src_path = path
            size = os.path.getsize(path)
            self.dec_file_lbl.setText(
                f"{os.path.basename(path)}  •  {b64.format_size(size)}"
            )
            self.btn_decode_file.setEnabled(True)

    def _decode_file(self):
        src = getattr(self, "_dec_src_path", None)
        if not src:
            return

        start = self.settings.default_dir or os.path.dirname(src)
        default = os.path.splitext(os.path.basename(src))[0] + ".decoded"
        dst, _ = QFileDialog.getSaveFileName(
            self, i18n.t("b64.decode_to_file"),
            os.path.join(start, default),
            "Все файлы (*)"
        )
        if not dst:
            return

        self.dec_progress.show()
        self.dec_progress.setValue(0)
        self.btn_decode_file.setEnabled(False)

        self._thread = QThread(self)
        self._worker = DecodeFileWorker(src, dst)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_dec_progress)
        self._worker.finished.connect(self._on_dec_finished)
        self._worker.failed.connect(self._on_dec_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)

        self._thread.start()

    def _decode_from_text(self):
        text = self.dec_paste.toPlainText().strip()
        if not text:
            return
        start = self.settings.default_dir or os.path.expanduser("~")
        dst, _ = QFileDialog.getSaveFileName(
            self, i18n.t("b64.decode_to_file"),
            os.path.join(start, "decoded.bin"),
            "Все файлы (*)"
        )
        if not dst:
            return
        try:
            raw = b64.decode_file_to_bytes(text)
            with open(dst, "wb") as f:
                f.write(raw)
            kind = b64.detect_decoded_type(raw)
            self._set_status(
                self.dec_status,
                f"✓ {i18n.t('b64.done')}: {b64.format_size(len(raw))}  •  {kind}",
                "ok"
            )
        except Exception as e:
            self._set_status(self.dec_status, f"✕ {i18n.t('b64.error')}: {e}", "err")

    def _on_dec_progress(self, processed: int, total: int):
        if total > 0:
            self.dec_progress.setValue(int(processed * 100 / total))

    def _on_dec_finished(self, written: int):
        self.dec_progress.hide()
        self.dec_progress.setValue(0)
        self.btn_decode_file.setEnabled(True)
        self._set_status(
            self.dec_status,
            f"✓ {i18n.t('b64.done')}: {b64.format_size(written)}",
            "ok"
        )

    def _on_dec_failed(self, err: str):
        self.dec_progress.hide()
        self.dec_progress.setValue(0)
        self.btn_decode_file.setEnabled(True)
        self._set_status(self.dec_status, f"✕ {i18n.t('b64.error')}: {err}", "err")

    def _cleanup_thread(self):
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
        if self._thread is not None:
            self._thread.deleteLater()
            self._thread = None

    def _set_status(self, label: QLabel, text: str, state: str):
        label.setText(text)
        label.setProperty("state", state)
        label.style().unpolish(label)
        label.style().polish(label)

    def retranslate(self):
        self.tabs.setTabText(0, i18n.t("b64.tab.text"))
        self.tabs.setTabText(1, i18n.t("b64.tab.file_enc"))
        self.tabs.setTabText(2, i18n.t("b64.tab.file_dec"))
        self.btn_encode_text.setText(i18n.t("b64.encode") + "  ↓")
        self.btn_decode_text.setText(i18n.t("b64.decode") + "  ↑")
        self.btn_encode_file.setText(i18n.t("b64.encode_file"))
        self.btn_decode_file.setText(i18n.t("b64.decode_to_file"))
        self.btn_decode_from_text.setText(i18n.t("b64.decode_from_text"))
        self.btn_copy_text.setText(i18n.t("b64.copy"))
        self.btn_copy_b64.setText(i18n.t("b64.copy"))
        self.btn_save_b64.setText(i18n.t("b64.save_as"))
        self.btn_swap_text.setText(i18n.t("b64.swap"))
