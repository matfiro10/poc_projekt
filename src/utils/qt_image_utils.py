from pathlib import Path
from sys import path
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import QSize
from PySide6.QtGui import QImage, QImageReader, QPixmap
from openpyxl import reader

from constants import MAX_INPUT_MEGAPIXELS, QT_ALLOCATION_LIMIT_MB, ImageArray

class ImageIOError(Exception):
    pass


def get_supported_image_filter() -> str:
    formats: list[str] = [
        bytes(fmt).decode("ascii").lower()
        for fmt in QImageReader.supportedImageFormats()
    ]
    patterns: str = " ".join(f"*.{ext}" for ext in formats)
    return f"Obrazy ({patterns});;Wszystkie pliki (*)"


def load_image_as_numpy(
    file_path: str | Path,
    max_megapixels: float = MAX_INPUT_MEGAPIXELS,
    allocation_limit_mb: int = QT_ALLOCATION_LIMIT_MB,
) -> ImageArray:
    if not file_path:
        raise ImageIOError("Nie podano ścieżki do pliku.")

    path = Path(file_path)
    if not path.exists() or not path.is_file():
        raise ImageIOError(f"Plik nie istnieje lub nie jest zwykłym plikiem: {path}")

    QImageReader.setAllocationLimit(allocation_limit_mb)

    reader = QImageReader(str(path))
    reader.setAutoTransform(True)

    if not reader.canRead():
        raise ImageIOError(
            f"Nieobsługiwany lub uszkodzony format pliku '{path.name}': "
            f"{reader.errorString()}"
        )

    header_size: QSize = reader.size()
    if header_size.isValid():
        width_hdr: int = header_size.width()
        height_hdr: int = header_size.height()
    else:
        width_hdr: int = 0
        height_hdr: int = 0

    if width_hdr <= 0 or height_hdr <= 0:
        raise ImageIOError(
            f"Nieprawidłowe wymiary obrazu: {width_hdr}x{height_hdr}"
        )

    megapixels: float = (width_hdr * height_hdr) / 1_000_000.0
    if megapixels > max_megapixels:
        raise ImageIOError(
            f"Obraz jest zbyt duży ({megapixels:.1f} MP). "
            f"Maksymalny dozwolony rozmiar to {max_megapixels:.0f} MP."
        )

    qimg: QImage = reader.read()
    if qimg.isNull():
        raise ImageIOError(
            f"Błąd dekodowania obrazu ({reader.error().name}):"
            f" {reader.errorString()}"
        )

    converted: QImage = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
    if converted.isNull():
        raise ImageIOError("Nie udało się przekonwertować obrazu do formatu RGBA.")

    width: int = converted.width()
    height: int = converted.height()
    ptr: memoryview = converted.constBits()

    arr: ImageArray = np.frombuffer(ptr, dtype=np.uint8).reshape(
        (height, width, 4)
    )
    return arr.copy()


def numpy_to_qpixmap(arr: ImageArray) -> QPixmap:
    if arr.size == 0 or arr.ndim not in (2, 3):
        raise ImageIOError(
            f"Nieprawidłowy kształt macierzy obrazu: {arr.shape}. "
            "Oczekiwano (H, W) lub (H, W, C)."
        )

    if arr.dtype != np.uint8:
        arr_uint8: ImageArray = np.clip(arr, 0, 255).astype(np.uint8)
    else:
        arr_uint8 = arr

    arr_contig: ImageArray = np.ascontiguousarray(arr_uint8)
    height: int = arr_contig.shape[0]
    width: int = arr_contig.shape[1]
    channels: int = arr_contig.shape[2] if arr_contig.ndim == 3 else 1

    if channels == 4:
        img_format = QImage.Format.Format_RGBA8888
    elif channels == 3:
        img_format = QImage.Format.Format_RGB888
    elif channels == 1:
        img_format = QImage.Format.Format_Grayscale8
    else:
        raise ImageIOError(
            f"Nieobsługiwana liczba kanałów: {channels} (dozwolone: 1, 3, 4)."
        )

    bytes_per_line: int = arr_contig.strides[0]
    qimg: QImage = QImage(
        arr_contig.data, width, height, bytes_per_line, img_format
    ).copy()

    if qimg.isNull():
        raise ImageIOError("Nie udało się utworzyć obiektu QImage z tablicy NumPy.")

    return QPixmap.fromImage(qimg)


def save_numpy_image(arr: ImageArray, file_path: str | Path) -> None:
    """Zapisuje tablicę obrazu NumPy na dysk za pomocą QPixmap/QImage."""
    if not file_path:
        raise ImageIOError("Nie podano docelowej ścieżki zapisu pliku.")

    path = Path(file_path)
    if not path.suffix:
        raise ImageIOError(
            f"Nazwa pliku '{path.name}' musi zawierać rozszerzenie (np. .png, .jpg)."
        )

    # Upewnij się, że katalog docelowy istnieje
    if path.parent and not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    pixmap: QPixmap = numpy_to_qpixmap(arr)
    if not pixmap.save(str(path)):
        raise ImageIOError(
            f"Nie udało się zapisać obrazu do pliku '{path}'."
        )