import os
import platform
import sys
import warnings
from abc import ABC, abstractmethod
from typing import List, Optional, Type
from pygame import error as PygameError

class CameraNotInitializedError(PygameError):
    def __init__(self, message="pygame.camera is not initialized"):
        super().__init__(message)

class AbstractCamera(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def get_size(self) -> tuple:
        pass

    @abstractmethod
    def query_image(self) -> bool:
        pass

    @abstractmethod
    def get_image(self, dest_surf=None):
        pass

    @abstractmethod
    def get_raw(self) -> bytes:
        pass

def _colorspace_not_available(*args, **kwargs):
    raise RuntimeError("pygame is not built with colorspace support")

try:
    from pygame import _camera
    colorspace = _camera.colorspace
except ImportError:
    colorspace = _colorspace_not_available

class CameraFactory:
    _is_initialized: bool = False
    _selected_backend: Optional[str] = None
    _camera_class_mapping: dict = {}

    @classmethod
    def get_backends(cls) -> List[str]:
        possible_backends = []
        if sys.platform == "win32":
            version_code = platform.win32_ver()[0].split(".")[0]
            if "Server" in version_code:
                version_code = ''.join(filter(str.isdigit, version_code))[:4]
                minimum_satisfied = int(version_code) >= 2012
            else:
                minimum_satisfied = int(version_code) >= 8
            if minimum_satisfied:
                try:
                    import cv2
                    possible_backends.append("OpenCV")
                except ImportError:
                    possible_backends.append("_camera (MSMF)")
        if "linux" in sys.platform:
            possible_backends.append("_camera (V4L2)")
        if "darwin" in sys.platform:
            possible_backends.append("OpenCV-Mac")
        if "OpenCV" not in possible_backends:
            possible_backends.append("OpenCV")
        if sys.platform == "win32":
            possible_backends.append("VideoCapture")
        camera_env = os.environ.get("PYGAME_CAMERA", "").lower()
        if camera_env == "opencv" and "OpenCV" in possible_backends:
            possible_backends.remove("OpenCV")
            possible_backends.insert(0, "OpenCV")
        elif camera_env in ("vidcapture", "videocapture") and "VideoCapture" in possible_backends:
            possible_backends.remove("VideoCapture")
            possible_backends.insert(0, "VideoCapture")
        return possible_backends

    @classmethod
    def initialize(cls, backend_name: Optional[str] = None) -> None:
        supported_backends = [b.lower() for b in cls.get_backends()]
        if not supported_backends:
            raise PygameError("No camera backends are supported on your platform!")
        chosen_backend = supported_backends[0] if backend_name is None else backend_name.lower()
        if chosen_backend not in supported_backends:
            warnings.warn(
                f"We don't think '{chosen_backend}' is a supported backend on this system, but we'll try it...",
                Warning,
                stacklevel=2,
            )
        try:
            cls._load_backend_classes(chosen_backend)
            cls._selected_backend = chosen_backend
            cls._is_initialized = True
        except ImportError:
            emsg = f"Backend '{chosen_backend}' is not supported on your platform!"
            if chosen_backend in ("opencv", "opencv-mac", "videocapture"):
                dep = "vidcap" if chosen_backend == "videocapture" else "OpenCV"
                emsg += f" Make sure you have '{dep}' installed to be able to use this backend"
            raise PygameError(emsg)

    @classmethod
    def _load_backend_classes(cls, backend: str) -> None:
        if backend == "opencv-mac":
            from pygame import _camera_opencv
            cls._camera_class_mapping["list_cameras"] = _camera_opencv.list_cameras_darwin
            cls._camera_class_mapping["Camera"] = _camera_opencv.CameraMac

        elif backend == "opencv":
            from pygame import _camera_opencv
            cls._camera_class_mapping["list_cameras"] = _camera_opencv.list_cameras
            cls._camera_class_mapping["Camera"] = _camera_opencv.Camera

        elif backend in ("_camera (msmf)", "_camera (v4l2)"):
            from pygame import _camera
            cls._camera_class_mapping["list_cameras"] = _camera.list_cameras
            cls._camera_class_mapping["Camera"] = _camera.Camera

        elif backend == "videocapture":
            from pygame import _camera_vidcapture
            warnings.warn(
                "The VideoCapture backend is not recommended and may be removed. "
                "For Python3 and Windows 8+, there is now a native Windows backend built into pygame.",
                DeprecationWarning,
                stacklevel=3,
            )
            _camera_vidcapture.init()
            cls._camera_class_mapping["list_cameras"] = _camera_vidcapture.list_cameras
            cls._camera_class_mapping["Camera"] = _camera_vidcapture.Camera
        else:
            raise ValueError("unrecognized backend name")

    @classmethod
    def list_cameras(cls) -> List:
        if not cls._is_initialized:
            raise CameraNotInitializedError()
        return cls._camera_class_mapping["list_cameras"]()

    @classmethod
    def create_camera(cls, *args, **kwargs) -> AbstractCamera:
        if not cls._is_initialized:
            raise CameraNotInitializedError()
        camera_class: Type[AbstractCamera] = cls._camera_class_mapping["Camera"]
        return camera_class(*args, **kwargs)

    @classmethod
    def shutdown(cls) -> None:
        cls._camera_class_mapping.clear()
        cls._selected_backend = None
        cls._is_initialized = False

def init(backend: Optional[str] = None) -> None:
    CameraFactory.initialize(backend)

def quit() -> None:
    CameraFactory.shutdown()

def list_cameras() -> List:
    return CameraFactory.list_cameras()

def Camera(*args, **kwargs) -> AbstractCamera:
    return CameraFactory.create_camera(*args, **kwargs)

def get_backends() -> List[str]:
    return CameraFactory.get_backends()