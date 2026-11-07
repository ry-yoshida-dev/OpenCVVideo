# combinator

## Overview

Combine multiple input videos into a single grid-layout output video, letterboxing each cell to a fixed size.

## Components

| Component | Description |
|------|------|
| [processor.py](processor.py) | `VideoCombinator`: grid composition and output writing |
| [parameter.py](parameter.py) | `VideoCombinatorParameters`: grid layout and iteration settings |
| [stop_criteria.py](stop_criteria.py) | `StopCriteria`: when to stop reading inputs |

## Examples

```python
from opencv_video import (
    VideoCombinator,
    VideoCombinatorParameters,
    VideoWriterParameters,
)
from opencv_video.combinator import StopCriteria
from opencv_video.codec import VideoCodec

combinator_params = VideoCombinatorParameters(
    rows=2,
    stop_criteria=StopCriteria.LONGEST_VIDEO_END,
    image_shape=(480, 640),
)
writer_params = VideoWriterParameters(fps=30, codec=VideoCodec.MP4V)

combinator = VideoCombinator(
    video_paths=["a.mp4", "b.mp4", "c.mp4"],
    output_path="grid.mp4",
    combinator_params=combinator_params,
    writer_params=writer_params,
)
combinator.combine_videos()
```
