"""Shared array type aliases for OpenCV BGR video frames."""

from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray

BGR_CHANNELS: int = 3

# OpenCV BGR frame: (height, width, BGR_CHANNELS), uint8.
BGRFrame: TypeAlias = NDArray[np.uint8]


def as_bgr_frame(frame: np.ndarray) -> BGRFrame:
    """
    Validate and narrow a NumPy array to BGRFrame.

    Parameters
    ----------
    frame : np.ndarray
        Raw array returned by OpenCV read/write APIs.

    Returns
    -------
    BGRFrame
        Validated BGR frame with dtype uint8 and shape (H, W, 3).

    Raises
    ------
    TypeError
        If dtype is not uint8.
    ValueError
        If rank is not 3 or the channel dimension is not BGR_CHANNELS.
    """
    if frame.dtype != np.uint8:
        raise TypeError(f"Expected uint8 dtype, got {frame.dtype}")
    if frame.ndim != 3 or frame.shape[2] != BGR_CHANNELS:
        raise ValueError(
            f"Expected shape (H, W, {BGR_CHANNELS}), got {tuple(frame.shape)}"
        )
    return frame
