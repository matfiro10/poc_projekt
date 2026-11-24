import numpy as np
from numpy.typing import NDArray
from src.constants import ImageArray


def nn_interp_for(
    img: ImageArray, x_scale: float, y_scale: float
) -> ImageArray:
    height, width = img.shape[:2]
    new_height: int = max(1, round(height * y_scale))
    new_width: int = max(1, round(width * x_scale))

    new_img: ImageArray = np.zeros(
        (new_height, new_width, *img.shape[2:]), dtype=img.dtype
    )

    for i in range(new_height):
        orig_y: int = min(int(i / y_scale), height - 1)
        for j in range(new_width):
            orig_x: int = min(int(j / x_scale), width - 1)
            new_img[i, j] = img[orig_y, orig_x]

    return new_img


def nn_interp_vectorized(
    img: ImageArray, x_scale: float, y_scale: float
) -> ImageArray:
    height, width = img.shape[:2]
    new_height: int = max(1, round(height * y_scale))
    new_width: int = max(1, round(width * x_scale))

    orig_y: NDArray[np.int_] = np.clip(
        (np.arange(new_height) / y_scale).astype(int), 0, height - 1
    )
    orig_x: NDArray[np.int_] = np.clip(
        (np.arange(new_width) / x_scale).astype(int), 0, width - 1
    )

    return img[orig_y[:, None], orig_x]