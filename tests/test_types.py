import numpy as np
import pytest

from opencv_video import as_bgr_frame


def test_as_bgr_frame_accepts_valid_array() -> None:
    frame = np.zeros((48, 64, 3), dtype=np.uint8)
    assert as_bgr_frame(frame).shape == (48, 64, 3)


def test_as_bgr_frame_rejects_grayscale() -> None:
    with pytest.raises(ValueError):
        _ = as_bgr_frame(np.zeros((48, 64), dtype=np.uint8))


def test_as_bgr_frame_rejects_non_uint8() -> None:
    with pytest.raises(TypeError):
        _ = as_bgr_frame(np.zeros((48, 64, 3), dtype=np.float32))
