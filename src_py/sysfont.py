import os
import sys
from os.path import basename, splitext
from matplotlib import font_manager
from pygame.font import Font

OpenType_extensions = frozenset((".ttf", ".ttc", ".otf"))
Sysfonts = {}
Sysalias = {}
is_init = False


def _simplename(name):
    return "".join(c.lower() for c in name if c.isalnum())


def create_aliases():
    alias_groups = (
        (
            "monospace",
            "misc-fixed",
            "courier",
            "couriernew",
            "console",
            "fixed",
            "mono",
            "freemono",
            "bitstreamverasansmono",
            "verasansmono",
            "monotype",
            "lucidaconsole",
            "consolas",
            "dejavusansmono",
            "liberationmono",
        ),
        (
            "sans",
            "arial",
            "helvetica",
            "swiss",
            "freesans",
            "bitstreamverasans",
            "verasans",
            "verdana",
            "tahoma",
            "calibri",
            "gillsans",
            "segoeui",
            "trebuchetms",
            "ubuntu",
            "dejavusans",
            "liberationsans",
        ),
        (
            "serif",
            "times",
            "freeserif",
            "bitstreamveraserif",
            "roman",
            "timesroman",
            "timesnewroman",
            "dutch",
            "veraserif",
            "georgia",
            "cambria",
            "constantia",
            "dejavuserif",
            "liberationserif",
        ),
        ("wingdings", "wingbats"),
        ("comicsansms", "comicsans"),
    )
    for alias_set in alias_groups:
        for name in alias_set:
            if name in Sysfonts:
                found = Sysfonts[name]
                break
        else:
            continue
        for name in alias_set:
            if name not in Sysfonts:
                Sysalias[name] = found


def initsysfonts():
    global is_init
    if is_init:
        return
    for font_path in font_manager.findSystemFonts():
        if splitext(font_path)[1].lower() in OpenType_extensions:
            try:
                prop = font_manager.FontProperties(fname=font_path)
                name = _simplename(prop.get_name())
                bold = prop.get_weight() in ("bold", "heavy", 700, 800, 900)
                italic = prop.get_style() in ("italic", "oblique")
                if name not in Sysfonts:
                    Sysfonts[name] = {}
                Sysfonts[name][bold, italic] = font_path
            except Exception:
                pass
    create_aliases()
    is_init = True


def font_constructor(fontpath, size, bold, italic):
    font = Font(fontpath, size)
    if bold:
        font.set_bold(True)
    if italic:
        font.set_italic(True)
    return font


def SysFont(name, size, bold=False, italic=False, constructor=None):
    if constructor is None:
        constructor = font_constructor
    initsysfonts()
    gotbold = gotitalic = False
    fontname = None
    if name:
        if isinstance(name, (str, bytes)):
            name = name.split(b"," if isinstance(name, bytes) else ",")
        for single_name in name:
            if isinstance(single_name, bytes):
                single_name = single_name.decode()
            single_name = _simplename(single_name)
            styles = Sysfonts.get(single_name)
            if not styles:
                styles = Sysalias.get(single_name)
            if styles:
                plainname = styles.get((False, False))
                fontname = styles.get((bold, italic))
                if not (fontname or plainname):
                    (style, fontname) = list(styles.items())[0]
                    if bold and style[0]:
                        gotbold = True
                    if italic and style[1]:
                        gotitalic = True
                elif not fontname:
                    fontname = plainname
                elif plainname != fontname:
                    gotbold = bold
                    gotitalic = italic
            if fontname:
                break
    set_bold = set_italic = False
    if bold and not gotbold:
        set_bold = True
    if italic and not gotitalic:
        set_italic = True
    return constructor(fontname, size, set_bold, set_italic)


def get_fonts():
    initsysfonts()
    return list(Sysfonts)


def match_font(name, bold=False, italic=False):
    initsysfonts()
    fontname = None
    if isinstance(name, (str, bytes)):
        name = name.split(b"," if isinstance(name, bytes) else ",")
    for single_name in name:
        if isinstance(single_name, bytes):
            single_name = single_name.decode()
        single_name = _simplename(single_name)
        styles = Sysfonts.get(single_name)
        if not styles:
            styles = Sysalias.get(single_name)
        if styles:
            while not fontname:
                fontname = styles.get((bold, italic))
                if italic:
                    italic = False
                elif bold:
                    bold = False
                elif not fontname:
                    fontname = list(styles.values())[0]
        if fontname:
            break
    return fontname