import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QCheckBox, QLineEdit,
    QMessageBox
)

from tools import permissions as perm
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

        self.text_lbl = QLabel(i18n.t("perm.drop_hint"))
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
            if path and os.path.exists(path):
                self.file_dropped.emit(path)
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.file_dropped.emit("__browse__")
        super().mousePressEvent(event)


def make_check(label_text: str) -> QCheckBox:
    cb = QCheckBox(label_text)
    cb.setObjectName("PermCheck")
    cb.setCursor(Qt.PointingHandCursor)
    return cb


class PermissionsPage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._unix_checks: dict[str, QCheckBox] = {}
        self._win_checks: dict[str, QCheckBox] = {}
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
        top.setObjectName("PermTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("perm.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("perm.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        top_layout.addWidget(title)
        top_layout.addStretch(1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("PermDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        info_host = QWidget()
        info_host.setObjectName("PermInfoHost")
        info_host.setAutoFillBackground(False)
        info_layout = QHBoxLayout(info_host)
        info_layout.setContentsMargins(36, 0, 36, 12)
        info_layout.setSpacing(10)

        self.file_lbl = QLabel(i18n.t("perm.no_file"))
        self.file_lbl.setObjectName("ConvertFileLabel")
        self.file_lbl.setAutoFillBackground(False)
        self.file_lbl.setWordWrap(True)
        info_layout.addWidget(self.file_lbl, 1)

        self.mode_lbl = QLabel("")
        self.mode_lbl.setObjectName("PermModeLabel")
        self.mode_lbl.setAutoFillBackground(False)
        info_layout.addWidget(self.mode_lbl)

        card_layout.addWidget(info_host)

        self.unix_host = QWidget()
        self.unix_host.setObjectName("PermUnixHost")
        self.unix_host.setAutoFillBackground(False)
        unix_layout = QVBoxLayout(self.unix_host)
        unix_layout.setContentsMargins(36, 0, 36, 12)
        unix_layout.setSpacing(8)

        unix_title = QLabel(i18n.t("perm.unix"))
        unix_title.setObjectName("ConvertSectionTitle")
        unix_title.setAutoFillBackground(False)
        unix_layout.addWidget(unix_title)

        grid_host = QWidget()
        grid_host.setObjectName("PermGrid")
        grid_host.setAutoFillBackground(False)
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(6)

        for col, key in enumerate(["perm.col.owner", "perm.col.group", "perm.col.other"], start=1):
            lbl = QLabel(i18n.t(key))
            lbl.setObjectName("PermColumn")
            lbl.setAutoFillBackground(False)
            grid.addWidget(lbl, 0, col)

        rows = ["read", "write", "exec"]
        for row, action in enumerate(rows, start=1):
            row_lbl = QLabel(i18n.t(f"perm.row.{action}"))
            row_lbl.setObjectName("PermRow")
            row_lbl.setAutoFillBackground(False)
            grid.addWidget(row_lbl, row, 0)

            for col, who in enumerate(["owner", "group", "other"], start=1):
                flag = f"{who}_{action}"
                cb = make_check("")
                cb.setProperty("flag", flag)
                cb.toggled.connect(self._on_unix_toggled)
                grid.addWidget(cb, row, col)
                self._unix_checks[flag] = cb

        unix_layout.addWidget(grid_host)
        card_layout.addWidget(self.unix_host)

        octal_host = QWidget()
        octal_host.setObjectName("PermOctalHost")
        octal_host.setAutoFillBackground(False)
        octal_layout = QHBoxLayout(octal_host)
        octal_layout.setContentsMargins(36, 0, 36, 12)
        octal_layout.setSpacing(10)

        lbl_oct = QLabel(i18n.t("perm.octal"))
        lbl_oct.setObjectName("HexLabel")
        lbl_oct.setAutoFillBackground(False)

        self.octal_input = QLineEdit()
        self.octal_input.setObjectName("HexInput")
        self.octal_input.setFixedWidth(90)
        self.octal_input.setMaxLength(3)
        self.octal_input.setPlaceholderText("755")
        self.octal_input.returnPressed.connect(self._apply_octal)

        btn_oct = QToolButton()
        btn_oct.setObjectName("InfoBrowseBtn")
        btn_oct.setText(i18n.t("perm.apply"))
        btn_oct.setCursor(Qt.PointingHandCursor)
        btn_oct.clicked.connect(self._apply_octal)

        octal_layout.addWidget(lbl_oct)
        octal_layout.addWidget(self.octal_input)
        octal_layout.addWidget(btn_oct)
        octal_layout.addStretch(1)

        card_layout.addWidget(octal_host)

        self.win_host = QWidget()
        self.win_host.setObjectName("PermWinHost")
        self.win_host.setAutoFillBackground(False)
        win_layout = QVBoxLayout(self.win_host)
        win_layout.setContentsMargins(36, 0, 36, 12)
        win_layout.setSpacing(8)

        win_title = QLabel(i18n.t("perm.win"))
        win_title.setObjectName("ConvertSectionTitle")
        win_title.setAutoFillBackground(False)
        win_layout.addWidget(win_title)

        win_grid_host = QWidget()
        win_grid_host.setObjectName("PermGrid")
        win_grid_host.setAutoFillBackground(False)
        win_grid = QGridLayout(win_grid_host)
        win_grid.setContentsMargins(0, 0, 0, 0)
        win_grid.setHorizontalSpacing(20)
        win_grid.setVerticalSpacing(6)

        for i, (flag, label_key) in enumerate([
            ("readonly", "perm.win.readonly"),
            ("hidden",   "perm.win.hidden"),
            ("system",   "perm.win.system"),
            ("archive",  "perm.win.archive"),
        ]):
            cb = make_check(i18n.t(label_key))
            cb.setProperty("flag", flag)
            win_grid.addWidget(cb, i // 2, i % 2)
            self._win_checks[flag] = cb

        win_layout.addWidget(win_grid_host)
        card_layout.addWidget(self.win_host)

        btn_host = QWidget()
        btn_host.setObjectName("PermBtnHost")
        btn_host.setAutoFillBackground(False)
        btn_layout = QHBoxLayout(btn_host)
        btn_layout.setContentsMargins(36, 0, 36, 12)
        btn_layout.setSpacing(10)
        btn_layout.addStretch(1)

        self.btn_apply = QToolButton()
        self.btn_apply.setObjectName("ConvertRunBtn")
        self.btn_apply.setText(i18n.t("perm.apply"))
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.setEnabled(False)
        self.btn_apply.clicked.connect(self._apply_all)
        btn_layout.addWidget(self.btn_apply)

        card_layout.addWidget(btn_host)

        status_host = QWidget()
        status_host.setObjectName("PermStatusHost")
        status_host.setAutoFillBackground(False)
        status_layout = QVBoxLayout(status_host)
        status_layout.setContentsMargins(36, 0, 36, 24)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("ConvertStatus")
        self.status_lbl.setAutoFillBackground(False)
        self.status_lbl.setWordWrap(True)
        status_layout.addWidget(self.status_lbl)

        card_layout.addWidget(status_host)
        card_layout.addStretch(1)

        self.win_host.setVisible(perm.IS_WINDOWS)
        if perm.IS_WINDOWS:
            unix_title.setText(i18n.t("perm.unix") + "  (приблизительно)")

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("perm.browse"), start
        )
        if path:
            self._load(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._load(path)

    def _load(self, path: str):
        try:
            data = perm.read_permissions(path)
        except OSError as e:
            QMessageBox.warning(self, i18n.t("perm.error"), str(e))
            return

        self._current_path = path
        name = os.path.basename(path)
        self.file_lbl.setText(name)
        self.mode_lbl.setText(
            f"{data['mode_octal']}  •  {perm.mode_to_rwx(data['mode_octal'])}"
        )

        for flag, cb in self._unix_checks.items():
            cb.blockSignals(True)
            cb.setChecked(bool(data["unix"].get(flag)))
            cb.blockSignals(False)

        if perm.IS_WINDOWS:
            for flag, cb in self._win_checks.items():
                cb.blockSignals(True)
                cb.setChecked(bool(data["win"].get(flag)))
                cb.blockSignals(False)

        self.octal_input.setText(data["mode_octal"])
        self.btn_apply.setEnabled(True)
        self.status_lbl.setText("")

    def _on_unix_toggled(self, _checked):
        mode = 0
        for name, _, oct_val in perm.PermissionModel.UNIX_FLAGS:
            cb = self._unix_checks.get(name)
            if cb and cb.isChecked():
                mode |= oct_val
        self.octal_input.setText(format(mode, "03o"))

    def _apply_octal(self):
        text = self.octal_input.text().strip()
        try:
            mode = int(text, 8) & 0o777
        except ValueError:
            QMessageBox.warning(self, i18n.t("perm.error"),
                                i18n.t("perm.bad_octal"))
            return

        for name, _, oct_val in perm.PermissionModel.UNIX_FLAGS:
            cb = self._unix_checks.get(name)
            if cb:
                cb.blockSignals(True)
                cb.setChecked(bool(mode & oct_val))
                cb.blockSignals(False)

        self.octal_input.setText(format(mode, "03o"))

    def _apply_all(self):
        if not self._current_path:
            return

        unix_flags = {f: cb.isChecked() for f, cb in self._unix_checks.items()}
        win_flags = {f: cb.isChecked() for f, cb in self._win_checks.items()}

        try:
            perm.apply_permissions(
                self._current_path,
                unix_flags=unix_flags,
                win_flags=win_flags,
            )
            self.status_lbl.setText(f"✓  {i18n.t('perm.done')}")
            self.status_lbl.setProperty("state", "ok")
            self.status_lbl.style().unpolish(self.status_lbl)
            self.status_lbl.style().polish(self.status_lbl)
            self._load(self._current_path)
        except (OSError, PermissionError) as e:
            self.status_lbl.setText(f"✕  {i18n.t('perm.error')}: {e}")
            self.status_lbl.setProperty("state", "err")
            self.status_lbl.style().unpolish(self.status_lbl)
            self.status_lbl.style().polish(self.status_lbl)

    def retranslate(self):
        self.btn_browse.setText(i18n.t("perm.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("perm.drop_hint"))
        self.btn_apply.setText(i18n.t("perm.apply"))
        if not self._current_path:
            self.file_lbl.setText(i18n.t("perm.no_file"))