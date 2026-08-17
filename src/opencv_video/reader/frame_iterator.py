from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Callable

import cv2

from ..types import BGRFrame
from .utils import cap_position_after_read

if TYPE_CHECKING:
    from .video_reader import VideoReader


class VideoFrameIterator(Iterator[BGRFrame]):
    """
    Per-iteration iterator that owns its own VideoCapture.
    Makes nested loops (e.g. for a in r: for b in r:) safe by not sharing cap state.
    """

    def __init__(
        self,
        reader: VideoReader,
        read_valid_frame: Callable[
            [cv2.VideoCapture, int, int | None],
            tuple[bool, BGRFrame | None],
        ],
    ) -> None:
        self.reader = reader
        self._read_valid_frame = read_valid_frame
        self._cap = cv2.VideoCapture(reader.video_path)
        if not self._cap.isOpened():
            raise ValueError(
                f"Error: Failed to open the video file: {reader.video_path}"
            )
        self._next_frame_id = reader.iter_start_frame
        self._last_cap_position: int | None = None
        self._last_yielded_frame_id: int | None = None

    def __next__(self) -> BGRFrame:
        if self._next_frame_id > self.reader.total_frame:
            raise StopIteration
        cap = self._cap
        if cap is None:
            raise StopIteration
        ret, frame = self._read_valid_frame(
            cap,
            self._next_frame_id,
            self._last_cap_position,
        )
        if frame is not None and ret:
            self._last_cap_position = cap_position_after_read(
                self._next_frame_id, self.reader.freq
            )
            self._last_yielded_frame_id = self._next_frame_id
        self._next_frame_id += self.reader.freq
        if frame is None or not ret:
            raise StopIteration
        return frame

    def skip(self) -> None:
        """
        Advance past the current frame without decoding it.

        Leaves `_last_cap_position` stale, so the next real `__next__` call
        seeks before reading rather than trusting `cap` to already be
        positioned where this skip left the logical count.

        Raises
        ------
        StopIteration: If the current position is past the last frame.
        """
        if self._next_frame_id > self.reader.total_frame:
            raise StopIteration
        self._next_frame_id += self.reader.freq

    @property
    def frame_id(self) -> int:
        """Last yielded frame id (e.g. for use by the owning VideoReader)."""
        if self._last_yielded_frame_id is not None:
            return self._last_yielded_frame_id
        return self.reader.iter_start_frame - 1

    @property
    def is_reach_end_of_video(self) -> bool:
        return self._next_frame_id > self.reader.total_frame

    def release(self) -> None:
        if hasattr(self, "_cap") and self._cap is not None:
            self._cap.release()
            self._cap = None

    def __del__(self) -> None:
        self.release()
