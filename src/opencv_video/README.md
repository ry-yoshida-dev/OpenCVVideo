# opencv_video

## Overview

OpenCV-based utilities for reading, writing, and combining video. `VideoReader` supports efficient frame iteration and random access; `VideoWriter` encodes image sequences with optional frame-index overlays; `VideoCombinator` tiles multiple inputs into a grid output.

## Public API

Re-exported from [\_\_init\_\_.py](__init__.py):

| Symbol | Description |
|--------|-------------|
| `VideoReader` | Frame iteration, extraction, and optional background prefetch |
| `VideoWriter` | Lazy-initialized `cv2.VideoWriter` wrapper with context manager support |
| `VideoWriterParameters` | FPS, codec, and timestamp options for `VideoWriter` |
| `VideoCodec` | FourCC enum for `VideoWriter`; use `.fourcc` for the OpenCV integer |
| `VideoCombinator` | Grid-layout composition of multiple input videos |
| `VideoCombinatorParameters` | Grid layout and iteration settings for `VideoCombinator` |
| `StopCriteria` | When to stop composing (`SHORT_VIDEO_END` or `LONGEST_VIDEO_END`) |
| `BGRFrame` | Type alias for OpenCV BGR frames (`NDArray[np.uint8]`, shape `(H, W, 3)`) |
| `as_bgr_frame` | Validate and narrow a raw NumPy array to `BGRFrame` |

## Components

| File / Dir | Role |
|------------|------|
| [types.py](types.py) | `BGRFrame` alias, `BGR_CHANNELS`, and `as_bgr_frame` validator |
| [combinator/](combinator/) | `VideoCombinator`, `VideoCombinatorParameters`, and `StopCriteria`. See [combinator/README.md](combinator/README.md) |
| [reader/](reader/) | `VideoReader`, `VideoFrameIterator`, and `FrameBuffer`. See [reader/README.md](reader/README.md) |
| [writer/](writer/) | `VideoWriter` and `VideoWriterParameters`. See [writer/README.md](writer/README.md) |
| [codec.py](codec.py) | `VideoCodec` enum with `.fourcc` property for `cv2.VideoWriter` |
| [extension.py](extension.py) | `VideoExtension` enum and `list_extensions` helper |

## Notes

- Install and usage examples live in the [repository root README](../../README.md).
- `VideoExtension` is not re-exported from the package root; import from `opencv_video.extension` when needed.
