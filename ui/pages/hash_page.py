import os

from PySide6.QtCore import Qt, Signal, QThread, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QScrollArea, QSizePolicy, QProgressBar,
    QCheckBox, QApplication
)

from tools.hash import available_algorithms, label_for, hash_file_multi
from core.i18n import i18n



class HashWorker(QObject):

    progress = Signal(int, int)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, path: str, algorithms: list[str]):
        super().__init__()
        self._path = path
        self._algorithms = algorithms
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            result = hash_file_multi(
                self._path,
                self._algorithms,
                on_progress=self._emit_progress,
                cancel_flag=lambda: self._cancel,
            )
            if not self._cancel:
                self.finished.emit(result)
        except InterruptedError:
            pass
        except Exception as e:
            self.failed.emit(str(e))

    def _emit_progress(self, processed: int, total: int):
        if not self._cancel:
            self.progress.emit(processed, total)


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

        self.icon_lbl = QLabel("⇩")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel(i18n.t("hash.drop_hint"))
        self.text_lbl.setObjectName("DropZoneText")
        self.text_lbl.setAlignment(Qt.AlignCenter)
        self.text_lbl.setAutoFillBackground(False)
        layout.addWidget(self.text_lbl)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("hovered", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event):
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


class HashRow(QFrame):

    def __init__(self, algo: str, parent=None):
        super().__init__(parent)
        self.setObjectName("HashRow")
        self._algo = algo
        self._value = ""
        self._build()

    def _build(self):
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(12)

        self.name_lbl = QLabel(label_for(self._algo))
        self.name_lbl.setObjectName("HashName")
        self.name_lbl.setFixedWidth(90)
        self.name_lbl.setAutoFillBackground(False)

        self.value_lbl = QLabel("—")
        self.value_lbl.setObjectName("HashValue")
        self.value_lbl.setAutoFillBackground(False)
        self.value_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.value_lbl.setWordWrap(False)

        self.btn_copy = QToolButton()
        self.btn_copy.setObjectName("HashCopyBtn")
        self.btn_copy.setText("⧉")
        self.btn_copy.setCursor(Qt.PointingHandCursor)
        self.btn_copy.setToolTip(i18n.t("hash.copy"))
        self.btn_copy.clicked.connect(self._copy)
        self.btn_copy.setEnabled(False)

        row.addWidget(self.name_lbl)
        row.addWidget(self.value_lbl, 1)
        row.addWidget(self.btn_copy)

    def set_value(self, value: str):
        self._value = value
        self.value_lbl.setText(value)
        self.btn_copy.setEnabled(bool(value))

    def _copy(self):
        if self._value:
            QGuiApplication.clipboard().setText(self._value)
            self.btn_copy.setText("✓")
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1200, lambda: self.btn_copy.setText("⧉"))



class HashPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._thread: QThread | None = None
        self._worker: HashWorker | None = None
        self._rows: dict[str, HashRow] = {}
        self._build()
        self._sync_checkboxes_enabled()

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
        top.setObjectName("HashTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("hash.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("hash.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        self.btn_export = QToolButton()
        self.btn_export.setObjectName("InfoBrowseBtn")
        self.btn_export.setText(i18n.t("hash.export"))
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self._export)
        self.btn_export.setEnabled(False)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_export)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("HashDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        algos_host = QWidget()
        algos_host.setObjectName("HashAlgosHost")
        algos_host.setAutoFillBackground(False)
        algos_layout = QVBoxLayout(algos_host)
        algos_layout.setContentsMargins(36, 0, 36, 12)
        algos_layout.setSpacing(8)

        algos_title = QLabel(i18n.t("hash.algorithms"))
        algos_title.setObjectName("HashSectionTitle")
        algos_title.setAutoFillBackground(False)
        algos_layout.addWidget(algos_title)

        grid_host = QWidget()
        grid_host.setObjectName("HashAlgosGrid")
        grid_host.setAutoFillBackground(False)
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(6)

        self._checkboxes: dict[str, QCheckBox] = {}
        algos = available_algorithms()
        for i, algo in enumerate(algos):
            row = i % 5
            col = i // 5
            cb = QCheckBox(label_for(algo))
            cb.setObjectName("HashCheckbox")
            cb.setCursor(Qt.PointingHandCursor)
            cb.setProperty("algo", algo)
            cb.setChecked(algo in ("sha256", "sha1", "md5", "sha512"))
            cb.toggled.connect(self._on_algo_toggled)
            grid.addWidget(cb, row, col)
            self._checkboxes[algo] = cb

        algos_layout.addWidget(grid_host)
        card_layout.addWidget(algos_host)

        self.progress = QProgressBar()
        self.progress.setObjectName("HashProgress")
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()

        progress_host = QWidget()
        progress_host.setObjectName("HashProgressHost")
        progress_host.setAutoFillBackground(False)
        progress_layout = QVBoxLayout(progress_host)
        progress_layout.setContentsMargins(36, 0, 36, 12)
        progress_layout.addWidget(self.progress)
        card_layout.addWidget(progress_host)

        scroll = QScrollArea()
        scroll.setObjectName("HashScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.result_host = QWidget()
        self.result_host.setObjectName("HashResultHost")
        self.result_host.setAutoFillBackground(False)

        self.result_layout = QVBoxLayout(self.result_host)
        self.result_layout.setContentsMargins(36, 0, 36, 24)
        self.result_layout.setSpacing(8)
        self.result_layout.addStretch(1)

        scroll.setWidget(self.result_host)
        card_layout.addWidget(scroll, 1)

        self._scroll = scroll

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("hash.browse"), start
        )
        if path:
            self._start_hash(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._start_hash(path)

    def _on_algo_toggled(self, _checked):
        self._sync_checkboxes_enabled()

    def _sync_checkboxes_enabled(self):
        pass

    def _selected_algos(self) -> list[str]:
        return [a for a, cb in self._checkboxes.items() if cb.isChecked()]

    def _start_hash(self, path: str):
        algos = self._selected_algos()
        if not algos:
            self._show_message(i18n.t("hash.need_algo"))
            return

        self._current_path = path
        self._clear_results()

        self.progress.show()
        self.progress.setValue(0)

        for algo in algos:
            row = HashRow(algo)
            self._rows[algo] = row
            self.result_layout.insertWidget(self.result_layout.count() - 1, row)

        self._thread = QThread(self)
        self._worker = HashWorker(path, algos)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)

        self._thread.start()

    def _on_progress(self, processed: int, total: int):
        if total <= 0:
            return
        pct = int(processed * 100 / total)
        self.progress.setValue(pct)

    def _on_finished(self, result: dict):
        self.progress.hide()
        for algo, digest in result.items():
            row = self._rows.get(algo)
            if row:
                row.set_value(digest)
        self.btn_export.setEnabled(True)

    def _on_failed(self, err: str):
        self.progress.hide()
        self._show_message(f"{i18n.t('hash.error')}: {err}", error=True)

    def _cleanup_thread(self):
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
        if self._thread:
            self._thread.deleteLater()
            self._thread = None

    def _export(self):
        if not self._current_path:
            return
        start = self.settings.reports_dir or os.path.expanduser("~")
        base = os.path.basename(self._current_path)
        default_name = os.path.join(start, f"{base}.hashes.txt")
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("hash.export"), default_name,
            "Text (*.txt);;All files (*)"
        )
        if not path:
            return

        lines = [
            f"# SemeryFiles — контрольные суммы",
            f"# Файл: {self._current_path}",
            f"# Размер: {os.path.getsize(self._current_path)} байт",
            "",
        ]
        for algo, row in self._rows.items():
            if row._value:
                lines.append(f"{label_for(algo):<10} {row._value}")

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
        except OSError as e:
            self._show_message(str(e), error=True)

    def _clear_results(self):
        self._rows.clear()
        self.btn_export.setEnabled(False)
        while self.result_layout.count() > 1:
            item = self.result_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    def _show_message(self, text: str, error: bool = False):
        lbl = QLabel(text)
        lbl.setObjectName("HashError" if error else "HashEmpty")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setAutoFillBackground(False)
        self.result_layout.insertWidget(0, lbl)

    def retranslate(self):
        self.btn_browse.setText(i18n.t("hash.browse"))
        self.btn_export.setText(i18n.t("hash.export"))
        self.drop_zone.text_lbl.setText(i18n.t("hash.drop_hint"))