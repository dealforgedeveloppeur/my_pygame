from pygame._freetype import (
    Font,
    STYLE_NORMAL,
    STYLE_OBLIQUE,
    STYLE_STRONG,
    STYLE_UNDERLINE,
    STYLE_WIDE,
    STYLE_DEFAULT,
    init,
    quit,
    get_init,
    was_init,
    get_cache_size,
    get_default_font,
    get_default_resolution,
    get_error,
    get_version,
    set_default_resolution,
)

from pygame.sysfont import match_font, get_fonts, SysFont as _SysFont

__all__ = [
    "Font",
    "STYLE_NORMAL",
    "STYLE_OBLIQUE",
    "STYLE_STRONG",
    "STYLE_UNDERLINE",
    "STYLE_WIDE",
    "STYLE_DEFAULT",
    "init",
    "quit",
    "get_init",
    "was_init",
    "get_cache_size",
    "get_default_font",
    "get_default_resolution",
    "get_error",
    "get_version",
    "set_default_resolution",
    "match_font",
    "get_fonts",
]


def SysFont(name, size, bold=False, italic=False, constructor=None):
    if constructor is None:
        def constructor(fontpath, size, bold, italic):
            font = Font(fontpath, size)
            font.strong = bold
            font.oblique = italic
            return font
    return _SysFont(name, size, bold, italic, constructor)
