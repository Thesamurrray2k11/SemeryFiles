# -*- coding: utf-8 -*-
"""
ui/pages/password_page.py

Страница инструмента «Генератор паролей».
"""

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QGuiApplication, QFont, QFontDatabase
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QToolButton, QSizePolicy, QCheckBox, QSlider, QSpinBox, QPlainTextEdit,
    QTabWidget, QProgressBar, QListWidget, QListWidgetItem, QMessageBox
)

from tools import password as pw
from core.i18n import i18n


class CopyButton(QToolButton):
    """Кнопка «копировать», которая ненадолго становится «✓»."""

    def __init__(self, get_text, parent=None):
        super().__init__(parent)
        self.setObjectName("InfoBrowseBtn")
        self.setText(i18n.t("pwd.copy"))
        self.setCursor(Qt.PointingHandCursor)
        self._get_text = get_text
        self.clicked.connect(self._do_copy)

    def _do_copy(self):
        text = self._get_text() if callable(self._get_text) else self._get_text
        if not text:
            return
        QGuiApplication.clipboard().setText(text)
        self.setText("✓")
        QTimer.singleShot(1200, lambda: self.setText(i18n.t("pwd.copy")))


# ==================================================================
#  PasswordPage
# ==================================================================
class PasswordPage(QWidget):
    """Страница «Генератор паролей»."""

    HISTORY_LIMIT = 50

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_password = ""
        self._history: list[str] = []
        self._build()
        self._generate()

    # ------------------------------------------------------------------
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

        # ---------- Заголовок ----------
        top = QWidget()
        top.setObjectName("PwdTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("pwd.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        top_layout.addWidget(title)
        top_layout.addStretch(1)

        card_layout.addWidget(top)

        # ---------- Табы ----------
        self.tabs = QTabWidget()
        self.tabs.setObjectName("RegexTabs")

        # ==================== Таб 1: Пароль ====================
        pwd_tab = QWidget()
        pwd_tab.setObjectName("RegexTabPage")
        pwd_layout = QVBoxLayout(pwd_tab)
        pwd_layout.setContentsMargins(36, 8, 36, 24)
        pwd_layout.setSpacing(14)

        # --- Поле вывода пароля ---
        output_row = QHBoxLayout()
        output_row.setSpacing(8)

        self.output = QPlainTextEdit()
        self.output.setObjectName("PwdOutput")
        self.output.setReadOnly(True)
        self.output.setFixedHeight(70)
        self.output.setLineWrapMode(QPlainTextEdit.WidgetWidth)

        f = QFont("Consolas")
        f.setStyleHint(QFont.Monospace)
        f.setPointSize(16)
        f.setBold(True)
        self.output.setFont(f)

        output_row.addWidget(self.output, 1)

        # Кнопки справа
        side_col = QVBoxLayout()
        side_col.setSpacing(6)

        self.btn_generate = QToolButton()
        self.btn_generate.setObjectName("ConvertRunBtn")
        self.btn_generate.setText(i18n.t("pwd.generate"))
        self.btn_generate.setCursor(Qt.PointingHandCursor)
        self.btn_generate.clicked.connect(self._generate)
        side_col.addWidget(self.btn_generate)

        self.btn_copy = CopyButton(lambda: self._current_password)
        side_col.addWidget(self.btn_copy)

        side_col.addStretch(1)
        output_row.addLayout(side_col)

        pwd_layout.addLayout(output_row)

        # --- Индикатор силы ---
        strength_row = QHBoxLayout()
        strength_row.setSpacing(8)

        self.strength_bar = QProgressBar()
        self.strength_bar.setObjectName("PwdStrength")
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setRange(0, 4)
        self.strength_bar.setValue(0)

        self.strength_lbl = QLabel("")
        self.strength_lbl.setObjectName("PwdStrengthLabel")
        self.strength_lbl.setAutoFillBackground(False)

        self.entropy_lbl = QLabel("")
        self.entropy_lbl.setObjectName("PwdStrengthLabel")
        self.entropy_lbl.setAutoFillBackground(False)

        strength_row.addWidget(self.strength_bar, 1)
        strength_row.addWidget(self.strength_lbl)
        strength_row.addSpacing(12)
        strength_row.addWidget(self.entropy_lbl)

        pwd_layout.addLayout(strength_row)

        # --- Длина ---
        length_row = QHBoxLayout()
        length_row.setSpacing(10)

        lbl_len = QLabel(i18n.t("pwd.length"))
        lbl_len.setObjectName("SettingsLabel")
        lbl_len.setAutoFillBackground(False)

        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setObjectName("PwdSlider")
        self.length_slider.setRange(4, 128)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self._on_length_changed)

        self.length_spin = QSpinBox()
        self.length_spin.setObjectName("ConvertSpin")
        self.length_spin.setRange(4, 128)
        self.length_spin.setValue(16)
        self.length_spin.valueChanged.connect(self._on_length_spin_changed)

        length_row.addWidget(lbl_len)
        length_row.addWidget(self.length_slider, 1)
        length_row.addWidget(self.length_spin)
        pwd_layout.addLayout(length_row)

        # --- Чекбоксы наборов ---
        sets_title = QLabel(i18n.t("pwd.sets"))
        sets_title.setObjectName("ConvertSectionTitle")
        sets_title.setAutoFillBackground(False)
        pwd_layout.addWidget(sets_title)

        sets_grid = QGridLayout()
        sets_grid.setHorizontalSpacing(24)
        sets_grid.setVerticalSpacing(6)

        self.cb_lower = QCheckBox(i18n.t("pwd.set.lower"))
        self.cb_upper = QCheckBox(i18n.t("pwd.set.upper"))
        self.cb_digits = QCheckBox(i18n.t("pwd.set.digits"))
        self.cb_symbols = QCheckBox(i18n.t("pwd.set.symbols"))
        for cb in (self.cb_lower, self.cb_upper, self.cb_digits, self.cb_symbols):
            cb.setObjectName("RegexFlag")
            cb.setChecked(True)
            cb.setCursor(Qt.PointingHandCursor)
            cb.toggled.connect(self._generate)

        sets_grid.addWidget(self.cb_lower, 0, 0)
        sets_grid.addWidget(self.cb_upper, 0, 1)
        sets_grid.addWidget(self.cb_digits, 0, 2)
        sets_grid.addWidget(self.cb_symbols, 0, 3)

        pwd_layout.addLayout(sets_grid)

        # --- Доп. опции ---
        extra_title = QLabel(i18n.t("pwd.extra"))
        extra_title.setObjectName("ConvertSectionTitle")
        extra_title.setAutoFillBackground(False)
        pwd_layout.addWidget(extra_title)

        extra_grid = QGridLayout()
        extra_grid.setHorizontalSpacing(24)
        extra_grid.setVerticalSpacing(6)

        self.cb_require = QCheckBox(i18n.t("pwd.opt.require"))
        self.cb_exclude_similar = QCheckBox(i18n.t("pwd.opt.no_similar"))
        self.cb_exclude_ambig = QCheckBox(i18n.t("pwd.opt.no_ambiguous"))
        self.cb_autocopy = QCheckBox(i18n.t("pwd.opt.autocopy"))
        for cb in (self.cb_require, self.cb_exclude_similar,
                   self.cb_exclude_ambig, self.cb_autocopy):
            cb.setObjectName("RegexFlag")
            cb.setCursor(Qt.PointingHandCursor)
        self.cb_require.setChecked(True)
        self.cb_require.toggled.connect(self._generate)
        self.cb_exclude_similar.toggled.connect(self._generate)
        self.cb_exclude_ambig.toggled.connect(self._generate)

        extra_grid.addWidget(self.cb_require, 0, 0)
        extra_grid.addWidget(self.cb_exclude_similar, 0, 1)
        extra_grid.addWidget(self.cb_exclude_ambig, 0, 2)
        extra_grid.addWidget(self.cb_autocopy, 0, 3)

        pwd_layout.addLayout(extra_grid)
        pwd_layout.addStretch(1)

        self.tabs.addTab(pwd_tab, i18n.t("pwd.tab.password"))

        # ==================== Таб 2: UUID ====================
        uuid_tab = QWidget()
        uuid_tab.setObjectName("RegexTabPage")
        uuid_layout = QVBoxLayout(uuid_tab)
        uuid_layout.setContentsMargins(36, 8, 36, 24)
        uuid_layout.setSpacing(12)

        uuid_row = QHBoxLayout()
        uuid_row.setSpacing(8)

        self.uuid_output = QPlainTextEdit()
        self.uuid_output.setObjectName("PwdOutput")
        self.uuid_output.setReadOnly(True)
        self.uuid_output.setFixedHeight(80)
        f2 = QFont("Consolas")
        f2.setStyleHint(QFont.Monospace)
        f2.setPointSize(12)
        self.uuid_output.setFont(f2)

        uuid_row.addWidget(self.uuid_output, 1)

        uuid_side = QVBoxLayout()
        uuid_side.setSpacing(6)

        self.btn_gen_uuid = QToolButton()
        self.btn_gen_uuid.setObjectName("ConvertRunBtn")
        self.btn_gen_uuid.setText(i18n.t("pwd.uuid.generate"))
        self.btn_gen_uuid.setCursor(Qt.PointingHandCursor)
        self.btn_gen_uuid.clicked.connect(self._generate_uuid)
        uuid_side.addWidget(self.btn_gen_uuid)

        self.btn_copy_uuid = CopyButton(lambda: self.uuid_output.toPlainText().strip())
        uuid_side.addWidget(self.btn_copy_uuid)

        uuid_side.addStretch(1)
        uuid_row.addLayout(uuid_side)

        uuid_layout.addLayout(uuid_row)

        # Количество UUID
        count_row = QHBoxLayout()
        count_row.setSpacing(10)

        lbl_count = QLabel(i18n.t("pwd.uuid.count"))
        lbl_count.setObjectName("SettingsLabel")
        lbl_count.setAutoFillBackground(False)

        self.uuid_count = QSpinBox()
        self.uuid_count.setObjectName("ConvertSpin")
        self.uuid_count.setRange(1, 100)
        self.uuid_count.setValue(1)
        self.uuid_count.valueChanged.connect(self._generate_uuid)

        count_row.addWidget(lbl_count)
        count_row.addWidget(self.uuid_count)
        count_row.addStretch(1)

        uuid_layout.addLayout(count_row)
        uuid_layout.addStretch(1)

        self.tabs.addTab(uuid_tab, "UUID v4")

        phrase_tab = QWidget()
        phrase_tab.setObjectName("RegexTabPage")
        phrase_layout = QVBoxLayout(phrase_tab)
        phrase_layout.setContentsMargins(36, 8, 36, 24)
        phrase_layout.setSpacing(12)

        phrase_row = QHBoxLayout()
        phrase_row.setSpacing(8)

        self.phrase_output = QPlainTextEdit()
        self.phrase_output.setObjectName("PwdOutput")
        self.phrase_output.setReadOnly(True)
        self.phrase_output.setFixedHeight(70)
        f3 = QFont("Consolas")
        f3.setStyleHint(QFont.Monospace)
        f3.setPointSize(13)
        self.phrase_output.setFont(f3)

        phrase_row.addWidget(self.phrase_output, 1)

        phrase_side = QVBoxLayout()
        phrase_side.setSpacing(6)

        self.btn_gen_phrase = QToolButton()
        self.btn_gen_phrase.setObjectName("ConvertRunBtn")
        self.btn_gen_phrase.setText(i18n.t("pwd.phrase.generate"))
        self.btn_gen_phrase.setCursor(Qt.PointingHandCursor)
        self.btn_gen_phrase.clicked.connect(self._generate_phrase)
        phrase_side.addWidget(self.btn_gen_phrase)

        self.btn_copy_phrase = CopyButton(lambda: self.phrase_output.toPlainText().strip())
        phrase_side.addWidget(self.btn_copy_phrase)

        phrase_side.addStretch(1)
        phrase_row.addLayout(phrase_side)

        phrase_layout.addLayout(phrase_row)

        phrase_grid = QGridLayout()
        phrase_grid.setHorizontalSpacing(20)
        phrase_grid.setVerticalSpacing(6)

        lbl_words = QLabel(i18n.t("pwd.phrase.words"))
        lbl_words.setObjectName("SettingsLabel")
        lbl_words.setAutoFillBackground(False)
        self.phrase_words = QSpinBox()
        self.phrase_words.setObjectName("ConvertSpin")
        self.phrase_words.setRange(2, 10)
        self.phrase_words.setValue(4)
        self.phrase_words.valueChanged.connect(self._generate_phrase)

        phrase_grid.addWidget(lbl_words, 0, 0)
        phrase_grid.addWidget(self.phrase_words, 0, 1)

        self.cb_phrase_capitalize = QCheckBox(i18n.t("pwd.phrase.capitalize"))
        self.cb_phrase_digit = QCheckBox(i18n.t("pwd.phrase.digit"))
        for cb in (self.cb_phrase_capitalize, self.cb_phrase_digit):
            cb.setObjectName("RegexFlag")
            cb.setChecked(True)
            cb.setCursor(Qt.PointingHandCursor)
            cb.toggled.connect(self._generate_phrase)

        phrase_grid.addWidget(self.cb_phrase_capitalize, 1, 0)
        phrase_grid.addWidget(self.cb_phrase_digit, 1, 1)

        phrase_layout.addLayout(phrase_grid)
        phrase_layout.addStretch(1)

        self.tabs.addTab(phrase_tab, i18n.t("pwd.tab.phrase"))

        history_tab = QWidget()
        history_tab.setObjectName("RegexTabPage")
        history_layout = QVBoxLayout(history_tab)
        history_layout.setContentsMargins(36, 8, 36, 24)
        history_layout.setSpacing(8)

        history_top = QHBoxLayout()
        history_top.addStretch(1)

        btn_clear = QToolButton()
        btn_clear.setObjectName("InfoBrowseBtn")
        btn_clear.setText(i18n.t("pwd.history.clear"))
        btn_clear.setCursor(Qt.PointingHandCursor)
        btn_clear.clicked.connect(self._clear_history)
        history_top.addWidget(btn_clear)

        history_layout.addLayout(history_top)

        self.history_list = QListWidget()
        self.history_list.setObjectName("SqliteTables")
        self.history_list.itemDoubleClicked.connect(self._history_copy)
        history_layout.addWidget(self.history_list, 1)

        self.tabs.addTab(history_tab, i18n.t("pwd.tab.history"))

        card_layout.addWidget(self.tabs, 1)

        self._generate_uuid()
        self._generate_phrase()

    def _on_length_changed(self, value: int):
        self.length_spin.blockSignals(True)
        self.length_spin.setValue(value)
        self.length_spin.blockSignals(False)
        self._generate()

    def _on_length_spin_changed(self, value: int):
        self.length_slider.blockSignals(True)
        self.length_slider.setValue(value)
        self.length_slider.blockSignals(False)
        self._generate()

    def _generate(self):
        try:
            password = pw.generate_password(
                length=self.length_spin.value(),
                use_lowercase=self.cb_lower.isChecked(),
                use_uppercase=self.cb_upper.isChecked(),
                use_digits=self.cb_digits.isChecked(),
                use_symbols=self.cb_symbols.isChecked(),
                exclude_similar=self.cb_exclude_similar.isChecked(),
                exclude_ambiguous=self.cb_exclude_ambig.isChecked(),
                require_each_type=self.cb_require.isChecked(),
            )
        except ValueError as e:
            self.output.setPlainText(str(e))
            return

        self._current_password = password
        self.output.setPlainText(password)

        info = pw.estimate_strength(password)
        self.strength_bar.setValue(info["score"])
        self.strength_bar.setProperty("score", info["score"])
        self.strength_bar.style().unpolish(self.strength_bar)
        self.strength_bar.style().polish(self.strength_bar)

        self.strength_lbl.setText(info["label"].upper())
        self.strength_lbl.setProperty("score", info["score"])
        self.strength_lbl.style().unpolish(self.strength_lbl)
        self.strength_lbl.style().polish(self.strength_lbl)

        self.entropy_lbl.setText(
            f"{info['entropy']} бит  •  взлом: {info['crack_time']}"
        )

        if password not in self._history:
            self._history.insert(0, password)
            if len(self._history) > self.HISTORY_LIMIT:
                self._history.pop()
            self._refresh_history()

        if self.cb_autocopy.isChecked():
            QGuiApplication.clipboard().setText(password)

    def _refresh_history(self):
        self.history_list.clear()
        for p in self._history:
            item = QListWidgetItem(p)
            self.history_list.addItem(item)

    def _history_copy(self, item: QListWidgetItem):
        QGuiApplication.clipboard().setText(item.text())

    def _clear_history(self):
        self._history.clear()
        self._refresh_history()

    def _generate_uuid(self):
        n = self.uuid_count.value()
        uuids = pw.generate_uuid_list(n)
        self.uuid_output.setPlainText("\n".join(uuids))

    def _generate_phrase(self):
        try:
            phrase = pw.generate_passphrase(
                word_count=self.phrase_words.value(),
                separator="-",
                add_digit=self.cb_phrase_digit.isChecked(),
                capitalize=self.cb_phrase_capitalize.isChecked(),
            )
        except Exception as e:
            self.phrase_output.setPlainText(str(e))
            return
        self.phrase_output.setPlainText(phrase)

    def retranslate(self):
        self.btn_generate.setText(i18n.t("pwd.generate"))
        self.btn_copy.setText(i18n.t("pwd.copy"))
        self.tabs.setTabText(0, i18n.t("pwd.tab.password"))
        self.tabs.setTabText(1, "UUID v4")
        self.tabs.setTabText(2, i18n.t("pwd.tab.phrase"))
        self.tabs.setTabText(3, i18n.t("pwd.tab.history"))