from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.setWindowTitle("Image Rescaling Benchmark Tool")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self._main_layout = QVBoxLayout(central_widget)

        self._info_label = QLabel("Gotowy do wczytania obrazu.")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._test_button = QPushButton("Testuj działanie")

        self._main_layout.addWidget(self._info_label)
        self._main_layout.addWidget(self._test_button)

    def _connect_signals(self):
        self._test_button.clicked.connect(self._on_test_clicked)

    def _on_test_clicked(self):
        self._info_label.setText("Okno działa poprawnie!")