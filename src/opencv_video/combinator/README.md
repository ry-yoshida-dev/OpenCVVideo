# combinator

## Overview

Combine multiple input videos into a single grid-layout output video. Each cell is letterboxed to a fixed size; encoding uses [VideoWriter](../writer/).

## Components

| File | Role |
|------|------|
| [processor.py](processor.py) | `VideoCombinator`: grid composition and output writing |
| [parameter.py](parameter.py) | `VideoCombinatorParameters`: grid layout and iteration settings |
| [stop_criteria.py](stop_criteria.py) | `StopCriteria`: when to stop reading inputs |

## VideoCombinatorParameters

| Field | Default | Description |
|-------|---------|-------------|
| `rows` | `2` | Number of grid rows |
| `stop_criteria` | `StopCriteria.SHORT_VIDEO_END` | Stop when any video ends, or when all have ended |
| `image_shape` | `(1080, 1920)` | Per-cell size as `(height, width)` |
| `iter_start_frame` | `0` | Start frame for each input |
| `end_frame` | `-1` | Max output frames; `-1` means no limit |
| `freq` | `1` | Frame step for each input reader |

Output encoding (FPS, codec, timestamp overlay) is configured via `VideoWriterParameters`.

## Example

```python
from opencv_video import VideoCombinator, VideoCombinatorParameters, VideoWriterParameters
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
