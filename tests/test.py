import os
import unittest

import cv2
import numpy as np

from opencv_video import VideoReader, VideoWriter, VideoWriterParameters, as_bgr_frame
from opencv_video.codec import VideoCodec


class TestBGRFrame(unittest.TestCase):

    def test_as_bgr_frame_accepts_valid_array(self) -> None:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        narrowed = as_bgr_frame(frame)
        self.assertEqual(narrowed.shape, (480, 640, 3))

    def test_as_bgr_frame_rejects_invalid_shape(self) -> None:
        grayscale = np.zeros((480, 640), dtype=np.uint8)
        with self.assertRaises(ValueError):
            as_bgr_frame(grayscale)

    def test_as_bgr_frame_rejects_invalid_dtype(self) -> None:
        frame = np.zeros((480, 640, 3), dtype=np.float32)
        with self.assertRaises(TypeError):
            as_bgr_frame(frame)


class TestVideoReader(unittest.TestCase):

    def setUp(self):
        self.video_path = "test_video.mp4"
        self.frame_path = "test_frame.jpg"
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        dummy_frame[:, :] = (0, 0, 255)
        cv2.imwrite(self.frame_path, dummy_frame)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(self.video_path, fourcc, 20.0, (640, 480))
        for _ in range(100):
            out.write(cv2.imread(self.frame_path))
        out.release()

    def tearDown(self):
        for path in (self.video_path, self.frame_path, "output.mp4"):
            if os.path.exists(path):
                os.remove(path)

    def test_extract_frame(self):
        video_reader = VideoReader(video_path=self.video_path)
        extracted_frame = video_reader.extract_frame(0)
        self.assertIsNotNone(extracted_frame)
        video_reader.release()

    def test_iterate_frames(self):
        video_reader = VideoReader(video_path=self.video_path, iter_start_frame=0, freq=1)
        frames = list(video_reader)
        self.assertEqual(len(frames), 100)
        self.assertIsNotNone(frames[0])
        video_reader.release()

        video_reader_freq = VideoReader(video_path=self.video_path, iter_start_frame=0, freq=2)
        frames_freq = list(video_reader_freq)
        self.assertEqual(len(frames_freq), 50)
        video_reader_freq.release()

        video_reader_start = VideoReader(video_path=self.video_path, iter_start_frame=50, freq=1)
        frames_start = list(video_reader_start)
        self.assertEqual(len(frames_start), 50)
        video_reader_start.release()


class TestVideoWriter(unittest.TestCase):

    def tearDown(self):
        if os.path.exists("output.mp4"):
            os.remove("output.mp4")

    def test_write_video(self):
        params = VideoWriterParameters(fps=20, codec=VideoCodec.MP4V)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with VideoWriter("output.mp4", params) as writer:
            for _ in range(10):
                writer.write(frame.copy())
        self.assertTrue(os.path.exists("output.mp4"))


if __name__ == "__main__":
    unittest.main()
