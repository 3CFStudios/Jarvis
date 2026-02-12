from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QResizeEvent
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from jarviso.branding import APP_NAME, BRAND_LINE, status_text, watermark_text
from jarviso.ui.about import AboutDialog


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Arya Build")
        self.resize(640, 400)

        self.status_label = QLabel("Status: IDLE")
        self.transcript_box = QTextEdit()
        self.transcript_box.setReadOnly(True)
        self.toggle_button = QPushButton("Start Listening")

        central = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.transcript_box)
        layout.addWidget(self.toggle_button)
        central.setLayout(layout)
        self.setCentralWidget(central)

        self._init_status_bar()
        self._init_menu()
        self._init_watermark()

    def _init_status_bar(self) -> None:
        status = QStatusBar(self)
        self.setStatusBar(status)
        self.brand_status_label = QLabel(status_text())
        status.addPermanentWidget(self.brand_status_label)

    def _init_menu(self) -> None:
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _init_watermark(self) -> None:
        self.watermark = QLabel(watermark_text(), self)
        self.watermark.setStyleSheet(
            "color: rgba(120, 120, 120, 90);"
            "font-size: 12px;"
            "font-weight: 600;"
            "padding: 2px;"
        )
        self.watermark.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.watermark.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._position_watermark()
        self.watermark.raise_()
        self.watermark.show()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._position_watermark()

    def _position_watermark(self) -> None:
        margin = 10
        hint = self.watermark.sizeHint()
        x = self.width() - hint.width() - margin
        y = self.height() - hint.height() - margin - self.statusBar().height()
        self.watermark.move(max(0, x), max(0, y))
        self.watermark.raise_()

    def show_about(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()


def create_app() -> QApplication:
    app = QApplication([])
    app.setApplicationDisplayName(BRAND_LINE)
    return app
