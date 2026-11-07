from dataclasses import dataclass, field

import cv2
from id_manager import IDManager

from ..codec import VideoCodec


@dataclass
class VideoWriterParameters:
    """
    VideoWriterParameters is the parameters for the video writer.

    Attributes
    ----------
    fps: int
        The frames per second.
    codec: VideoCodec
        The codec for the video.
    is_timestamp_enabled: bool
        Whether to draw ``Frame: {id}`` on each frame.
    freq: int
        The step of the frame ID when the timestamp is enabled.
    start_index: int
        The start index of the timestamp. Validated but reserved for future
        offset use.
    """

    fps: int = 30
    codec: VideoCodec = VideoCodec.MP4V

    # For timestamp parameters
    is_timestamp_enabled: bool = False
    freq: int = 1
    start_index: int = 0

    id_manager: IDManager | None = field(
        init=False, default=None, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        self._validate_parameters()
        if self.is_timestamp_enabled:
            self.id_manager = IDManager(current_id=0, step=self.freq)

    def _validate_parameters(self) -> None:
        """
        Validate the parameters.

        Raises
        ------
        ValueError: If the parameters are not valid.
        """
        if self.freq <= 0:
            raise ValueError("freq must be a positive integer")
        if self.start_index < 0:
            raise ValueError("start_index must be a non-negative integer")

    def get_timestamp(self) -> str:
        """
        Get the timestamp.

        Returns
        -------
        str: The timestamp.
        """
        if self.id_manager is None:
            return ""
        time = self.id_manager.next_id
        return f"Frame: {time}"

    def initialize_writer(
        self, output_path: str, image_size: tuple[int, int]
    ) -> cv2.VideoWriter:
        """
        Initialize the video writer.

        Parameters
        ----------
        output_path: str
            The path to save the video.
        image_size: tuple[int, int]
            The size of the image.

        Returns
        -------
        cv2.VideoWriter: The video writer.
        """
        return cv2.VideoWriter(
            filename=output_path,
            fourcc=self.codec.fourcc,
            fps=float(self.fps),
            frameSize=image_size,
        )
