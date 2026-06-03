# writer

## Overview

Encode a sequence of BGR images to a video file. The underlying `cv2.VideoWriter` is created on the first `write()` call once frame dimensions are known.

## Components

| File | Role |
|------|------|
| [core.py](core.py) | `VideoWriter`: `write`, `release`, context manager |
| [parameter.py](parameter.py) | `VideoWriterParameters`: FPS, codec, optional frame-index overlay |

## VideoWriterParameters

| Field | Default | Description |
|-------|---------|-------------|
| `fps` | `30` | Output frame rate |
| `codec` | `VideoCodec.MP4V` | FourCC via `VideoCodec.fourcc` in [codec.py](../codec.py) |
| `is_timestamp_enabled` | `False` | Draw `Frame: {id}` on each frame |
| `freq` | `1` | Step for `IDManager` when timestamp is enabled |
| `start_index` | `0` | Validated; reserved for future offset use |

## Notes

- **`self.writer is None`**: Intentional until the first frame supplies `(width, height)`.
- **Timestamp overlay**: `write()` copies the input array before `cv2.putText` so the caller's buffer is not modified in place.
- **`release()`**: Logs success at INFO via `logging` (`opencv_video.writer.core`).

## Example

```python
import numpy as np
from opencv_video import VideoWriter, VideoWriterParameters, VideoCodec

params = VideoWriterParameters(fps=30, codec=VideoCodec.MP4V)

with VideoWriter("output.mp4", params) as writer:
    for _ in range(100):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
```
