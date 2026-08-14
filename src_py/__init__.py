import sys
import os
import copyreg
from pathlib import Path

pygame_dir = Path(__file__).parent.resolve()
if os.name == "nt":
    os.add_dll_directory(str(pygame_dir))
del pygame_dir

if "DISPLAY" in os.environ:
    os.environ.setdefault("SDL_VIDEO_X11_WMCLASS", os.path.basename(sys.argv[0]))

def _attribute_undefined(name):
    raise RuntimeError(f"{name} is not available")

from pygame.base import *
from pygame.constants import *
from pygame.version import *
from pygame.rect import Rect
from pygame.rwobject import encode_string, encode_file_path
import pygame.surflock
import pygame.color
import pygame.display
import pygame.draw
import pygame.event
import pygame.image
import pygame.joystick
import pygame.key
import pygame.mouse
import pygame.cursors
import pygame.sprite
import pygame.threads
import pygame.pixelcopy
import pygame.mask
import pygame.time
import pygame.transform
import pygame.font
import pygame.sysfont
import pygame.mixer_music
import pygame.mixer
import pygame.scrap
import pygame.bufferproxy
import pygame.surfarray
import pygame.sndarray
import pygame.fastevent
import pygame.pkgdata
import pygame.math

from pygame.mask import Mask
from pygame.cursors import Cursor
from pygame.pixelarray import PixelArray
from pygame.surface import Surface, SurfaceType

try:
    import pygame.imageext
except (ImportError, OSError):
    pass

pygame.font.SysFont = pygame.sysfont.SysFont
pygame.font.get_fonts = pygame.sysfont.get_fonts
pygame.font.match_font = pygame.sysfont.match_font

Color = pygame.color.Color
BufferProxy = pygame.bufferproxy.BufferProxy
Vector2 = pygame.math.Vector2
Vector3 = pygame.math.Vector3


def __rect_constructor(x, y, w, h):
    return Rect(x, y, w, h)

def __rect_reduce(r):
    assert isinstance(r, Rect)
    return __rect_constructor, (r.x, r.y, r.w, r.h)

def __color_constructor(r, g, b, a):
    return Color(r, g, b, a)

def __color_reduce(c):
    assert isinstance(c, Color)
    return __color_constructor, (c.r, c.g, c.b, c.a)

copyreg.pickle(Rect, __rect_reduce, __rect_constructor)
copyreg.pickle(Color, __color_reduce, __color_constructor)

del os, sys, copyreg