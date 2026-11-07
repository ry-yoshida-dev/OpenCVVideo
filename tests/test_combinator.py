from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from opencv_video import (
    StopCriteria,
    VideoCombinator,
    VideoCombinatorParameters,
    VideoReader,
    VideoWriterParameters,
)

from .conftest import FRAME_HEIGHT, FRAME_WIDTH, VideoFactory


def combine(
    paths: list[Path],
    output_path: Path,
    params: VideoCombinatorParameters,
) -> int:
    VideoCombinator(
        video_paths=[str(path) for path in paths],
        output_path=str(output_path),
        combinator_params=params,
        writer_params=VideoWriterParameters(fps=10),
    ).combine_videos()
    with VideoReader(str(output_path)) as reader:
        return len(reader)


@pytest.mark.parametrize(
    ("stop_criteria", "expected_frames"),
    [
        (StopCriteria.SHORT_VIDEO_END, 3),
        (StopCriteria.LONGEST_VIDEO_END, 5),
    ],
)
def test_stop_criteria(
    make_video: VideoFactory,
    tmp_path: Path,
    stop_criteria: StopCriteria,
    expected_frames: int,
) -> None:
    paths = [make_video("long.mp4", 5), make_video("short.mp4", 3)]
    params = VideoCombinatorParameters(
        rows=1,
        image_shape=(FRAME_HEIGHT, FRAME_WIDTH),
        stop_criteria=stop_criteria,
    )
    assert combine(paths, tmp_path / "grid.mp4", params) == expected_frames


def test_end_frame_limits_output(make_video: VideoFactory, tmp_path: Path) -> None:
    paths = [make_video("a.mp4", 5)]
    params = VideoCombinatorParameters(
        rows=1, image_shape=(FRAME_HEIGHT, FRAME_WIDTH), end_frame=2
    )
    assert combine(paths, tmp_path / "grid.mp4", params) == 2


def test_grid_layout(make_video: VideoFactory, tmp_path: Path) -> None:
    paths = [make_video(f"{index}.mp4", 2) for index in range(3)]
    output_path = tmp_path / "grid.mp4"
    params = VideoCombinatorParameters(rows=2, image_shape=(FRAME_HEIGHT, FRAME_WIDTH))
    _ = combine(paths, output_path, params)
    with VideoReader(str(output_path)) as reader:
        # Three inputs in two rows need two columns.
        assert reader.extract_frame(0).shape == (FRAME_HEIGHT * 2, FRAME_WIDTH * 2, 3)


def test_letterbox_resize_keeps_aspect_ratio() -> None:
    image = np.full((10, 40, 3), 255, dtype=np.uint8)
    resized, ratio = VideoCombinator.letterbox_resize(image, (40, 40), color=(0, 0, 0))
    assert resized.shape == (40, 40, 3)
    assert ratio == 1.0
    # The 40x10 image is centered vertically with padding above and below.
    assert not resized[:15].any()
    assert resized[15:25].all()
    assert not resized[25:].any()


def test_empty_video_paths_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        _ = VideoCombinator(
            video_paths=[],
            output_path=str(tmp_path / "grid.mp4"),
            combinator_params=VideoCombinatorParameters(),
            writer_params=VideoWriterParameters(),
        )


@pytest.mark.parametrize(
    "create",
    [
        lambda: VideoCombinatorParameters(rows=0),
        lambda: VideoCombinatorParameters(freq=0),
        lambda: VideoCombinatorParameters(iter_start_frame=-1),
        lambda: VideoCombinatorParameters(end_frame=-2),
        lambda: VideoCombinatorParameters(image_shape=(0, 10)),
    ],
)
def test_parameters_reject_invalid_values(
    create: Callable[[], VideoCombinatorParameters],
) -> None:
    with pytest.raises(ValueError):
        _ = create()
