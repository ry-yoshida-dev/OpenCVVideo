# opencv_video

## Overview

OpenCV-based utilities for reading and writing video. `VideoReader` supports efficient frame iteration and random access; `VideoWriter` encodes image sequences with optional frame-index overlays.

## Public API

Re-exported from [\_\_init\_\_.py](__init__.py):

| Symbol | Description |
|--------|-------------|
| `VideoReader` | Frame iteration, extraction, and optional background prefetch |
| `VideoWriter` | Lazy-initialized `cv2.VideoWriter` wrapper with context manager support |
| `VideoWriterParameters` | FPS, codec, and timestamp options for `VideoWriter` |
| `VideoCodec` | FourCC enum for `VideoWriter`; use `.fourcc` for the OpenCV integer |

## Components

| File / Dir | Role |
|------------|------|
| [reader/](reader/) | `VideoReader`, `VideoFrameIterator`, and `FrameBuffer`. See [reader/README.md](reader/README.md) |
| [writer/](writer/) | `VideoWriter` and `VideoWriterParameters`. See [writer/README.md](writer/README.md) |
| [codec.py](codec.py) | `VideoCodec` enum with `.fourcc` property for `cv2.VideoWriter` |
| [extension.py](extension.py) | `VideoExtension` enum and `list_extensions` helper |

## Notes

- Install and usage examples live in the [repository root README](../../README.md).
- `VideoExtension` is not re-exported from the package root; import from `opencv_video.extension` when needed.
