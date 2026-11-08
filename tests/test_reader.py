from pathlib import Path

import numpy as np
import pytest

from opencv_video import BGRFrame, VideoReader

from .conftest import FRAME_HEIGHT, FRAME_WIDTH, VideoFactory, gray_level

# Tolerance for the mean gray level of a frame after lossy encoding.
GRAY_TOLERANCE = 6


def assert_frame_id(frame: BGRFrame, frame_id: int) -> None:
    assert (
        abs(float(np.mean(frame, dtype=np.float64)) - gray_level(frame_id))
        <= GRAY_TOLERANCE
    )


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        _ = VideoReader(str(tmp_path / "missing.mp4"))


def test_len_and_full_iteration(make_video: VideoFactory) -> None:
    path = make_video("video.mp4", 10)
    with VideoReader(str(path)) as reader:
        assert len(reader) == 10
        frames = list(reader)
    assert len(frames) == 10
    assert frames[0].shape == (FRAME_HEIGHT, FRAME_WIDTH, 3)
    for frame_id, frame in enumerate(frames):
        assert_frame_id(frame, frame_id)


@pytest.mark.parametrize(
    ("iter_start_frame", "freq", "expected_ids"),
    [
        (0, 2, [0, 2, 4, 6, 8]),
        (5, 1, [5, 6, 7, 8, 9]),
        (1, 3, [1, 4, 7]),
        # Above freq_th, the reader seeks instead of reading sequentially.
        (0, 11, [0]),
    ],
)
def test_iteration_respects_start_and_freq(
    make_video: VideoFactory,
    iter_start_frame: int,
    freq: int,
    expected_ids: list[int],
) -> None:
    path = make_video("video.mp4", 10)
    with VideoReader(str(path), iter_start_frame=iter_start_frame, freq=freq) as reader:
        frames = list(reader)
    assert len(frames) == len(expected_ids)
    for frame_id, frame in zip(expected_ids, frames, strict=True):
        assert_frame_id(frame, frame_id)


def test_iteration_with_queue(make_video: VideoFactory) -> None:
    path = make_video("video.mp4", 10)
    with VideoReader(str(path), freq=2, use_queue=True) as reader:
        frames = list(reader)
        assert reader.frame_id == 8
    assert len(frames) == 5
    for frame_id, frame in zip([0, 2, 4, 6, 8], frames, strict=True):
        assert_frame_id(frame, frame_id)


def test_nested_iteration_is_independent(make_video: VideoFactory) -> None:
    path = make_video("video.mp4", 3)
    with VideoReader(str(path)) as reader:
        outer_count = 0
        for _ in reader:
            outer_count += 1
            assert len(list(reader)) == 3
    # The inner loop replaces the reader's current iterator, but the outer loop keeps its own.
    assert outer_count == 3


def test_extract_frame_by_seek_and_by_read(make_video: VideoFactory) -> None:
    path = make_video("video.mp4", 10)
    with VideoReader(str(path)) as reader:
        assert_frame_id(reader.extract_frame(7), 7)
        # Backwards forces a seek.
        assert_frame_id(reader.extract_frame(2), 2)
        # A short step forwards is served by sequential reads.
        assert_frame_id(reader.extract_frame(4), 4)


def test_extract_frame_out_of_range_raises(make_video: VideoFactory) -> None:
    path = make_video("video.mp4", 3)
    with VideoReader(str(path)) as reader, pytest.raises(ValueError):
        _ = reader.extract_frame(50)


def test_skip_advances_without_returning_frame(make_video: VideoFactory) -> None:
    path = make_video("video.mp4", 5)
    with VideoReader(str(path)) as reader:
        iterator = iter(reader)
        assert_frame_id(next(iterator), 0)
        reader.skip()
        assert_frame_id(next(iterator), 2)
        assert reader.frame_id == 2
