import pygame

_cursor_id_table = {
    pygame.SYSTEM_CURSOR_ARROW: "SYSTEM_CURSOR_ARROW",
    pygame.SYSTEM_CURSOR_IBEAM: "SYSTEM_CURSOR_IBEAM",
    pygame.SYSTEM_CURSOR_WAIT: "SYSTEM_CURSOR_WAIT",
    pygame.SYSTEM_CURSOR_CROSSHAIR: "SYSTEM_CURSOR_CROSSHAIR",
    pygame.SYSTEM_CURSOR_WAITARROW: "SYSTEM_CURSOR_WAITARROW",
    pygame.SYSTEM_CURSOR_SIZENWSE: "SYSTEM_CURSOR_SIZENWSE",
    pygame.SYSTEM_CURSOR_SIZENESW: "SYSTEM_CURSOR_SIZENESW",
    pygame.SYSTEM_CURSOR_SIZEWE: "SYSTEM_CURSOR_SIZEWE",
    pygame.SYSTEM_CURSOR_SIZENS: "SYSTEM_CURSOR_SIZENS",
    pygame.SYSTEM_CURSOR_SIZEALL: "SYSTEM_CURSOR_SIZEALL",
    pygame.SYSTEM_CURSOR_NO: "SYSTEM_CURSOR_NO",
    pygame.SYSTEM_CURSOR_HAND: "SYSTEM_CURSOR_HAND",
}


class Cursor:
    def __init__(self, *args):
        if len(args) == 0:
            self.type = "system"
            self.data = (pygame.SYSTEM_CURSOR_ARROW,)
        elif len(args) == 1 and args[0] in _cursor_id_table:
            self.type = "system"
            self.data = (args[0],)
        elif len(args) == 1 and isinstance(args[0], Cursor):
            self.type = args[0].type
            self.data = args[0].data
        elif (
            len(args) == 2 and len(args[0]) == 2 and isinstance(args[1], pygame.Surface)
        ):
            self.type = "color"
            self.data = tuple(args)
        elif len(args) == 4 and len(args[0]) == 2 and len(args[1]) == 2:
            self.type = "bitmap"
            self.data = tuple(tuple(arg) for arg in args)
        else:
            raise TypeError("Arguments must match a cursor specification")

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __eq__(self, other):
        return isinstance(other, Cursor) and self.data == other.data

    def __ne__(self, other):
        return not self.__eq__(other)

    def __copy__(self):
        return self.__class__(self)

    copy = __copy__

    def __hash__(self):
        return hash(tuple([self.type] + list(self.data)))

    def __repr__(self):
        if self.type == "system":
            id_string = _cursor_id_table.get(self.data[0], "constant lookup error")
            return f"<Cursor(type: system, constant: {id_string})>"
        if self.type == "bitmap":
            size = f"size: {self.data[0]}"
            hotspot = f"hotspot: {self.data[1]}"
            return f"<Cursor(type: bitmap, {size}, {hotspot})>"
        if self.type == "color":
            hotspot = f"hotspot: {self.data[0]}"
            surf = repr(self.data[1])
            return f"<Cursor(type: color, {hotspot}, surf: {surf})>"
        raise TypeError("Invalid Cursor")


pygame.mouse.set_cursor = lambda *args: pygame.mouse._set_cursor(**{(c := Cursor(*args)).type: c.data})
pygame.mouse.get_cursor = lambda: Cursor(*pygame.mouse._get_cursor())