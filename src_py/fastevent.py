import pygame.event
import pygame.display
from pygame import error, register_quit
from pygame.event import Event

_ft_init = False


def _ft_init_check():
    if not _ft_init:
        raise error("FastEvent system not initialized")


def _quit_hook():
    global _ft_init
    _ft_init = False


def init():
    global _ft_init
    if not pygame.display.get_init():
        raise error("Video system not initialized")

    register_quit(_quit_hook)
    _ft_init = True


def get_init():
    return _ft_init


def pump():
    _ft_init_check()
    pygame.event.pump()


def wait():
    _ft_init_check()
    return pygame.event.wait()


def poll():
    _ft_init_check()
    return pygame.event.poll()


def get():
    _ft_init_check()
    return pygame.event.get()


def post(event: Event):
    _ft_init_check()
    pygame.event.post(event)
