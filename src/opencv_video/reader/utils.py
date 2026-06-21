"""Shared utilities for reader components."""

# When extract_frame target is within this many frames of last position, use read() instead of seek.
EXTRACT_SEEK_THRESHOLD = 20


def cap_position_after_read(frame_id: int, freq: int) -> int:
    """Position of the capture after reading the frame at frame_id (0-based)."""
    return max(0, frame_id - freq + 1) + freq
