from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from opencv_video import VideoCodec, VideoWriter, VideoWriterParameters

FRAME_HEIGHT = 48
FRAME_WIDTH = 64
# Each frame is filled with a distinct gray level so tests can tell frames apart after lossy encoding.
GRAY_STEP = 20

VideoFactory = Callable[[str, int], Path]


def gray_level(frame_id: int) -> int:
    return (frame_id * GRAY_STEP) % 256


@pytest.fixture
def make_video(tmp_path: Path) -> VideoFactory:
    def factory(name: str, frame_count: int) -> Path:
        path = tmp_path / name
        params = VideoWriterParameters(fps=10, codec=VideoCodec.MP4V)
        with VideoWriter(str(path), params) as writer:
            for frame_id in range(frame_count):
                writer.write(
                    np.full(
                        (FRAME_HEIGHT, FRAME_WIDTH, 3),
                        gray_level(frame_id),
                        dtype=np.uint8,
                    )
                )
        return path

    return factory
