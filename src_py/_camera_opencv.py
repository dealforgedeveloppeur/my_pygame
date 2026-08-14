import sys
import time
import numpy
import pygame
import cv2
import cv2_enumerate_cameras

def list_cameras() -> list[int]:
    return [camera_info.index for camera_info in cv2_enumerate_cameras.enumerate_cameras()]

def find_camera_details_by_name(cam_name: str) -> tuple:
    for cam in cv2_enumerate_cameras.enumerate_cameras():
        if cam.name == cam_name:
            return cam.index, cam.backend
    return None, None	         

class Camera:
    def __init__(self, device=0, size=(640, 480), mode="RGB", api_preference=None):
        self.api_preference = api_preference
        if isinstance(device, str):
            self._device_index, cam_backend = find_camera_details_by_name(device)
            if self._device_index is None:
                raise ValueError(f"Camera named '{device}' not found.")
            if api_preference is None:
                self.api_preference = cam_backend
        elif isinstance(device, int):
            self._device_index = device
        else:
            raise TypeError(f"Device must be an int or a str, not {type(device).__name__}")
        self._size = size
        if self.api_preference is None and sys.platform == "win32":
            self.api_preference = cv2.CAP_DSHOW
        modes = {
            "RGB": cv2.COLOR_BGR2RGB,
            "YUV": cv2.COLOR_BGR2YUV,
            "HSV": cv2.COLOR_BGR2HSV
        }
        if mode not in modes:
            raise ValueError("Not a supported mode")
        self._fmt = modes[mode]
        self._open = False

    def start(self):
        if self._open:
            return
        if self.api_preference is not None:
            self._cam = cv2.VideoCapture(self._device_index, self.api_preference)
        else:
            self._cam = cv2.VideoCapture(self._device_index)
        if not self._cam.isOpened():
            raise ValueError("Could not open camera.")
        self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, self._size[0])
        self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self._size[1])
        w = self._cam.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = self._cam.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self._size = (int(w), int(h))
        self._flipx = False
        self._flipy = False
        fps = self._cam.get(cv2.CAP_PROP_FPS)
        self._frametime = 1 / fps if fps > 0 else 1 / 30
        self._last_frame_time = 0
        self._open = True

    def stop(self):
        if self._open:
            self._cam.release()
            self._cam = None
            self._open = False

    def _check_open(self):
        if not self._open:
            raise pygame.error("Camera must be started")

    def get_size(self):
        self._check_open()
        return self._size

    def set_controls(self, hflip=None, vflip=None, brightness=None):
        self._check_open()
        if hflip is not None:
            self._flipx = bool(hflip)
        if vflip is not None:
            self._flipy = bool(vflip)
        if brightness is not None:
            self._cam.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        return self.get_controls()

    def get_controls(self):
        self._check_open()
        return (self._flipx, self._flipy, self._cam.get(cv2.CAP_PROP_BRIGHTNESS))

    def query_image(self):
        self._check_open()
        return time.time() - self._last_frame_time > self._frametime

    def get_image(self, dest_surf=None):
        self._check_open()
        self._last_frame_time = time.time()
        success, image = self._cam.read()
        if not success:
            raise RuntimeError("Failed to grab frame")
        image = cv2.cvtColor(image, self._fmt)
        flip_code = None
        if self._flipx:
            flip_code = 1 if not self._flipy else -1
        elif self._flipy:
            flip_code = 0
        if flip_code is not None:
            image = cv2.flip(image, flip_code)
        image = numpy.fliplr(image)
        image = numpy.rot90(image)
        surf = pygame.surfarray.make_surface(image)
        if dest_surf:
            dest_surf.blit(surf, (0, 0))
            return dest_surf
        return surf

    def get_raw(self):
        self._check_open()
        self._last_frame_time = time.time()
        success, image = self._cam.read()
        if not success:
            raise RuntimeError("Failed to grab frame.")
        return image.tobytes()