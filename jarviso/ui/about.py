from __future__ import annotations

from pathlib import Path
import webbrowser

from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QPushButton, QVBoxLayout

from jarviso.branding import ABOUT_TEXT, BRAND_LINE


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {BRAND_LINE}")
        self.setMinimumWidth(420)

        body = QLabel(ABOUT_TEXT)
        body.setWordWrap(True)

        open_license_button = QPushButton("Open LICENSE")
        open_license_button.clicked.connect(self._open_license)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(body)
        layout.addWidget(open_license_button)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def _open_license(self) -> None:
        root = Path(__file__).resolve().parents[2]
        license_path = root / "J.A.R.V.I.S-main" / "LICENSE"
        if not license_path.exists():
            return
        webbrowser.open(license_path.resolve().as_uri())
