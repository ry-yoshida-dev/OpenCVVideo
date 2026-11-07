# reader

## Overview

Video frame reading with seek/read strategy selection, safe nested iteration, and optional background prefetch.

## Components

| Component | Description |
|------|------|
| [video_reader.py](video_reader.py) | `VideoReader`: iteration, frame extraction, and optional prefetch |
| [frame_iterator.py](frame_iterator.py) | `VideoFrameIterator`: per-iteration capture for safe nested loops |
| [iteration_source.py](iteration_source.py) | `IterationSource`: reader settings a frame iterator depends on |
| [buffer.py](buffer.py) | `FrameBuffer`: background thread and bounded queue for `use_queue=True` |
| [utils.py](utils.py) | Shared capture position helpers |
