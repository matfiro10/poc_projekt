from typing import Final, TypeAlias
import numpy as np
from numpy.typing import NDArray

ImageArray: TypeAlias = NDArray[np.uint8 | np.uint16]

MAX_INPUT_MEGAPIXELS: Final[float] = 100.0
MAX_OUTPUT_MEGAPIXELS: Final[float] = 150.0
QT_ALLOCATION_LIMIT_MB: Final[int] = 512