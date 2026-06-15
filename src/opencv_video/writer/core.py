import logging
from types import TracebackType

import cv2
import numpy as np
from pathlib import Path
from typing import Self

from .parameter import VideoWriterParameters
from ..types import BGRFrame

logger = logging.getLogger(__name__)

class VideoWriter:
    """
    A class for writing video files from images.

    Attributes:
    ----------
    params: VideoWriterParameters
        The parameters for the video writer.
    output_path: str
        The path to save the video.
    writer: cv2.VideoWriter | None
        The writer for the video.

    Raises
    ------
    ValueError:
        If the codec is not supported.
    """
    def __init__(
        self, 
        output_path: str,
        params: VideoWriterParameters
        ) -> None:
        """
        Initialize the video writer.

        Parameters:
        ----------
        first_image: BGRFrame
            The first image to write.
        params: VideoWriterParameters
            The parameters for the video writer.
        """
        self.params = params
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path = output_path
        self.writer: cv2.VideoWriter | None = None

    def write(
        self, 
        image: BGRFrame
        ) -> None:
        """
        Write an image to the video.

        Parameters:
        ----------
        image: BGRFrame
            The image to write.
        """
        if self.writer is None:
            self.writer = self.params.initialize_writer(
                output_path=self.output_path,
                image_size=(image.shape[1], image.shape[0]),
            )  # (width, height)

        frame = image.copy() if self.params.is_timestamp_enabled else image
        if self.params.is_timestamp_enabled:
            timestamp = self.params.get_timestamp()
            cv2.putText(frame, timestamp, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
            cv2.putText(frame, timestamp, (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        self.writer.write(frame)
            
    def release(self) -> None:
        if self.writer is None:
            return
        self.writer.release()
        logger.info("Video created successfully: %s", self.output_path)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.release()