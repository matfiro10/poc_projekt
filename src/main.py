import sys
from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
from constants import QT_ALLOCATION_LIMIT_MB
from PySide6.QtGui import QImageReader


def main() -> int:
    QImageReader.setAllocationLimit(QT_ALLOCATION_LIMIT_MB)

    app = QApplication(sys.argv)
    app.setApplicationName("ImageRescalerBenchmark")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())