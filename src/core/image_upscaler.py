from enum import IntEnum, StrEnum
from pathlib import Path
from typing import assert_never
from unittest import case
import numpy as np
from numpy.typing import NDArray
from PySide6.QtGui import QPixmap
from algorithms.nn_interp import nn_interp_vectorized
from algorithms.bicubic_interp import bicubic_interp
from utils.qt_image_utils import (
    ImageIOError,
    load_image_as_numpy,
    numpy_to_qpixmap,
    save_numpy_image,
)
from constants import MAX_OUTPUT_MEGAPIXELS, ImageArray


class ScaleFactor(IntEnum):
    X1 = 1
    X2 = 2
    X3 = 3
    X4 = 4

    @property
    def label(self) -> str:
        return f"{self.value}x"


class InterpolationAlgorithm(StrEnum):
    NEAREST = "nearest"
    BICUBIC = "bicubic"

    @property
    def label(self) -> str:
        match self:
            case InterpolationAlgorithm.NEAREST:
                return "Nearest Neighbor"
            case InterpolationAlgorithm.BICUBIC:
                return "Bicubic"
            case _ as unreachable:
                assert_never(unreachable)


class ImageUpscaler:
    def __init__(
        self,
        default_scale: ScaleFactor = ScaleFactor.X2,
        default_algorithm: InterpolationAlgorithm = InterpolationAlgorithm.NEAREST,
        max_output_megapixels: float = MAX_OUTPUT_MEGAPIXELS,
    ) -> None:
        self._source_path: Path | None = None
        self._original_image: ImageArray | None = None
        self._processed_image: ImageArray | None = None
        self._scale: ScaleFactor = default_scale
        self._algorithm: InterpolationAlgorithm = default_algorithm
        self._max_output_megapixels: float = max_output_megapixels

    @property
    def source_path(self) -> Path | None:
        return self._source_path

    @property
    def original_image(self) -> ImageArray | None:
        return self._original_image

    @property
    def processed_image(self) -> ImageArray | None:
        return self._processed_image

    @property
    def has_image(self) -> bool:
        return self._original_image is not None

    @property
    def scale(self) -> ScaleFactor:
        return self._scale


    @scale.setter
    def scale(self, value: ScaleFactor | int) -> None:
        try:
            new_scale = ScaleFactor(value)
        except ValueError as exc:
            allowed = [s.value for s in ScaleFactor]
            raise ValueError(
                f"Nieobsługiwana skala: {value}. Dozwolone wartości: {allowed}"
            ) from exc

        if new_scale != self._scale:
            self._scale = new_scale
            self._processed_image = None


    @property
    def algorithm(self) -> InterpolationAlgorithm:
        return self._algorithm


    @algorithm.setter
    def algorithm(self, value: InterpolationAlgorithm | str) -> None:
        try:
            new_algorithm = InterpolationAlgorithm(value)
        except ValueError as exc:
            allowed = [a.value for a in InterpolationAlgorithm]
            raise ValueError(
                f"Nieobsługiwany algorytm: {value}. Dozwolone wartości: {allowed}"
            ) from exc

        if new_algorithm != self._algorithm:
            self._algorithm = new_algorithm
            self._processed_image = None


    def load_image(self, file_path: str | Path) -> None:
        loaded: ImageArray = load_image_as_numpy(file_path)

        self._source_path = Path(file_path)
        self._original_image = loaded
        self._processed_image = None


    def process(self) -> ImageArray:
        if self._original_image is None:
            raise ImageIOError("Brak wczytanego obrazu do przetworzenia.")

        factor: int = int(self._scale)
        if factor == 1:
            self._processed_image = self._original_image.copy()
            return self._processed_image

        height: int
        width: int
        height, width = self._original_image.shape[:2]

        new_height: int = max(1, height * factor)
        new_width: int = max(1, width * factor)

        out_megapixels: float = (new_height * new_width) / 1_000_000.0
        if out_megapixels > self._max_output_megapixels:
            raise ImageIOError(
                f"Obraz wynikowy ({new_width}x{new_height} px, {out_megapixels:.1f} MP) "
                f"przekracza bezpieczny limit {self._max_output_megapixels:.0f} MP."
        )

        match self._algorithm:
            case InterpolationAlgorithm.NEAREST:
                self._processed_image = nn_interp_vectorized(
                    self._original_image, factor, factor
                )
       
            case InterpolationAlgorithm.BICUBIC:
                self._processed_image = bicubic_interp(
                    self._original_image, factor, factor
                )
            case _ as unreachable:
                assert_never(unreachable)

        return self._processed_image


    def get_original_pixmap(self) -> QPixmap:
        if self._original_image is None:
            raise ImageIOError("Nie wczytano jeszcze żadnego obrazu.")
        return numpy_to_qpixmap(self._original_image)


    def get_result_pixmap(self, auto_process: bool = True) -> QPixmap:
        if self._processed_image is None:
            if not auto_process:
                raise ImageIOError("Obraz nie został jeszcze przeskalowany.")
            self.process()

        assert self._processed_image is not None
        return numpy_to_qpixmap(self._processed_image)


    def save_result(self, file_path: str | Path, auto_process: bool = True) -> None:
        """Zapisuje przeskalowany obraz do pliku na dysku."""
        if self._processed_image is None:
            if not auto_process:
                raise ImageIOError("Obraz nie został jeszcze przeskalowany.")
            self.process()
        assert self._processed_image is not None
        save_numpy_image(self._processed_image, file_path)
