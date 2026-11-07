# tests

## Overview

Pytest suite for `opencv_video`. Videos are generated per test in a temporary directory.

## Components

| Component | Description |
|------|------|
| [conftest.py](conftest.py) | `make_video` fixture that writes a small video with a distinct gray level per frame |
| [test_types.py](test_types.py) | `as_bgr_frame` validation |
| [test_reader.py](test_reader.py) | `VideoReader` iteration, prefetch, nested loops, frame extraction, and `skip` |
| [test_writer.py](test_writer.py) | `VideoCodec`, `VideoWriterParameters`, and `VideoWriter` |
| [test_combinator.py](test_combinator.py) | `VideoCombinator` stop criteria, grid layout, letterboxing, and parameter validation |
