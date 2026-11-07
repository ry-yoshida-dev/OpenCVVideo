# OpenCVVideo

## Overview

`opencv_video` provides OpenCV-based utilities for video: `VideoReader` for frame iteration, random access, and optional background prefetch; `VideoWriter` for encoding image sequences with optional frame-index overlays; and `VideoCombinator` for tiling several videos into one grid video.

## Installation

```bash
pip install -e .
```

## Usage

```python
import cv2
import numpy as np

from opencv_video import VideoCodec, VideoReader, VideoWriter, VideoWriterParameters

with VideoReader("input.mp4", iter_start_frame=10, freq=5) as reader:
    print(f"Total frames: {len(reader)}")
    for frame in reader:
        ...
    cv2.imwrite("frame_0100.jpg", reader.extract_frame(100))

params = VideoWriterParameters(fps=30, codec=VideoCodec.MP4V)
with VideoWriter("output.mp4", params) as writer:
    for _ in range(100):
        writer.write(np.zeros((480, 640, 3), dtype=np.uint8))
```
