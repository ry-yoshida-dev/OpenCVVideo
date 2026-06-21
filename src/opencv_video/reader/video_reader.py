from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from types import TracebackType
from typing import Callable

import cv2

from ..types import BGRFrame, as_bgr_frame
from .buffer import FrameBuffer
from .frame_iterator import VideoFrameIterator
from .utils import EXTRACT_SEEK_THRESHOLD, cap_position_after_read


@dataclass
class VideoReader:
    """
    VideoReader is the reader for the video.

    Parameters
    ----------
    video_path : str
        Path to the video file.
    iter_start_frame : int, optional
        The frame number to start reading from (default is 0).
    freq : int, optional
        The step size for frame iteration (default is 1).
    freq_th : int, optional
        Threshold for freq; when freq > freq_th, seek-based read is used (default is 10).
    use_queue : bool, optional
        If True, prefetch frames in a background thread (default is False).
    queue_size : int, optional
        Max size of the prefetch queue when use_queue is True (default is 2).

    Attributes
    ----------
    video_path: str
        The path to the video file.
    iter_start_frame: int
        The frame number to start reading from.
    freq: int
        The step size for frame iteration.
    cap: cv2.VideoCapture
        The video capture object.
    _read_next_frame: Callable[[], tuple[bool, BGRFrame | None]]
        The function to read the next frame.
    total_frame: int
        The total number of frames in the video.
    _next_frame_id: int
        The current frame number.
    use_queue: bool
        If True, frames are prefetched in a background thread and consumed from a queue.
    queue_size: int
        Max number of frames to prefetch when use_queue is True.
    freq_th: int
        Threshold for freq; above this value, seek-based read is used instead of loop.
    _next_impl: Callable[[], BGRFrame]
        Bound implementation for __next__ (either _next_from_queue or _next_from_cap).
    """

    video_path: str
    iter_start_frame: int = 0
    freq: int = 1
    freq_th: int = 10
    use_queue: bool = False
    queue_size: int = 2

    cap: cv2.VideoCapture = field(init=False)
    _frame_reader_function: Callable[[], tuple[bool, BGRFrame | None]] = field(init=False)
    total_frame: int = field(init=False)
    _next_frame_id: int = field(init=False)
    _buffer: FrameBuffer | None = field(init=False, default=None)
    _current_frame_id_queue: int | None = field(init=False, default=None)
    _current_iterator: VideoFrameIterator | None = field(init=False, default=None)
    _last_cap_position: int | None = field(init=False, default=None)
    _last_extract_position: int | None = field(init=False, default=None)
    _next_impl: Callable[[], BGRFrame] = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the VideoReader (open video, set reader function, etc.).

        Raises
        ------
        FileNotFoundError
            If the video file does not exist.
        ValueError
            If the video file cannot be opened.
        """
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Error: The video file does not exist: {self.video_path}")

        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Error: Failed to open the video file: {self.video_path}")

        self._frame_reader_function = self.define_frame_reader_function()
        self.total_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._next_frame_id = self.iter_start_frame
        self._next_impl = self._next_from_cap
        self._current_iterator = None

    def define_frame_reader_function(self) -> Callable[[], tuple[bool, BGRFrame | None]]:
        """
        Define the function to read the next frame.

        Returns a bound callable that reads the next valid frame for self.cap at self._next_frame_id.
        The actual strategy (seek per frame vs loop read) is inside _read_next_valid_frame.

        Returns
        -------
        Callable[[], tuple[bool, BGRFrame | None]]
            The function to read the next frame.
        """
        return lambda: self._read_next_valid_frame(
            self.cap, self._next_frame_id, current_cap_position=self._last_cap_position
        )

    def _read_next_valid_frame(
        self,
        cap: cv2.VideoCapture,
        next_frame_id: int,
        *,
        current_cap_position: int | None = None,
    ) -> tuple[bool, BGRFrame | None]:
        """
        Read the next valid frame at the given position (single responsibility: one logical frame).

        When freq > freq_th: seek to next_frame_id and read once (efficient for large step).
        When freq <= freq_th: seek only if cap is not already at the right position, then read
        freq times (avoids one seek per frame for sequential iteration).

        Parameters
        ----------
        cap : cv2.VideoCapture
            The video capture to read from.
        next_frame_id : int
            The frame index of the logical "next" frame to return.
        current_cap_position : int | None
            Current frame index of cap (next frame to be read). If given and correct, seek is skipped.

        Returns
        -------
        tuple[bool, BGRFrame | None]
            (success, frame). Frame is None on failure.
        """
        if self.freq > self.freq_th:
            cap.set(cv2.CAP_PROP_POS_FRAMES, next_frame_id)
            return self._read_bgr_frame(cap)
        start_pos = cap_position_after_read(next_frame_id, self.freq) - self.freq
        if current_cap_position != start_pos:
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_pos)
        ret, frame = False, None
        for _ in range(self.freq):
            ret, frame = self._read_bgr_frame(cap)
            if not ret:
                return False, None
        return ret, frame

    @staticmethod
    def _read_bgr_frame(cap: cv2.VideoCapture) -> tuple[bool, BGRFrame | None]:
        """
        Read one frame from capture and narrow it to BGRFrame.

        Parameters
        ----------
        cap : cv2.VideoCapture
            OpenCV capture handle.

        Returns
        -------
        tuple[bool, BGRFrame | None]
            Success flag and validated BGR frame, or None on read failure.
        """
        ret, frame = cap.read()
        if not ret:
            return False, None
        return True, as_bgr_frame(frame)

    def _next_from_queue(self) -> BGRFrame:
        """Get next frame from buffer. Used when use_queue is True."""
        buffer = self._buffer
        if buffer is None:
            raise StopIteration
        frame_id, frame = buffer.__next__()
        self._current_frame_id_queue = frame_id
        return frame

    def _next_from_cap(self) -> BGRFrame:
        """Get next frame from VideoCapture. Used when use_queue is False."""
        if self._next_frame_id > self.total_frame:
            raise StopIteration
        ret, frame = self._frame_reader_function()
        if frame is not None and ret:
            self._last_cap_position = cap_position_after_read(
                self._next_frame_id, self.freq
            )
        self._next_frame_id += self.freq
        # Prefer ret over total_frame; some files have incorrect frame count metadata.
        if frame is None or not ret:
            raise StopIteration
        return frame

    def _iterate_frames(
        self,
        cap: cv2.VideoCapture | None = None,
    ) -> Iterator[tuple[int, BGRFrame]]:
        """
        Yield (frame_id, frame). Uses cap if given.
        Delegates "next valid frame" to _read_next_valid_frame; no branching on freq/freq_th here.

        Parameters
        ----------
        cap : cv2.VideoCapture | None
            The video capture object. If None, a new video capture object is created.

        Returns
        -------
        Iterator[tuple[int, BGRFrame]]
            An iterator yielding (frame_id, frame).
        """
        own_cap = cap is None
        if cap is None:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                return
        try:
            total = self.total_frame if not own_cap else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            next_id = self.iter_start_frame
            cap_pos: int | None = None
            # When total <= 0 (e.g. live stream), rely only on ret; otherwise use total as upper bound.
            while total <= 0 or next_id <= total:
                ret, frame = self._read_next_valid_frame(
                    cap, next_id, current_cap_position=cap_pos
                )
                if not ret or frame is None:
                    return
                yield (next_id, frame)
                cap_pos = cap_position_after_read(next_id, self.freq)
                next_id += self.freq
        finally:
            if own_cap:
                cap.release()

    def _create_frame_iterator_factory(
        self,
    ) -> Callable[[], Iterator[tuple[int, BGRFrame]]]:
        """
        Create a frame iterator factory.

        Returns
        -------
        Callable[[], Iterator[tuple[int, BGRFrame]]]: A function that returns an iterator yielding (frame_id, frame).
        """
        return lambda: self._iterate_frames(self.cap)

    def _stop_buffer(self) -> None:
        """Stop the frame buffer if used. No-op otherwise."""
        if self._buffer is not None:
            self._buffer.release()
            self._buffer = None

    @property
    def is_reach_end_of_video(self) -> bool:
        if self._current_iterator is not None and not self.use_queue:
            return self._current_iterator.is_reach_end_of_video
        return self._next_frame_id > self.total_frame

    def extract_frame(
        self,
        frame_number: int,
    ) -> BGRFrame:
        """
        Extracts and saves a specific frame from the video.

        When use_queue is True, uses a temporary VideoCapture so it is safe to call during iteration.

        Parameters
        ----------
        frame_number : int
            The frame number to extract.

        Returns
        -------
        BGRFrame
            The extracted frame.

        Raises
        ------
        ValueError
            If the frame could not be read.
        """
        if self.use_queue and self._buffer is not None and self._buffer.is_running():
            cap = cv2.VideoCapture(self.video_path)
            try:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                ret, frame = self._read_bgr_frame(cap)
                if not ret or frame is None:
                    raise ValueError(f"Failed to read frame {frame_number} from {self.video_path}")
                return frame
            finally:
                cap.release()
        # When target is near current cap position, advance by read() to avoid slow seek.
        if self._last_extract_position is not None and frame_number >= self._last_extract_position:
            delta = frame_number - self._last_extract_position
            if delta <= EXTRACT_SEEK_THRESHOLD:
                if delta > 0:
                    frame: BGRFrame | None = None
                    for _ in range(delta):
                        ret, frame = self._read_bgr_frame(self.cap)
                        if not ret or frame is None:
                            raise ValueError(
                                f"Failed to read frame {frame_number} from {self.video_path}"
                            )
                    if frame is None:
                        raise ValueError(
                            f"Failed to read frame {frame_number} from {self.video_path}"
                        )
                    self._last_extract_position = frame_number
                    return frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self._read_bgr_frame(self.cap)
        if not ret or frame is None:
            raise ValueError(f"Failed to read frame {frame_number} from {self.video_path}")
        self._last_extract_position = frame_number
        return frame

    def __iter__(self) -> Iterator[BGRFrame]:
        """
        Resets the video position to the specified iter_start_frame and returns an iterator over frames.

        When use_queue is True, returns self (buffer feeds frames). When use_queue is False,
        returns a dedicated VideoFrameIterator so nested loops over the same reader are safe.

        Returns
        -------
        Iterator[BGRFrame]
            Iterator yielding frames sequentially from the iter_start_frame.
        """
        self._current_frame_id_queue = None
        if self.use_queue:
            self._stop_buffer()
            self._buffer = FrameBuffer(
                self._create_frame_iterator_factory(),
                queue_size=self.queue_size,
            )
            self._buffer.start()
            self._next_impl = self._next_from_queue
            self._current_iterator = None
            return self
        # use_queue=False: return a dedicated iterator so nested loops are safe.
        if self._current_iterator is not None:
            self._current_iterator.release()
        self._current_iterator = VideoFrameIterator(
            self,
            lambda cap, next_frame_id, cap_pos: self._read_next_valid_frame(
                cap, next_frame_id, current_cap_position=cap_pos
            ),
        )
        return self._current_iterator

    def __len__(self) -> int:
        """
        Returns the total number of frames in the video.

        Returns
        -------
        int
            Total number of frames in the video.
        """
        return self.total_frame

    def __next__(self) -> BGRFrame:
        """ Retrieves the next frame in the video, based on the specified frequency.

        When use_queue=False, delegates to the current VideoFrameIterator if one exists,
        so that next(reader) and next(iter(reader)) stay in sync.

        Returns
        -------
        BGRFrame
            The next frame as a NumPy array.

        Raises
        ------
        StopIteration
            When the video reaches the end.
        """
        if self._current_iterator is not None and not self.use_queue:
            return self._current_iterator.__next__()
        return self._next_impl()

    def release(self) -> None:
        """
        Releases the video file and stops the frame buffer if running.
        """
        self._stop_buffer()
        if self._current_iterator is not None:
            self._current_iterator.release()
            self._current_iterator = None
        self.cap.release()

    @property
    def frame_id(self) -> int:
        """
        Returns the current frame id (last yielded when using queue).

        Returns
        -------
        int
            Current frame id.
            When use_queue is True, returns the frame id of the last frame yielded from the queue.
            Otherwise, POS_FRAMES - 1 (next frame to be read).
        """
        if self.use_queue and self._current_frame_id_queue is not None:
            return self._current_frame_id_queue
        if self._current_iterator is not None and not self.use_queue:
            return self._current_iterator.frame_id
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1

    def __enter__(self) -> VideoReader:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.release()

    def __str__(self) -> str:
        return f"VideoReader(video_path={self.video_path}, total_frame={self.total_frame})"
