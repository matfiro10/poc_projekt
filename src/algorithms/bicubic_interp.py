import numpy as np
from numpy.typing import NDArray
from src.constants import ImageArray


def _cubic_weights(d: NDArray[np.float64], a: float = -0.75) -> NDArray[np.float64]:
    """Oblicza wagi jądra kubicznego Keys'a dla zadanych odległości d."""
    abs_d = np.abs(d)
    abs_d2 = abs_d ** 2
    abs_d3 = abs_d ** 3

    weights = np.zeros_like(abs_d, dtype=np.float64)

    mask_near = abs_d <= 1.0
    weights[mask_near] = (
            (a + 2.0) * abs_d3[mask_near]
            - (a + 3.0) * abs_d2[mask_near]
            + 1.0
    )

    mask_far = (abs_d > 1.0) & (abs_d < 2.0)
    weights[mask_far] = (
            a * abs_d3[mask_far]
            - 5.0 * a * abs_d2[mask_far]
            + 8.0 * a * abs_d[mask_far]
            - 4.0 * a
    )

    return weights


def _resize_axis(
        img: NDArray[np.float64], new_size: int, scale: float, axis: int, a: float = -0.75
) -> NDArray[np.float64]:
    """Interpoluje obraz kubicznie wzdłuż jednej osi (axis=1: szerokość, axis=0: wysokość)."""
    old_size: int = img.shape[axis]

    coords: NDArray[np.float64] = np.arange(new_size, dtype=np.float64) / scale
    base_idx: NDArray[np.int_] = np.floor(coords).astype(np.int_)
    frac: NDArray[np.float64] = coords - base_idx

    offsets = (-1, 0, 1, 2)
    neighbor_indices = [
        np.clip(base_idx + offset, 0, old_size - 1) for offset in offsets
    ]

    weights = [_cubic_weights(frac - offset, a=a) for offset in offsets]

    if axis == 1:
        weights = [w[None, :, None] for w in weights]
        slices = [img[:, idx, :] for idx in neighbor_indices]
    else:
        weights = [w[:, None, None] for w in weights]
        slices = [img[idx, :, :] for idx in neighbor_indices]

    result: NDArray[np.float64] = (
            weights[0] * slices[0]
            + weights[1] * slices[1]
            + weights[2] * slices[2]
            + weights[3] * slices[3]
    )
    return result


def bicubic_interp(
        img: ImageArray, x_scale: float, y_scale: float, a: float = -0.75
) -> ImageArray:
    """Powiększa obraz za pomocą separowalnej interpolacji dwusześciennej (Bicubic)."""
    height, width = img.shape[:2]
    new_height: int = int(height * y_scale)
    new_width: int = int(width * x_scale)

    img_float: NDArray[np.float64] = img.astype(np.float64)

    horiz_resized = _resize_axis(img_float, new_width, x_scale, axis=1, a=a)
    vert_resized = _resize_axis(horiz_resized, new_height, y_scale, axis=0, a=a)

    info = np.iinfo(img.dtype)
    clipped = np.clip(np.rint(vert_resized), info.min, info.max)

    return clipped.astype(img.dtype)