from PySide6.QtWidgets import QFileDialog, QMessageBox, QWidget

from src.utils.qt_image_utils import get_supported_image_filter


def ask_open_image_path(parent: QWidget) -> str | None:
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        "Wybierz obraz",
        "",
        get_supported_image_filter(),
    )
    return file_path or None


def ask_save_image_path(
    parent: QWidget, default_filename: str = "output.png"
) -> str | None:
    save_path, _ = QFileDialog.getSaveFileName(
        parent,
        "Zapisz obraz",
        default_filename,
        get_supported_image_filter(),
    )
    return save_path or None


def show_warning(parent: QWidget, title: str, message: str) -> None:
    QMessageBox.warning(parent, title, message)


def show_info(parent: QWidget, title: str, message: str) -> None:
    QMessageBox.information(parent, title, message)


def format_resolution_banner(
    orig_w: int,
    orig_h: int,
    res_w: int,
    res_h: int,
    algorithm_label: str,
    scale_label: str,
) -> str:
    return (
        f"{orig_w}x{orig_h} px -> {res_w}x{res_h} px "
        f"({algorithm_label}, {scale_label})"
    )