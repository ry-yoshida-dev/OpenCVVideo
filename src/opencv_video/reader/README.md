# reader

## Overview

Video frame reading with seek/read strategy selection, safe nested iteration, and optional producer–consumer prefetch.

## Components

| File | Role |
|------|------|
| [video_reader.py](video_reader.py) | `VideoReader` (`@dataclass`): main reader with seek/read strategy and optional prefetch |
| [frame_iterator.py](frame_iterator.py) | `VideoFrameIterator`: per-iteration capture for safe nested loops |
| [utils.py](utils.py) | Shared reader utilities (capture position helpers) |
| [buffer.py](buffer.py) | `FrameBuffer`: background thread + bounded queue for `use_queue=True` |

## VideoReader parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `iter_start_frame` | `0` | First frame index for iteration |
| `freq` | `1` | Step between yielded frames |
| `freq_th` | `10` | Above this, each step uses seek; at or below, sequential read with minimal seeks |
| `use_queue` | `False` | Prefetch frames in a background thread |
| `queue_size` | `2` | Max queued frames when `use_queue=True` |

## Notes

- **`use_queue=False`**: `__iter__` returns a dedicated `VideoFrameIterator` with its own `VideoCapture`, so nested `for` loops on the same reader do not share capture state.
- **`extract_frame`**: Uses a separate capture when the prefetch queue is active; otherwise seeks or advances by `read()` when the target is within `EXTRACT_SEEK_THRESHOLD` frames of the last extract position.
- **`__len__`**: Returns `total_frame` from capture metadata (may be inaccurate for some files; iteration prefers `ret` over metadata at end-of-stream).

## Example

```python
from opencv_video import VideoReader

with VideoReader("input.mp4", iter_start_frame=0, freq=2) as reader:
    for frame in reader:
        process(frame)

frame = reader.extract_frame(100)
```
