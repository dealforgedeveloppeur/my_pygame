__all__ = [
    "Font",
    "init",
    "quit",
    "get_default_font",
    "get_init",
    "SysFont",
    "match_font",
    "get_fonts",
]

from pygame._freetype import init, Font as _Font, get_default_resolution
from pygame._freetype import quit, get_default_font, get_init as _get_init
from pygame._freetype import _internal_mod_init
from pygame.sysfont import match_font, get_fonts, SysFont as _SysFont
from pygame import encode_file_path


class Font(_Font):
    __encode_file_path = staticmethod(encode_file_path)
    __get_default_resolution = staticmethod(get_default_resolution)
    __default_font = encode_file_path(get_default_font())

    __unull = "\x00"
    __bnull = b"\x00"

    def __init__(self, file=None, size=-1):
        size = max(size, 1)
        if isinstance(file, str):
            try:
                bfile = self.__encode_file_path(file, ValueError)
            except ValueError:
                bfile = ""
        else:
            bfile = file
        if isinstance(bfile, bytes) and bfile == self.__default_font:
            file = None
        if file is None:
            resolution = int(self.__get_default_resolution() * 0.6875)
            if resolution == 0:
                resolution = 1
        else:
            resolution = 0
        super().__init__(file, size=size, resolution=resolution)
        self.strength = 1.0 / 12.0
        self.kerning = False
        self.origin = True
        self.pad = True
        self.ucs4 = True
        self.underline_adjustment = 1.0

    def render(self, text, antialias, color, background=None):
        if text is None:
            text = ""
        if isinstance(text, str) and self.__unull in text:
            raise ValueError("A null character was found in the text")
        if isinstance(text, bytes) and self.__bnull in text:
            raise ValueError("A null character was found in the text")
        save_antialiased = (
            self.antialiased
        )
        self.antialiased = bool(antialias)
        try:
            s, _ = super().render(text, color, background)
            return s
        finally:
            self.antialiased = save_antialiased

    def set_bold(self, value):
        self.wide = bool(value)

    def get_bold(self):
        return self.wide

    bold = property(get_bold, set_bold)

    def set_italic(self, value):
        self.oblique = bool(value)

    def get_italic(self):
        return self.oblique

    italic = property(get_italic, set_italic)

    def set_underline(self, value):
        self.underline = bool(value)

    def get_underline(self):
        return self.underline

    def metrics(self, text):
        return self.get_metrics(text)

    def get_ascent(self):
        return self.get_sized_ascender()

    def get_descent(self):
        return self.get_sized_descender()

    def get_height(self):
        return self.get_sized_ascender() - self.get_sized_descender() + 1

    def get_linesize(self):
        return self.get_sized_height()

    def size(self, text):
        return self.get_rect(text).size

FontType = Font

def get_init():
    return _get_init()


def SysFont(name, size, bold=0, italic=0, constructor=None):
    if constructor is None:
        def constructor(fontpath, size, bold, italic):
            font = Font(fontpath, size)
            font.set_bold(bold)
            font.set_italic(italic)
            return font
    return _SysFont(name, size, bold, italic, constructor)


del _Font, get_default_resolution, encode_file_path
