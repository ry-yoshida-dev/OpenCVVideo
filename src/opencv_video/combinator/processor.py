from __future__ import annotations

import logging

import cv2
import numpy as np

from ..types import BGRFrame, as_bgr_frame
from ..reader import VideoReader
from ..writer import VideoWriter, VideoWriterParameters
from .parameter import VideoCombinatorParameters
from .stop_criteria import StopCriteria

logger = logging.getLogger(__name__)


class VideoCombinator:
    """
    Combine multiple videos into a single grid-layout output video.

    Attributes
    ----------
    video_paths : list[str]
        Paths to the input videos.
    output_path : str
        Destination path for the combined video.
    combinator_params : VideoCombinatorParameters
        Grid layout and iteration settings.
    writer_params : VideoWriterParameters
        Encoding settings for the output video.
    video_readers : list[VideoReader]
        Readers for each input video.
    columns : int
        Number of columns in the grid, derived from ``rows`` and input count.
    """

    def __init__(
        self,
        video_paths: list[str],
        output_path: str,
        combinator_params: VideoCombinatorParameters,
        writer_params: VideoWriterParameters,
    ) -> None:
        """
        Initialize the video combinator.

        Parameters
        ----------
        video_paths : list[str]
            Paths to the input videos.
        output_path : str
            Destination path for the combined video.
        combinator_params : VideoCombinatorParameters
            Grid layout and iteration settings.
        writer_params : VideoWriterParameters
            Encoding settings for the output video.

        Raises
        ------
        ValueError
            If no input videos are provided.
        """
        if not video_paths:
            raise ValueError("video_paths must contain at least one path")

        self.combinator_params = combinator_params
        self.writer_params = writer_params
        self.video_paths = video_paths
        self.output_path = output_path
        self.video_readers = [
            VideoReader(
                video_path=video_path,
                iter_start_frame=self.combinator_params.iter_start_frame,
                freq=self.combinator_params.freq,
            )
            for video_path in video_paths
        ]
        self.columns = int(np.ceil(len(self.video_readers) / self.combinator_params.rows))
        logger.info(
            "Initialized combinator: videos=%d, columns=%d, rows=%d",
            len(self.video_readers),
            self.columns,
            self.combinator_params.rows,
        )

    def create_canvas(self) -> BGRFrame:
        """
        Create an empty canvas for one output frame.

        Returns
        -------
        BGRFrame
            Zero-filled BGR canvas sized for the full grid.
        """
        cell_height, cell_width = self.combinator_params.image_shape
        width = cell_width * self.columns
        height = cell_height * self.combinator_params.rows
        return np.zeros((height, width, 3), dtype=np.uint8)

    def _get_grid_position(self, video_index: int) -> tuple[int, int]:
        """
        Get the grid position for a video index.

        Parameters
        ----------
        video_index : int
            Index of the video in ``video_readers``.

        Returns
        -------
        tuple[int, int]
            ``(row, column)`` position in the grid.
        """
        row = video_index // self.columns
        col = video_index % self.columns
        return row, col

    def _place_frame_on_canvas(
        self,
        canvas: BGRFrame,
        frame: BGRFrame,
        video_index: int,
    ) -> None:
        """
        Place a letterboxed frame on the canvas.

        Parameters
        ----------
        canvas : BGRFrame
            Target canvas.
        frame : BGRFrame
            Source frame in BGR format.
        video_index : int
            Index of the video in ``video_readers``.
        """
        resized_frame, _ = self.letterbox_resize(frame, self.combinator_params.image_shape)
        row, col = self._get_grid_position(video_index)
        cell_height, cell_width = self.combinator_params.image_shape

        y_start = row * cell_height
        y_end = y_start + resized_frame.shape[0]
        x_start = col * cell_width
        x_end = x_start + resized_frame.shape[1]

        canvas[y_start:y_end, x_start:x_end] = resized_frame

    def _read_frame_for_video(self, video_index: int) -> tuple[BGRFrame | None, bool]:
        """
        Read the next frame for one input video.

        Parameters
        ----------
        video_index : int
            Index of the video in ``video_readers``.

        Returns
        -------
        tuple[BGRFrame | None, bool]
            Frame and whether iteration should stop for this batch.
        """
        video_reader = self.video_readers[video_index]
        cell_height, cell_width = self.combinator_params.image_shape

        try:
            frame = next(video_reader)
            return frame, False
        except StopIteration:
            match self.combinator_params.stop_criteria:
                case StopCriteria.SHORT_VIDEO_END:
                    return None, True
                case StopCriteria.LONGEST_VIDEO_END:
                    blank_frame = np.zeros(
                        (cell_height, cell_width, 3),
                        dtype=np.uint8,
                    )
                    return blank_frame, False

    def _process_frame_batch(self) -> tuple[BGRFrame, int, bool]:
        """
        Read one frame from each input and compose a grid canvas.

        Returns
        -------
        tuple[BGRFrame, int, bool]
            Canvas, number of frames read successfully, and stop flag.
        """
        canvas = self.create_canvas()
        frames_available = 0
        should_stop = False

        for video_index in range(len(self.video_readers)):
            frame, stop_now = self._read_frame_for_video(video_index)
            if stop_now:
                should_stop = True
                break
            if frame is None:
                continue
            frames_available += 1
            self._place_frame_on_canvas(canvas, frame, video_index)

        if (
            self.combinator_params.stop_criteria == StopCriteria.LONGEST_VIDEO_END
            and frames_available == 0
        ):
            should_stop = True

        return canvas, frames_available, should_stop

    def combine_videos(self) -> None:
        """
        Combine input videos and write the result to ``output_path``.
        """
        video_writer = VideoWriter(self.output_path, self.writer_params)

        for reader in self.video_readers:
            iter(reader)

        frame_count = 0
        while True:
            canvas, frames_available, should_stop = self._process_frame_batch()

            if frames_available == 0:
                break

            video_writer.write(canvas)
            frame_count += 1

            if should_stop:
                break

            if (
                self.combinator_params.end_frame > 0
                and frame_count >= self.combinator_params.end_frame
            ):
                break

        video_writer.release()
        for reader in self.video_readers:
            reader.release()
        logger.info("Combined videos saved to %s (%d frames)", self.output_path, frame_count)

    @staticmethod
    def letterbox_resize(
        img: BGRFrame,
        new_shape: tuple[int, int],
        color: tuple[int, int, int] = (114, 114, 114),
    ) -> tuple[BGRFrame, float]:
        """
        Resize an image with aspect ratio preserved and letterbox padding.

        Parameters
        ----------
        img : BGRFrame
            Input image in BGR format.
        new_shape : tuple[int, int]
            Target ``(height, width)``.
        color : tuple[int, int, int], optional
            Padding color, by default ``(114, 114, 114)``.

        Returns
        -------
        tuple[BGRFrame, float]
            Letterboxed image and scaling ratio.
        """
        original_h, original_w = img.shape[:2]
        if (original_h, original_w) == new_shape:
            return img, 1.0

        new_h, new_w = new_shape
        ratio = min(new_w / original_w, new_h / original_h)
        resized_w, resized_h = int(original_w * ratio), int(original_h * ratio)
        resized_img = as_bgr_frame(
            cv2.resize(img, (resized_w, resized_h), interpolation=cv2.INTER_CUBIC)
        )

        canvas = np.full((new_h, new_w, 3), color, dtype=np.uint8)
        y_offset = (new_h - resized_h) // 2
        x_offset = (new_w - resized_w) // 2
        canvas[y_offset : y_offset + resized_h, x_offset : x_offset + resized_w] = resized_img

        return canvas, ratio

    def __str__(self) -> str:
        return (
            f"VideoCombinator(video_paths={self.video_paths}, "
            f"output_path={self.output_path}, params={self.combinator_params})"
        )
