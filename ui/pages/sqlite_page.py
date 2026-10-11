import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QToolButton, QFileDialog, QSizePolicy, QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QPlainTextEdit,
    QTabWidget, QMessageBox, QSpinBox, QCheckBox, QComboBox,
    QAbstractItemView
)

from tools import sqlite_tool as sq
from core.i18n import i18n


PAGE_SIZE_DEFAULT = 100


class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(80)
        self.setMaximumHeight(90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel("▤")
        self.icon_lbl.setObjectName("DropZoneIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        self.icon_lbl.setAutoFillBackground(False)
        self.icon_lbl.setFixedWidth(30)

        self.text_lbl = QLabel(i18n.t("sqlite.drop_hint"))
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


class SqlitePage(QWidget):

    def __init__(self, app_settings, parent=None):
        super().__init__(parent)
        self.settings = app_settings
        self._current_path: str | None = None
        self._conn = None
        self._tables: list[dict] = []
        self._current_table: str | None = None
        self._schema: list[dict] = []
        self._offset = 0
        self._page_size = PAGE_SIZE_DEFAULT
        self._total_rows = 0
        self._columns: list[str] = []
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
        top.setObjectName("SqliteTopBar")
        top.setAutoFillBackground(False)
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(36, 24, 36, 12)
        top_layout.setSpacing(12)

        title = QLabel(i18n.t("sqlite.title"))
        title.setObjectName("WorkspaceTitle")
        title.setAutoFillBackground(False)

        self.btn_browse = QToolButton()
        self.btn_browse.setObjectName("InfoBrowseBtn")
        self.btn_browse.setText(i18n.t("sqlite.browse"))
        self.btn_browse.setCursor(Qt.PointingHandCursor)
        self.btn_browse.clicked.connect(self._open_dialog)

        self.lbl_path = QLabel("")
        self.lbl_path.setObjectName("ConvertFileLabel")
        self.lbl_path.setAutoFillBackground(False)
        self.lbl_path.setWordWrap(True)

        top_layout.addWidget(title)
        top_layout.addWidget(self.lbl_path, 1)
        top_layout.addWidget(self.btn_browse)

        card_layout.addWidget(top)

        drop_host = QWidget()
        drop_host.setObjectName("SqliteDropHost")
        drop_host.setAutoFillBackground(False)
        drop_layout = QVBoxLayout(drop_host)
        drop_layout.setContentsMargins(36, 0, 36, 12)

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_drop)
        drop_layout.addWidget(self.drop_zone)

        card_layout.addWidget(drop_host)

        main_host = QWidget()
        main_host.setObjectName("SqliteMainHost")
        main_host.setAutoFillBackground(False)
        main_layout = QHBoxLayout(main_host)
        main_layout.setContentsMargins(36, 0, 36, 24)
        main_layout.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(6)

        lbl_tables = QLabel(i18n.t("sqlite.tables"))
        lbl_tables.setObjectName("RegexSectionLabel")
        lbl_tables.setAutoFillBackground(False)
        left.addWidget(lbl_tables)

        self.tables_list = QListWidget()
        self.tables_list.setObjectName("SqliteTables")
        self.tables_list.setMinimumWidth(220)
        self.tables_list.setMaximumWidth(320)
        self.tables_list.itemSelectionChanged.connect(self._on_table_selected)
        left.addWidget(self.tables_list, 1)

        right = QVBoxLayout()
        right.setSpacing(6)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("RegexTabs")

        data_tab = QWidget()
        data_tab.setObjectName("RegexTabPage")
        data_layout = QVBoxLayout(data_tab)
        data_layout.setContentsMargins(0, 8, 0, 0)
        data_layout.setSpacing(8)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)

        lbl_page = QLabel(i18n.t("sqlite.per_page"))
        lbl_page.setObjectName("HexLabel")
        lbl_page.setAutoFillBackground(False)

        self.page_spin = QSpinBox()
        self.page_spin.setObjectName("ConvertSpin")
        self.page_spin.setRange(10, 5000)
        self.page_spin.setValue(PAGE_SIZE_DEFAULT)
        self.page_spin.setSingleStep(50)
        self.page_spin.valueChanged.connect(self._on_page_size_changed)

        self.btn_prev = QToolButton()
        self.btn_prev.setObjectName("InfoBrowseBtn")
        self.btn_prev.setText("◀")
        self.btn_prev.setCursor(Qt.PointingHandCursor)
        self.btn_prev.clicked.connect(self._prev_page)

        self.lbl_page_info = QLabel("")
        self.lbl_page_info.setObjectName("HexInfo")
        self.lbl_page_info.setAutoFillBackground(False)
        self.lbl_page_info.setAlignment(Qt.AlignCenter)
        self.lbl_page_info.setMinimumWidth(160)

        self.btn_next = QToolButton()
        self.btn_next.setObjectName("InfoBrowseBtn")
        self.btn_next.setText("▶")
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.clicked.connect(self._next_page)

        self.btn_export = QToolButton()
        self.btn_export.setObjectName("InfoBrowseBtn")
        self.btn_export.setText(i18n.t("sqlite.export_csv"))
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self._export_csv)

        ctrl.addWidget(lbl_page)
        ctrl.addWidget(self.page_spin)
        ctrl.addSpacing(12)
        ctrl.addWidget(self.btn_prev)
        ctrl.addWidget(self.lbl_page_info)
        ctrl.addWidget(self.btn_next)
        ctrl.addStretch(1)
        ctrl.addWidget(self.btn_export)
        data_layout.addLayout(ctrl)

        self.data_table = QTableWidget(0, 0)
        self.data_table.setObjectName("SqliteDataTable")
        self.data_table.verticalHeader().setVisible(True)
        self.data_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table.itemChanged.connect(self._on_cell_changed)
        self._suppress_item_changed = False
        data_layout.addWidget(self.data_table, 1)

        self.tabs.addTab(data_tab, i18n.t("sqlite.tab.data"))

        schema_tab = QWidget()
        schema_tab.setObjectName("RegexTabPage")
        schema_layout = QVBoxLayout(schema_tab)
        schema_layout.setContentsMargins(0, 8, 0, 0)

        self.schema_table = QTableWidget(0, 5)
        self.schema_table.setObjectName("SqliteSchemaTable")
        self.schema_table.setHorizontalHeaderLabels([
            "#", i18n.t("sqlite.col.name"), i18n.t("sqlite.col.type"),
            "NOT NULL", "PK",
        ])
        self.schema_table.verticalHeader().setVisible(False)
        self.schema_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.schema_table.setAlternatingRowColors(True)
        hdr = self.schema_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        schema_layout.addWidget(self.schema_table)

        self.tabs.addTab(schema_tab, i18n.t("sqlite.tab.schema"))

        sql_tab = QWidget()
        sql_tab.setObjectName("RegexTabPage")
        sql_layout = QVBoxLayout(sql_tab)
        sql_layout.setContentsMargins(0, 8, 0, 0)
        sql_layout.setSpacing(8)

        self.sql_input = QPlainTextEdit()
        self.sql_input.setObjectName("SqliteSqlInput")
        self.sql_input.setPlaceholderText(
            i18n.t("sqlite.sql_hint")
        )
        self.sql_input.setFixedHeight(90)
        sql_layout.addWidget(self.sql_input)

        sql_btn_row = QHBoxLayout()
        sql_btn_row.setSpacing(8)

        self.btn_run = QToolButton()
        self.btn_run.setObjectName("ConvertRunBtn")
        self.btn_run.setText(i18n.t("sqlite.run"))
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.clicked.connect(self._run_sql)

        self.lbl_sql_status = QLabel("")
        self.lbl_sql_status.setObjectName("RegexStatus")
        self.lbl_sql_status.setAutoFillBackground(False)

        sql_btn_row.addWidget(self.btn_run)
        sql_btn_row.addWidget(self.lbl_sql_status, 1)
        sql_layout.addLayout(sql_btn_row)

        self.sql_result = QTableWidget(0, 0)
        self.sql_result.setObjectName("SqliteDataTable")
        self.sql_result.verticalHeader().setVisible(False)
        self.sql_result.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sql_result.setAlternatingRowColors(True)
        sql_layout.addWidget(self.sql_result, 1)

        self.tabs.addTab(sql_tab, i18n.t("sqlite.tab.sql"))

        right.addWidget(self.tabs, 1)
        main_layout.addLayout(left, 0)
        main_layout.addLayout(right, 1)

        card_layout.addWidget(main_host, 1)

    def _open_dialog(self):
        start = self.settings.default_dir or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.t("sqlite.browse"), start,
            "SQLite базы (*.db *.sqlite *.sqlite3 *.db3);;Все файлы (*)"
        )
        if path:
            self._load_db(path)

    def _on_drop(self, path: str):
        if path == "__browse__":
            self._open_dialog()
        else:
            self._load_db(path)

    def _load_db(self, path: str):
        if not sq.is_sqlite_file(path):
            QMessageBox.warning(self, i18n.t("sqlite.error"),
                                i18n.t("sqlite.not_sqlite"))
            return

        self._close_connection()

        try:
            self._conn = sq.open_database(path, read_only=False)
        except Exception as e:
            QMessageBox.warning(self, i18n.t("sqlite.error"), str(e))
            return

        self._current_path = path
        self.lbl_path.setText(path)

        self.tables_list.clear()
        self._tables = sq.list_tables(self._conn)
        for t in self._tables:
            label = t["name"]
            if t["rows"] is not None:
                label += f"  ({t['rows']})"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, t["name"])
            self.tables_list.addItem(item)

        self._current_table = None
        self._offset = 0
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.schema_table.setRowCount(0)

        if self.tables_list.count() > 0:
            self.tables_list.setCurrentRow(0)

    def _close_connection(self):
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    def _on_table_selected(self):
        items = self.tables_list.selectedItems()
        if not items:
            return
        name = items[0].data(Qt.UserRole)
        if not name or name == self._current_table:
            return
        self._current_table = name
        self._offset = 0
        self._schema = sq.table_schema(self._conn, name)
        try:
            self._total_rows = sq.count_rows(self._conn, name)
        except Exception:
            self._total_rows = 0

        self._load_page()
        self._fill_schema()

    def _fill_schema(self):
        self.schema_table.setRowCount(len(self._schema))
        for i, col in enumerate(self._schema):
            self.schema_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.schema_table.setItem(i, 1, QTableWidgetItem(col["name"]))
            self.schema_table.setItem(i, 2, QTableWidgetItem(col["type"]))
            self.schema_table.setItem(i, 3, QTableWidgetItem("✓" if col["notnull"] else ""))
            self.schema_table.setItem(i, 4, QTableWidgetItem("✓" if col["pk"] else ""))

    def _load_page(self):
        if not self._current_table:
            return
        try:
            rows = sq.read_rows(
                self._conn, self._current_table,
                offset=self._offset, limit=self._page_size,
            )
        except Exception as e:
            QMessageBox.warning(self, i18n.t("sqlite.error"), str(e))
            return

        if self._schema:
            self._columns = [c["name"] for c in self._schema]
        elif rows:
            self._columns = list(rows[0].keys())
        else:
            self._columns = []

        self._suppress_item_changed = True
        self.data_table.clear()
        self.data_table.setColumnCount(len(self._columns))
        self.data_table.setHorizontalHeaderLabels(self._columns)
        self.data_table.setRowCount(len(rows))

        for r, row in enumerate(rows):
            for c, col in enumerate(self._columns):
                val = row.get(col)
                text = sq.format_value(val)
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, val)
                if val is None:
                    item.setForeground(Qt.gray)
                self.data_table.setItem(r, c, item)

        self.data_table.resizeColumnsToContents()
        self._suppress_item_changed = False

        start = self._offset + 1 if rows else 0
        end = self._offset + len(rows)
        self.lbl_page_info.setText(
            i18n.t("sqlite.page_info").format(
                start=start, end=end, total=self._total_rows
            )
        )

        self.btn_prev.setEnabled(self._offset > 0)
        self.btn_next.setEnabled(self._offset + self._page_size < self._total_rows)

    def _on_page_size_changed(self, value: int):
        self._page_size = value
        self._offset = 0
        self._load_page()

    def _prev_page(self):
        if self._offset <= 0:
            return
        self._offset = max(0, self._offset - self._page_size)
        self._load_page()

    def _next_page(self):
        if self._offset + self._page_size >= self._total_rows:
            return
        self._offset += self._page_size
        self._load_page()

    def _on_cell_changed(self, item: QTableWidgetItem):
        if self._suppress_item_changed:
            return
        if not self._current_table or not self._schema:
            return

        pk_col = next((c for c in self._schema if c["pk"]), None)
        if pk_col is None:
            QMessageBox.information(
                self, i18n.t("sqlite.error"),
                i18n.t("sqlite.no_pk")
            )
            self._suppress_item_changed = True
            old = item.data(Qt.UserRole)
            item.setText(sq.format_value(old))
            self._suppress_item_changed = False
            return

        col_name = self._columns[item.column()]
        row_index = item.row()

        pk_index = next(
            (i for i, c in enumerate(self._schema) if c["pk"]),
            None,
        )
        if pk_index is None:
            return
        pk_item = self.data_table.item(row_index, pk_index)
        if pk_item is None:
            return
        pk_value = pk_item.data(Qt.UserRole)

        new_value = item.text()
        if new_value == "NULL":
            new_value = None

        ok, err = sq.update_cell(
            self._conn, self._current_table,
            pk_col["name"], pk_value,
            col_name, new_value,
        )
        if not ok:
            QMessageBox.warning(self, i18n.t("sqlite.error"), err or "")
            return

        item.setData(Qt.UserRole, new_value)

    def _run_sql(self):
        sql = self.sql_input.toPlainText().strip()
        if not sql:
            return
        if not self._conn:
            return

        result = sq.execute_query(self._conn, sql)

        if not result["ok"]:
            self.lbl_sql_status.setText(f"✕ {result['error']}")
            self.lbl_sql_status.setProperty("state", "err")
            self.lbl_sql_status.style().unpolish(self.lbl_sql_status)
            self.lbl_sql_status.style().polish(self.lbl_sql_status)
            self.sql_result.setRowCount(0)
            self.sql_result.setColumnCount(0)
            return

        if result["is_select"]:
            cols = result["columns"]
            rows = result["rows"]
            self.sql_result.clear()
            self.sql_result.setColumnCount(len(cols))
            self.sql_result.setHorizontalHeaderLabels(cols)
            self.sql_result.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    item = QTableWidgetItem(sq.format_value(val))
                    self.sql_result.setItem(r, c, item)
            self.sql_result.resizeColumnsToContents()

            self.lbl_sql_status.setText(
                i18n.t("sqlite.sql_rows").format(n=len(rows))
            )
        else:
            self.lbl_sql_status.setText(
                i18n.t("sqlite.sql_affected").format(n=result["rowcount"])
            )
            self._refresh_tables()

        self.lbl_sql_status.setProperty("state", "ok")
        self.lbl_sql_status.style().unpolish(self.lbl_sql_status)
        self.lbl_sql_status.style().polish(self.lbl_sql_status)

    def _refresh_tables(self):
        if not self._conn:
            return
        current = self._current_table
        self.tables_list.blockSignals(True)
        self.tables_list.clear()
        self._tables = sq.list_tables(self._conn)
        for t in self._tables:
            label = t["name"]
            if t["rows"] is not None:
                label += f"  ({t['rows']})"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, t["name"])
            self.tables_list.addItem(item)
        self.tables_list.blockSignals(False)

        if current:
            for i in range(self.tables_list.count()):
                if self.tables_list.item(i).data(Qt.UserRole) == current:
                    self.tables_list.setCurrentRow(i)
                    break

    def _export_csv(self):
        if not self._current_table:
            return
        start = self.settings.reports_dir or os.path.expanduser("~")
        default_name = f"{self._current_table}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.t("sqlite.export_csv"),
            os.path.join(start, default_name),
            "CSV (*.csv)"
        )
        if not path:
            return

        try:
            rows = sq.read_rows(
                self._conn, self._current_table,
                offset=0, limit=max(1_000_000, self._total_rows)
            )
            sq.export_csv(self._columns, [list(r.values()) for r in rows], path)
            QMessageBox.information(self, i18n.t("sqlite.export_csv"),
                                    i18n.t("sqlite.export_done"))
        except Exception as e:
            QMessageBox.warning(self, i18n.t("sqlite.error"), str(e))

    def retranslate(self):
        self.btn_browse.setText(i18n.t("sqlite.browse"))
        self.drop_zone.text_lbl.setText(i18n.t("sqlite.drop_hint"))
        self.btn_export.setText(i18n.t("sqlite.export_csv"))
        self.btn_run.setText(i18n.t("sqlite.run"))
        self.tabs.setTabText(0, i18n.t("sqlite.tab.data"))
        self.tabs.setTabText(1, i18n.t("sqlite.tab.schema"))
        self.tabs.setTabText(2, i18n.t("sqlite.tab.sql"))