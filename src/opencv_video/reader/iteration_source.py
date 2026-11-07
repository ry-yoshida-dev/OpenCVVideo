from typing import Protocol


class IterationSource(Protocol):
    """
    Reader settings that a frame iterator needs to walk through a video.

    Attributes
    ----------
    video_path : str
        Path to the video file.
    iter_start_frame : int
        The frame number to start reading from.
    freq : int
        The step size for frame iteration.
    total_frame : int
        The total number of frames in the video.
    """

    video_path: str
    iter_start_frame: int
    freq: int
    total_frame: int
