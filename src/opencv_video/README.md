# opencv_video

## Overview

OpenCV-based utilities for reading, writing, and combining video. Public names are re-exported from the package root, except `VideoExtension` (import it from `opencv_video.extension`).

## Components

| Component | Description |
|------------|------|
| [types.py](types.py) | `BGRFrame` alias, `BGR_CHANNELS`, and the `as_bgr_frame` validator |
| [codec.py](codec.py) | `VideoCodec` FourCC enum for `cv2.VideoWriter` |
| [extension.py](extension.py) | `VideoExtension` enum and `list_extensions` helper |
| [reader/](reader/README.md) | `VideoReader` and its iteration helpers |
| [writer/](writer/README.md) | `VideoWriter` and `VideoWriterParameters` |
| [combinator/](combinator/README.md) | `VideoCombinator`, `VideoCombinatorParameters`, and `StopCriteria` |
