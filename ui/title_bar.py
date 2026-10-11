from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QToolButton, QSizePolicy
)


class TitleBar(QWidget):

    minimize_clicked = Signal()
    maximize_clicked = Signal()
    close_clicked = Signal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(38)

        self._drag_pos = None
        self._is_maximized = False

        self._build(title)

    def _build(self, title):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 6, 0)
        layout.setSpacing(8)

        logo = QLabel("SF")
        logo.setObjectName("TitleLogo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(22, 22)

        name = QLabel(title)
        name.setObjectName("TitleText")

        layout.addWidget(logo)
        layout.addWidget(name)
        layout.addStretch(1)

        self.btn_min = self._make_btn("–", "Свернуть", "WinBtnMin")
        self.btn_max = self._make_btn("□", "Развернуть", "WinBtnMax")
        self.btn_close = self._make_btn("✕", "Закрыть", "WinBtnClose")

        self.btn_min.clicked.connect(self.minimize_clicked.emit)
        self.btn_max.clicked.connect(self.maximize_clicked.emit)
        self.btn_close.clicked.connect(self.close_clicked.emit)

        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addWidget(self.btn_close)

    def _make_btn(self, text: str, tip: str, obj_name: str) -> QToolButton:
        btn = QToolButton()
        btn.setObjectName(obj_name)
        btn.setText(text)
        btn.setToolTip(tip)
        btn.setFixedSize(36, 28)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setAutoRaise(True)
        return btn

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is None:
            return
        window = self.window()
        if window.isMaximized():
            return
        delta = event.globalPosition().toPoint() - self._drag_pos
        window.move(window.pos() + delta)
        self._drag_pos = event.globalPosition().toPoint()
        event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.maximize_clicked.emit()