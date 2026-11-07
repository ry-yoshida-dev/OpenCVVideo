from pathlib import Path

import cv2
import numpy as np
import pytest

from opencv_video import VideoCodec, VideoReader, VideoWriter, VideoWriterParameters


def test_codec_fourcc_matches_opencv() -> None:
    assert VideoCodec.MJPG.fourcc == cv2.VideoWriter.fourcc("M", "J", "P", "G")


@pytest.mark.parametrize(
    ("freq", "start_index"),
    [(0, 0), (-1, 0), (1, -1)],
)
def test_parameters_reject_invalid_values(freq: int, start_index: int) -> None:
    with pytest.raises(ValueError):
        _ = VideoWriterParameters(freq=freq, start_index=start_index)


def test_timestamp_counts_by_freq() -> None:
    params = VideoWriterParameters(is_timestamp_enabled=True, freq=5)
    assert [params.get_timestamp() for _ in range(3)] == [
        "Frame: 0",
        "Frame: 5",
        "Frame: 10",
    ]


def test_timestamp_is_empty_when_disabled() -> None:
    assert VideoWriterParameters().get_timestamp() == ""


def test_release_without_write_creates_no_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.mp4"
    VideoWriter(str(path), VideoWriterParameters()).release()
    assert not path.exists()


def test_write_creates_readable_video_in_new_directory(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "output.avi"
    params = VideoWriterParameters(fps=10, codec=VideoCodec.MJPG)
    frame = np.zeros((48, 64, 3), dtype=np.uint8)
    with VideoWriter(str(path), params) as writer:
        for _ in range(4):
            writer.write(frame)
    with VideoReader(str(path)) as reader:
        assert len(reader) == 4
        assert reader.extract_frame(0).shape == (48, 64, 3)


def test_timestamp_overlay_does_not_modify_input(tmp_path: Path) -> None:
    params = VideoWriterParameters(is_timestamp_enabled=True)
    frame = np.zeros((48, 160, 3), dtype=np.uint8)
    with VideoWriter(str(tmp_path / "output.mp4"), params) as writer:
        writer.write(frame)
    assert not frame.any()
