import os

from PySide6.QtCore import Qt, Signal, QThread, QObject, QTimer
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QScrollArea, QSizePolicy, QProgressBar,
    QComboBox, QSpinBox, QStackedWidget
)

from tools import convert as cv
from core.i18n import i18n


class ConvertWorker(QObject):
    progress = Signal(int, int)
    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, action: str, params: dict):
        super().__init__()
        self._action = action
        self._params = params
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            src = self._params["src"]
            dst = self._params["dst"]
            on_p = lambda p, t: self.progress.emit(p, t) if not self._cancel else None
            cancel = lambda: self._cancel

            if self._action == "encoding":
                cv.convert_encoding(
                    src, dst,
                    self._params["src_enc"], self._params["dst_enc"],
                    on_progress=on_p, cancel_flag=cancel,
                )
            elif self._action == "base64_encode":
                cv.base64_encode(src, dst, on_progress=on_p, cancel_flag=cancel)
            elif self._action == "base64_decode":
                cv.base64_decode(src, dst, on_progress=on_p, cancel_flag=cancel)
            elif self._action == "line_endings":
                cv.convert_line_endings(
                    src, dst, self._params["target"],
                    on_progress=on_p, cancel_flag=cancel,
                )
            elif self._action == "image":
                cv.convert_image(
                    src, dst, self._params["target_format"],
                    self._params.get("quality", 90),
                )
            else:
                raise ValueError(f"Неизвестное действие: {self._action}")

            if not self._cancel:
                self.finished.emit(dst)
        except InterruptedError:
            pass
        except Exception as e:
            self.failed.emit(str(e))


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

        self.text_lbl = QLabel(i18n.t("convert.drop_hint"))
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


class ConvertPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._thread: QThread | None = None
        self._worker: ConvertWorker | None = None
        self._build()
        self._update_action_ui()

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
        top.setObjectName("ConvertTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("convert.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("convert.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("ConvertDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        info_host = QWidget()
        info_host.setObjectName("ConvertInfoHost")
        info_host.setAutoFillBackground(False)
        info_layout = QHBoxLayout(info_host)
        info_layout.setContentsMargins(36, 0, 36, 12)
        info_layout.setSpacing(10)

        self.file_lbl = QLabel(i18n.t("convert.no_file"))
        self.file_lbl.setObjectName("ConvertFileLabel")
        self.file_lbl.setAutoFillBackground(False)
        self.file_lbl.setWordWrap(True)
        info_layout.addWidget(self.file_lbl, 1)

        card_layout.addWidget(info_host)

        action_host = QWidget()
        action_host.setObjectName("ConvertActionHost")
        action_host.setAutoFillBackground(False)
        action_layout = QVBoxLayout(action_host)
        action_layout.setContentsMargins(36, 0, 36, 12)
        action_layout.setSpacing(10)

        action_title = QLabel(i18n.t("convert.action"))
        action_title.setObjectName("ConvertSectionTitle")
        action_title.setAutoFillBackground(False)
        action_layout.addWidget(action_title)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.action_combo = QComboBox()
        self.action_combo.setObjectName("ConvertCombo")
        self.action_combo.addItem(i18n.t("convert.action.encoding"), "encoding")
        self.action_combo.addItem(i18n.t("convert.action.b64_enc"), "base64_encode")
        self.action_combo.addItem(i18n.t("convert.action.b64_dec"), "base64_decode")
        self.action_combo.addItem(i18n.t("convert.action.line_end"), "line_endings")
        if cv.has_pillow():
            self.action_combo.addItem(i18n.t("convert.action.image"), "image")
        self.action_combo.currentIndexChanged.connect(self._update_action_ui)

        action_row.addWidget(self.action_combo, 1)
        action_layout.addLayout(action_row)

        self.params_stack = QStackedWidget()
        self.params_stack.setObjectName("ConvertParamsStack")

        enc_page = QWidget()
        enc_layout = QGridLayout(enc_page)
        enc_layout.setContentsMargins(0, 0, 0, 0)
        enc_layout.setHorizontalSpacing(12)
        enc_layout.setVerticalSpacing(6)

        enc_layout.addWidget(QLabel(i18n.t("convert.src_enc")), 0, 0)
        self.src_enc = QComboBox()
        self.src_enc.setObjectName("ConvertCombo")
        self.src_enc.addItems(cv.TEXT_ENCODINGS)
        self.src_enc.setCurrentText("cp1251")
        enc_layout.addWidget(self.src_enc, 0, 1)

        enc_layout.addWidget(QLabel(i18n.t("convert.dst_enc")), 1, 0)
        self.dst_enc = QComboBox()
        self.dst_enc.setObjectName("ConvertCombo")
        self.dst_enc.addItems(cv.TEXT_ENCODINGS)
        self.dst_enc.setCurrentText("utf-8")
        enc_layout.addWidget(self.dst_enc, 1, 1)

        self.params_stack.addWidget(enc_page)

        line_page = QWidget()
        line_layout = QGridLayout(line_page)
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setHorizontalSpacing(12)
        line_layout.setVerticalSpacing(6)

        line_layout.addWidget(QLabel(i18n.t("convert.line_target")), 0, 0)
        self.line_target = QComboBox()
        self.line_target.setObjectName("ConvertCombo")
        self.line_target.addItem("LF  (Unix)", "lf")
        self.line_target.addItem("CRLF  (Windows)", "crlf")
        self.line_target.addItem("CR  (Classic Mac)", "cr")
        line_layout.addWidget(self.line_target, 0, 1)

        self.params_stack.addWidget(line_page)

        img_page = QWidget()
        img_layout = QGridLayout(img_page)
        img_layout.setContentsMargins(0, 0, 0, 0)
        img_layout.setHorizontalSpacing(12)
        img_layout.setVerticalSpacing(6)

        img_layout.addWidget(QLabel(i18n.t("convert.img_format")), 0, 0)
        self.img_format = QComboBox()
        self.img_format.setObjectName("ConvertCombo")
        img_layout.addWidget(self.img_format, 0, 1)

        img_layout.addWidget(QLabel(i18n.t("convert.img_quality")), 1, 0)
        self.img_quality = QSpinBox()
        self.img_quality.setObjectName("ConvertSpin")
        self.img_quality.setRange(1, 100)
        self.img_quality.setValue(90)
        img_layout.addWidget(self.img_quality, 1, 1)

        self.params_stack.addWidget(img_page)

        action_layout.addWidget(self.params_stack)
        card_layout.addWidget(action_host)

        btn_host = QWidget()
        btn_host.setObjectName("ConvertBtnHost")
        btn_host.setAutoFillBackground(False)
        btn_layout = QHBoxLayout(btn_host)
        btn_layout.setContentsMargins(36, 0, 36, 12)
        btn_layout.setSpacing(12)
        btn_layout.addStretch(1)

        self.btn_convert = QToolButton()
        self.btn_convert.setObjectName("ConvertRunBtn")
        self.btn_convert.setText(i18n.t("convert.run"))
        self.btn_convert.setCursor(Qt.PointingHandCursor)
        self.btn_convert.setEnabled(False)
        self.btn_convert.clicked.connect(self._run)
        btn_layout.addWidget(self.btn_convert)

        card_layout.addWidget(btn_host)

        self.progress = QProgressBar()
        self.progress.setObjectName("HashProgress")
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(6)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.hide()

        progress_host = QWidget()
        progress_host.setObjectName("ConvertProgressHost")
        progress_host.setAutoFillBackground(False)
        progress_layout = QVBoxLayout(progress_host)
        progress_layout.setContentsMargins(36, 0, 36, 12)
        progress_layout.addWidget(self.progress)
        card_layout.addWidget(progress_host)

        status_host = QWidget()
        status_host.setObjectName("ConvertStatusHost")
        status_host.setAutoFillBackground(False)
        status_layout = QVBoxLayout(status_host)
        status_layout.setContentsMargins(36, 0, 36, 24)
        status_layout.setSpacing(6)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("ConvertStatus")
        self.status_lbl.setAutoFillBackground(False)
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        status_layout.addWidget(self.status_lbl)

        card_layout.addWidget(status_host)

    def _update_action_ui(self):
        action = self.action_combo.currentData()
        if action == "encoding":
            self.params_stack.setCurrentIndex(0)
        elif action in ("base64_encode", "base64_decode"):
            self.params_stack.setCurrentIndex(0)
            self.params_stack.setCurrentIndex(0)
        elif action == "line_endings":
            self.params_stack.setCurrentIndex(1)
        elif action == "image":
            self.params_stack.setCurrentIndex(2)
            self._update_image_formats()

        self.btn_convert.setEnabled(bool(self._current_path))

    def _update_image_formats(self):
        self.img_format.clear()
        if not self._current_path:
            for f in cv.IMAGE_FORMATS:
                self.img_format.addItem(f, f)
            return
        for f in cv.image_targets(self._current_path):
            self.img_format.addItem(f, f)

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("convert.browse"), start
        )
        if path:
            self._set_file(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._set_file(path)

    def _set_file(self, path: str):
        self._current_path = path
        size = os.path.getsize(path)
        self.file_lbl.setText(
            f"{os.path.basename(path)}  •  {size:,} Б".replace(",", " ")
        )
        self.btn_convert.setEnabled(True)
        self._update_image_formats()

    def _run(self):
        if not self._current_path:
            return

        action = self.action_combo.currentData()
        params = {"src": self._current_path}
        suggested = self._suggest_dst(action)

        start = self.settings.default_dir or os.path.dirname(self._current_path)
        dst, _ = QFileDialog.getSaveFileName(
            self,
            i18n.t("convert.save_as"),
            os.path.join(start, suggested),
            "All files (*)",
        )
        if not dst:
            return
        params["dst"] = dst

        if action == "encoding":
            params["src_enc"] = self.src_enc.currentText()
            params["dst_enc"] = self.dst_enc.currentText()
        elif action == "line_endings":
            params["target"] = self.line_target.currentData()
        elif action == "image":
            params["target_format"] = self.img_format.currentData()
            params["quality"] = self.img_quality.value()

        self.progress.show()
        self.progress.setValue(0)
        self.btn_convert.setEnabled(False)
        self.status_lbl.setText("")

        self._thread = QThread(self)
        self._worker = ConvertWorker(action, params)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_thread)

        self._thread.start()

    def _suggest_dst(self, action: str) -> str:
        base = os.path.splitext(os.path.basename(self._current_path))[0]
        ext = os.path.splitext(self._current_path)[1]

        if action == "base64_encode":
            return f"{base}{ext}.b64"
        if action == "base64_decode":
            return f"{base}.decoded"
        if action == "line_endings":
            return f"{base}{ext}"
        if action == "image":
            target = self.img_format.currentData() if self.img_format.count() else "PNG"
            ext_map = {
                "PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp",
                "BMP": ".bmp", "TIFF": ".tiff", "GIF": ".gif",
            }
            return f"{base}{ext_map.get(target, '.bin')}"
        return f"{base}.converted{ext}"

    def _on_progress(self, processed: int, total: int):
        if total <= 0:
            return
        self.progress.setValue(int(processed * 100 / total))

    def _on_finished(self, dst: str):
        self.progress.hide()
        self.btn_convert.setEnabled(True)
        self.status_lbl.setText(f"✓  {i18n.t('convert.done')}:  {dst}")
        self.status_lbl.setProperty("state", "ok")
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

    def _on_failed(self, err: str):
        self.progress.hide()
        self.btn_convert.setEnabled(True)
        self.status_lbl.setText(f"✕  {i18n.t('convert.error')}: {err}")
        self.status_lbl.setProperty("state", "err")
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

    def _cleanup_thread(self):
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
        if self._thread:
            self._thread.deleteLater()
            self._thread = None

    def retranslate(self):
        self.btn_browse.setText(i18n.t("convert.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("convert.drop_hint"))
        self.btn_convert.setText(i18n.t("convert.run"))
        if not self._current_path:
            self.file_lbl.setText(i18n.t("convert.no_file"))