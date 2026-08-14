import pygame
import cv2
import cv2_enumerate_cameras

def list_cameras():
    return [cam.index for cam in cv2_enumerate_cameras.enumerate_cameras()]

class Camera:
    def __init__(self, device=0, size=(640, 480), mode="RGB", show_video_window=0):
        self.device_index = device
        self.size = size
        self.cap = None

    def start(self):
        self.cap = cv2.VideoCapture(self.device_index)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.size[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.size[1])

    def stop(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    def get_surface(self, dest_surf=None):
        if not self.cap or not self.cap.isOpened():
            return dest_surf
        ret, frame = self.cap.read()
        if not ret:
            return dest_surf
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.transpose(frame)
        surf = pygame.surfarray.make_surface(frame)
        if dest_surf:
            dest_surf.blit(surf, (0, 0))
        else:
            dest_surf = surf
        return dest_surf

    def get_image(self, dest_surf=None):
        return self.get_surface(dest_surf)