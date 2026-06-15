from enum import Enum


class StopCriteria(Enum):
    """
    Criteria that control when multi-video grid composition stops.

    Attributes
    ----------
    LONGEST_VIDEO_END
        Continue until every input video has finished; shorter streams show black frames.
    SHORT_VIDEO_END
        Stop as soon as any input video finishes.
    """

    LONGEST_VIDEO_END = "longest_video_end"
    SHORT_VIDEO_END = "short_video_end"
