from dataclasses import dataclass

from .stop_criteria import StopCriteria


@dataclass
class VideoCombinatorParameters:
    """
    Layout and iteration settings for grid-based video composition.

    Attributes
    ----------
    rows : int
        Number of rows in the output grid.
    stop_criteria : StopCriteria
        When to stop reading input videos.
    image_shape : tuple[int, int]
        Per-cell frame size as ``(height, width)``.
    iter_start_frame : int
        First frame index to read from each input video.
    end_frame : int
        Maximum number of output frames to write; ``-1`` means no limit.
    freq : int
        Frame step when iterating each input video.
    """

    rows: int = 2
    stop_criteria: StopCriteria = StopCriteria.SHORT_VIDEO_END
    image_shape: tuple[int, int] = (1080, 1920)
    iter_start_frame: int = 0
    end_frame: int = -1
    freq: int = 1

    def __post_init__(self) -> None:
        self._validate_parameters()

    def _validate_parameters(self) -> None:
        """
        Validate combinator parameters.

        Raises
        ------
        ValueError
            If any parameter is out of range.
        """
        if self.rows <= 0:
            raise ValueError("rows must be a positive integer")
        if self.freq <= 0:
            raise ValueError("freq must be a positive integer")
        if self.iter_start_frame < 0:
            raise ValueError("iter_start_frame must be a non-negative integer")
        if self.end_frame < -1:
            raise ValueError("end_frame must be -1 or a non-negative integer")
        height, width = self.image_shape
        if height <= 0 or width <= 0:
            raise ValueError("image_shape height and width must be positive integers")
