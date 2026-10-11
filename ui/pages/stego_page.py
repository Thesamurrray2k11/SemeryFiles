import os
from io import BytesIO

from PySide6.QtCore import Qt, Signal, QBuffer, QIODevice
from PySide6.QtGui import QPixmap, QImage, QGuiApplication
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QLineEdit, QPlainTextEdit,
    QTabWidget, QMessageBox, QRadioButton, QButtonGroup, QProgressBar,
    QScrollArea, QComboBox
)

from tools import steganography as st
from core.i18n import i18n


class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self, hint_key: str = "stego.drop_image", parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(80)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._hint_key = hint_key
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel("◐")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        self.icon_lbl.setFixedWidth(30)

        self.text_lbl = QLabel(i18n.t(self._hint_key))
        self.text_lbl.setObjectName("DropZoneText")
        self.text_lbl.setAutoFillBackground(False)

        layout.addStretch(1)
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.text_lbl)
        layout.addStretch(1)

    def refresh_text(self):
        self.text_lbl.setText(i18n.t(self._hint_key))

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



class StegoPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings

        self._cover_path: str | None = None
        self._payload_bytes: bytes = b""
        self._payload_name: str = ""

        self._extract_path: str | None = None
        self._extracted_data: bytes = b""

        self._build()
        self._update_capacity()

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
        top.setObjectName("StegoTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("stego.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        top_layout.addWidget(title)
        top_layout.addStretch(1)

        card_layout.addWidget(top)

        if not st.is_available():
            warn = QLabel(i18n.t("stego.no_pillow"))
            warn.setObjectName("MetaError")
            warn.setAlignment(Qt.AlignCenter)
            warn.setAutoFillBackground(False)
            warn.setWordWrap(True)
            card_layout.addWidget(warn)
            return

        self.tabs = QTabWidget()
        self.tabs.setObjectName("RegexTabs")

        hide_tab = QWidget()
        hide_tab.setObjectName("RegexTabPage")
        hide_layout = QVBoxLayout(hide_tab)
        hide_layout.setContentsMargins(36, 8, 36, 24)
        hide_layout.setSpacing(10)


        self.hide_drop = DropZone("stego.drop_image")
        self.hide_drop.file_dropped.connect(self._on_cover_dropped)
        hide_layout.addWidget(self.hide_drop)

        info_row = QHBoxLayout()
        info_row.setSpacing(10)

        self.cover_lbl = QLabel(i18n.t("stego.no_cover"))
        self.cover_lbl.setObjectName("ConvertFileLabel")
        self.cover_lbl.setAutoFillBackground(False)
        self.cover_lbl.setWordWrap(True)
        info_row.addWidget(self.cover_lbl, 1)

        self.capacity_lbl = QLabel("")
        self.capacity_lbl.setObjectName("EncConfidence")
        self.capacity_lbl.setAutoFillBackground(False)
        info_row.addWidget(self.capacity_lbl)

        hide_layout.addLayout(info_row)

        what_row = QHBoxLayout()
        what_row.setSpacing(12)

        self.rb_text = QRadioButton(i18n.t("stego.what_text"))
        self.rb_text.setObjectName("LangRadio")
        self.rb_text.setChecked(True)
        self.rb_text.toggled.connect(self._on_payload_type_changed)

        self.rb_file = QRadioButton(i18n.t("stego.what_file"))
        self.rb_file.setObjectName("LangRadio")
        self.rb_file.toggled.connect(self._on_payload_type_changed)

        self._what_group = QButtonGroup(self)
        self._what_group.addButton(self.rb_text, 0)
        self._what_group.addButton(self.rb_file, 1)

        what_row.addWidget(self.rb_text)
        what_row.addWidget(self.rb_file)
        what_row.addStretch(1)

        hide_layout.addLayout(what_row)

        density_title = QLabel(i18n.t("stego.density"))
        density_title.setObjectName("ConvertSectionTitle")
        density_title.setAutoFillBackground(False)
        hide_layout.addWidget(density_title)

        density_row = QHBoxLayout()
        density_row.setSpacing(12)

        self.rb_1bit = QRadioButton(i18n.t("stego.density.1bit"))
        self.rb_1bit.setObjectName("LangRadio")
        self.rb_1bit.setChecked(True)
        self.rb_1bit.toggled.connect(self._on_density_changed)

        self.rb_2bit = QRadioButton(i18n.t("stego.density.2bit"))
        self.rb_2bit.setObjectName("LangRadio")
        self.rb_2bit.toggled.connect(self._on_density_changed)

        self._density_group = QButtonGroup(self)
        self._density_group.addButton(self.rb_1bit, 0)
        self._density_group.addButton(self.rb_2bit, 1)

        density_row.addWidget(self.rb_1bit)
        density_row.addWidget(self.rb_2bit)
        density_row.addStretch(1)
        hide_layout.addLayout(density_row)

        density_hint = QLabel(i18n.t("stego.density.hint"))
        density_hint.setObjectName("SettingsHint")
        density_hint.setAutoFillBackground(False)
        density_hint.setWordWrap(True)
        hide_layout.addWidget(density_hint)

        self.text_input = QPlainTextEdit()
        self.text_input.setObjectName("SqliteSqlInput")
        self.text_input.setFixedHeight(90)
        self.text_input.setPlaceholderText(i18n.t("stego.text_hint"))
        hide_layout.addWidget(self.text_input)

        file_row = QHBoxLayout()
        file_row.setSpacing(8)

        self.file_lbl = QLabel(i18n.t("stego.no_payload_file"))
        self.file_lbl.setObjectName("ConvertFileLabel")
        self.file_lbl.setAutoFillBackground(False)
        self.file_lbl.setWordWrap(True)

        self.btn_pick_payload = QToolButton()
        self.btn_pick_payload.setObjectName("InfoBrowseBtn")
        self.btn_pick_payload.setText(i18n.t("stego.pick_payload"))
        self.btn_pick_payload.setCursor(Qt.PointingHandCursor)
        self.btn_pick_payload.clicked.connect(self._pick_payload_file)

        file_row.addWidget(self.file_lbl, 1)
        file_row.addWidget(self.btn_pick_payload)
        hide_layout.addLayout(file_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background:#3A3D43;border:none;")
        hide_layout.addWidget(sep)

        pwd_title = QLabel(i18n.t("stego.protection"))
        pwd_title.setObjectName("ConvertSectionTitle")
        pwd_title.setAutoFillBackground(False)
        hide_layout.addWidget(pwd_title)

        self.rb_no_pwd = QRadioButton(i18n.t("stego.no_password"))
        self.rb_no_pwd.setObjectName("LangRadio")
        self.rb_no_pwd.setChecked(True)
        self.rb_no_pwd.toggled.connect(self._on_password_mode_changed)

        self.rb_with_pwd = QRadioButton(i18n.t("stego.with_password"))
        self.rb_with_pwd.setObjectName("LangRadio")
        self.rb_with_pwd.toggled.connect(self._on_password_mode_changed)

        pwd_mode_row = QHBoxLayout()
        pwd_mode_row.setSpacing(14)
        pwd_mode_row.addWidget(self.rb_no_pwd)
        pwd_mode_row.addWidget(self.rb_with_pwd)
        pwd_mode_row.addStretch(1)
        hide_layout.addLayout(pwd_mode_row)

        pwd_input_row = QHBoxLayout()
        pwd_input_row.setSpacing(8)

        lbl_pwd = QLabel(i18n.t("stego.password"))
        lbl_pwd.setObjectName("HexLabel")
        lbl_pwd.setAutoFillBackground(False)

        self.pwd_input = QLineEdit()
        self.pwd_input.setObjectName("RegexInput")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setPlaceholderText(i18n.t("stego.password_hint"))
        self.pwd_input.setEnabled(False)
        self.pwd_input.textChanged.connect(self._check_ready)

        self.btn_show_pwd = QToolButton()
        self.btn_show_pwd.setObjectName("InfoBrowseBtn")
        self.btn_show_pwd.setText("👁")
        self.btn_show_pwd.setCursor(Qt.PointingHandCursor)
        self.btn_show_pwd.setCheckable(True)
        self.btn_show_pwd.toggled.connect(self._toggle_pwd_visibility)

        pwd_input_row.addWidget(lbl_pwd)
        pwd_input_row.addWidget(self.pwd_input, 1)
        pwd_input_row.addWidget(self.btn_show_pwd)
        hide_layout.addLayout(pwd_input_row)

        hide_layout.addStretch(1)

        self.hide_progress = QProgressBar()
        self.hide_progress.setObjectName("HashProgress")
        self.hide_progress.setTextVisible(False)
        self.hide_progress.setFixedHeight(6)
        self.hide_progress.hide()
        hide_layout.addWidget(self.hide_progress)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)

        self.btn_hide = QToolButton()
        self.btn_hide.setObjectName("ConvertRunBtn")
        self.btn_hide.setText(i18n.t("stego.hide"))
        self.btn_hide.setCursor(Qt.PointingHandCursor)
        self.btn_hide.clicked.connect(self._do_hide)
        self.btn_hide.setEnabled(False)
        btn_row.addWidget(self.btn_hide)
        hide_layout.addLayout(btn_row)

        self.hide_status = QLabel("")
        self.hide_status.setObjectName("ConvertStatus")
        self.hide_status.setAutoFillBackground(False)
        self.hide_status.setWordWrap(True)
        hide_layout.addWidget(self.hide_status)

        self.tabs.addTab(hide_tab, i18n.t("stego.tab.hide"))

        extract_tab = QWidget()
        extract_tab.setObjectName("RegexTabPage")
        extract_layout = QVBoxLayout(extract_tab)
        extract_layout.setContentsMargins(36, 8, 36, 24)
        extract_layout.setSpacing(10)

        self.extract_drop = DropZone("stego.drop_stego")
        self.extract_drop.file_dropped.connect(self._on_extract_dropped)
        extract_layout.addWidget(self.extract_drop)

        ex_info_row = QHBoxLayout()
        ex_info_row.setSpacing(10)

        self.extract_lbl = QLabel(i18n.t("stego.no_stego"))
        self.extract_lbl.setObjectName("ConvertFileLabel")
        self.extract_lbl.setAutoFillBackground(False)
        self.extract_lbl.setWordWrap(True)
        ex_info_row.addWidget(self.extract_lbl, 1)
        extract_layout.addLayout(ex_info_row)

        ex_pwd_row = QHBoxLayout()
        ex_pwd_row.setSpacing(8)

        lbl_ex_pwd = QLabel(i18n.t("stego.password"))
        lbl_ex_pwd.setObjectName("HexLabel")
        lbl_ex_pwd.setAutoFillBackground(False)

        self.extract_pwd = QLineEdit()
        self.extract_pwd.setObjectName("RegexInput")
        self.extract_pwd.setEchoMode(QLineEdit.Password)
        self.extract_pwd.setPlaceholderText(i18n.t("stego.password_hint"))
        self.extract_pwd.textChanged.connect(self._check_ready)

        self.btn_show_ex_pwd = QToolButton()
        self.btn_show_ex_pwd.setObjectName("InfoBrowseBtn")
        self.btn_show_ex_pwd.setText("👁")
        self.btn_show_ex_pwd.setCursor(Qt.PointingHandCursor)
        self.btn_show_ex_pwd.setCheckable(True)
        self.btn_show_ex_pwd.toggled.connect(self._toggle_ex_pwd_visibility)

        ex_pwd_row.addWidget(lbl_ex_pwd)
        ex_pwd_row.addWidget(self.extract_pwd, 1)
        ex_pwd_row.addWidget(self.btn_show_ex_pwd)
        extract_layout.addLayout(ex_pwd_row)

        ex_btn_row = QHBoxLayout()
        ex_btn_row.addStretch(1)

        self.btn_extract = QToolButton()
        self.btn_extract.setObjectName("ConvertRunBtn")
        self.btn_extract.setText(i18n.t("stego.extract"))
        self.btn_extract.setCursor(Qt.PointingHandCursor)
        self.btn_extract.clicked.connect(self._do_extract)
        self.btn_extract.setEnabled(False)
        ex_btn_row.addWidget(self.btn_extract)
        extract_layout.addLayout(ex_btn_row)

        result_title = QLabel(i18n.t("stego.result"))
        result_title.setObjectName("ConvertSectionTitle")
        result_title.setAutoFillBackground(False)
        extract_layout.addWidget(result_title)

        self.result_view = QPlainTextEdit()
        self.result_view.setObjectName("EncPreview")
        self.result_view.setReadOnly(True)
        self.result_view.setPlaceholderText(i18n.t("stego.result_hint"))
        extract_layout.addWidget(self.result_view, 1)

        res_btn_row = QHBoxLayout()
        res_btn_row.setSpacing(8)

        self.btn_copy_result = QToolButton()
        self.btn_copy_result.setObjectName("InfoBrowseBtn")
        self.btn_copy_result.setText(i18n.t("stego.copy_result"))
        self.btn_copy_result.setCursor(Qt.PointingHandCursor)
        self.btn_copy_result.clicked.connect(self._copy_result)
        self.btn_copy_result.setEnabled(False)

        self.btn_save_result = QToolButton()
        self.btn_save_result.setObjectName("InfoBrowseBtn")
        self.btn_save_result.setText(i18n.t("stego.save_result"))
        self.btn_save_result.setCursor(Qt.PointingHandCursor)
        self.btn_save_result.clicked.connect(self._save_result)
        self.btn_save_result.setEnabled(False)

        res_btn_row.addWidget(self.btn_copy_result)
        res_btn_row.addWidget(self.btn_save_result)
        res_btn_row.addStretch(1)
        extract_layout.addLayout(res_btn_row)

        self.extract_status = QLabel("")
        self.extract_status.setObjectName("ConvertStatus")
        self.extract_status.setAutoFillBackground(False)
        self.extract_status.setWordWrap(True)
        extract_layout.addWidget(self.extract_status)

        self.tabs.addTab(extract_tab, i18n.t("stego.tab.extract"))

        card_layout.addWidget(self.tabs, 1)

    def _on_cover_dropped(self, path: str):
        if path == "__browse__":
            start = self.settings.default_dir or os.path.expanduser("~")
            path, _ = QFileDialog.getOpenFileName(
                self, i18n.t("stego.drop_image"), start,
                "PNG (*.png);;Все файлы (*)"
            )
            if not path:
                return

        ext = os.path.splitext(path)[1].lower()
        if ext != ".png":
            QMessageBox.warning(
                self, i18n.t("stego.error"),
                i18n.t("stego.only_png")
            )
            return

        self._cover_path = path
        size = os.path.getsize(path)
        self.cover_lbl.setText(
            f"{os.path.basename(path)}  •  {size:,} Б".replace(",", " ")
        )
        self._update_capacity()
        self._check_ready()

    def _update_capacity(self):
        if not self._cover_path:
            self.capacity_lbl.setText("")
            return
        cap = st.capacity_bytes(self._cover_path, bits_per_channel=self._bits_per_channel())
        self.capacity_lbl.setText(
            i18n.t("stego.capacity").format(
                cap=self._format_size(cap)
            )
        )

    @staticmethod
    def _format_size(n: int) -> str:
        f = float(n)
        for suf in ("Б", "KiB", "MiB", "GiB"):
            if f < 1024:
                return f"{int(f)} {suf}" if suf == "Б" else f"{f:.2f} {suf}"
            f /= 1024
        return f"{f:.2f} TiB"

    def _on_payload_type_changed(self):
        is_text = self.rb_text.isChecked()
        self.text_input.setVisible(is_text)
        self.file_lbl.setVisible(not is_text)
        self.btn_pick_payload.setVisible(not is_text)
        self._check_ready()

    def _pick_payload_file(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("stego.pick_payload"), start,
            "Все файлы (*)"
        )
        if not path:
            return
        size = os.path.getsize(path)
        self._payload_name = os.path.basename(path)
        self._payload_bytes = b""
        self.file_lbl.setText(
            f"{self._payload_name}  •  {self._format_size(size)}"
        )
        self._payload_file_path = path
        self._check_ready()

    def _on_password_mode_changed(self):
        use_pwd = self.rb_with_pwd.isChecked()
        self.pwd_input.setEnabled(use_pwd)
        self.btn_show_pwd.setEnabled(use_pwd)
        if not use_pwd:
            self.pwd_input.clear()
            self.btn_show_pwd.setChecked(False)
        self._check_ready()
    def _on_density_changed(self):
        self._update_capacity()
        self._check_ready()
    def _bits_per_channel(self) -> int:
        return 2 if self.rb_2bit.isChecked() else 1

    def _toggle_pwd_visibility(self, checked: bool):
        self.pwd_input.setEchoMode(
            QLineEdit.Normal if checked else QLineEdit.Password
        )

    def _toggle_ex_pwd_visibility(self, checked: bool):
        self.extract_pwd.setEchoMode(
            QLineEdit.Normal if checked else QLineEdit.Password
        )

    def _check_ready(self):
        ready = bool(self._cover_path)
        if self.rb_text.isChecked():
            ready = ready and bool(self.text_input.toPlainText().strip())
        else:
            ready = ready and hasattr(self, "_payload_file_path")

        if self.rb_with_pwd.isChecked():
            ready = ready and bool(self.pwd_input.text())

        self.btn_hide.setEnabled(ready)

        self.btn_extract.setEnabled(bool(self._extract_path))

    def _do_hide(self):
        if not self._cover_path:
            return

        if self.rb_text.isChecked():
            data = self.text_input.toPlainText().encode("utf-8")
        else:
            path = getattr(self, "_payload_file_path", None)
            if not path:
                return
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except OSError as e:
                QMessageBox.warning(self, i18n.t("stego.error"), str(e))
                return

        bits = self._bits_per_channel()
        cap = st.capacity_bytes(self._cover_path, bits_per_channel=bits)
        overhead = 9 + (28 + 16 if self.rb_with_pwd.isChecked() else 0)
        if len(data) + overhead > cap:
            QMessageBox.warning(
                self, i18n.t("stego.error"),
                i18n.t("stego.too_big").format(
                    payload=self._format_size(len(data)),
                    cap=self._format_size(cap),
                )
            )
            return

        password = self.pwd_input.text() if self.rb_with_pwd.isChecked() else None

        start = self.settings.default_dir or os.path.dirname(self._cover_path)
        base, _ = os.path.splitext(os.path.basename(self._cover_path))
        dst, _ = QFileDialog.getSaveFileName(
            self, i18n.t("stego.save_stego"),
            os.path.join(start, f"{base}.stego.png"),
            "PNG (*.png)"
        )
        if not dst:
            return

        self.hide_progress.show()
        self.hide_progress.setValue(20)
        self.btn_hide.setEnabled(False)

        result = st.hide_in_image(
            self._cover_path, dst, data,
            password=password,
            bits_per_channel=bits,
        )

        self.hide_progress.setValue(100)
        self.hide_progress.hide()
        self.btn_hide.setEnabled(True)

        if not result["ok"]:
            err = result.get("error", "unknown")
            self._set_status(
                self.hide_status, f"✕ {i18n.t('stego.error')}: {err}", "err"
            )
            return

        self._set_status(
            self.hide_status,
            f"✓ {i18n.t('stego.done')}: {dst}",
            "ok"
        )

    def _on_extract_dropped(self, path: str):
        if path == "__browse__":
            start = self.settings.default_dir or os.path.expanduser("~")
            path, _ = QFileDialog.getOpenFileName(
                self, i18n.t("stego.drop_stego"), start,
                "PNG (*.png);;Все файлы (*)"
            )
            if not path:
                return

        self._extract_path = path
        self.extract_lbl.setText(os.path.basename(path))
        self._check_ready()
        self._set_status(self.extract_status, "", "")

    def _do_extract(self):
        if not self._extract_path:
            return

        password = self.extract_pwd.text() or None

        result = st.extract_from_image(self._extract_path, password=password)

        self.result_view.setPlainText("")
        self._extracted_data = b""
        self.btn_copy_result.setEnabled(False)
        self.btn_save_result.setEnabled(False)

        if not result["ok"]:
            err = result.get("error", "unknown")
            if err == "no_magic":
                msg = i18n.t("stego.err.no_magic")
            elif err == "password_required":
                msg = i18n.t("stego.err.password_required")
            elif err == "wrong_password":
                msg = i18n.t("stego.err.wrong_password")
            elif err.startswith("capacity") or err.startswith("bad_length"):
                msg = i18n.t("stego.err.corrupted")
            else:
                msg = f"{i18n.t('stego.error')}: {err}"
            self._set_status(self.extract_status, f"✕ {msg}", "err")
            return

        data = result["data"]
        self._extracted_data = data

        try:
            text = data.decode("utf-8")
            self.result_view.setPlainText(text)
        except UnicodeDecodeError:
            self.result_view.setPlainText(
                i18n.t("stego.binary_data").format(
                    size=self._format_size(len(data))
                )
            )

        self.btn_copy_result.setEnabled(True)
        self.btn_save_result.setEnabled(True)

        self._set_status(
            self.extract_status,
            f"✓ {i18n.t('stego.extracted')}: {self._format_size(len(data))}",
            "ok"
        )

    def _copy_result(self):
        if not self._extracted_data:
            return
        try:
            QGuiApplication.clipboard().setText(
                self._extracted_data.decode("utf-8")
            )
        except UnicodeDecodeError:
            QGuiApplication.clipboard().setImage(
                QImage.fromData(self._extracted_data)
            )

    def _save_result(self):
        if not self._extracted_data:
            return
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("stego.save_result"),
            os.path.join(start, "extracted.bin"),
            "Все файлы (*)"
        )
        if not path:
            return
        try:
            with open(path, "wb") as f:
                f.write(self._extracted_data)
        except OSError as e:
            QMessageBox.warning(self, i18n.t("stego.error"), str(e))

    def _set_status(self, label: QLabel, text: str, state: str):
        label.setText(text)
        label.setProperty("state", state)
        label.style().unpolish(label)
        label.style().polish(label)

    def retranslate(self):
        self.tabs.setTabText(0, i18n.t("stego.tab.hide"))
        self.tabs.setTabText(1, i18n.t("stego.tab.extract"))
        self.btn_hide.setText(i18n.t("stego.hide"))
        self.btn_extract.setText(i18n.t("stego.extract"))
        self.btn_copy_result.setText(i18n.t("stego.copy_result"))
        self.btn_save_result.setText(i18n.t("stego.save_result"))
        self.btn_pick_payload.setText(i18n.t("stego.pick_payload"))
        self.rb_1bit.setText(i18n.t("stego.density.1bit"))
        self.rb_2bit.setText(i18n.t("stego.density.2bit"))