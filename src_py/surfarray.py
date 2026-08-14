from pygame.pixelcopy import (
    array_to_surface,
    surface_to_array,
    map_array as pix_map_array,
    make_surface as pix_make_surface,
)
import numpy
from numpy import (
    array as numpy_array,
    empty as numpy_empty,
    uint32 as numpy_uint32,
    ndarray as numpy_ndarray,
)

import warnings
numpy_floats = [
    getattr(numpy, type_name)
    for type_name in "float32 float64 float96".split()
    if hasattr(numpy, type_name)
]
numpy_floats.append(float)
_pixel2d_bitdepths = {8, 16, 32}


__all__ = [
    "array2d",
    "array3d",
    "array_alpha",
    "array_blue",
    "array_colorkey",
    "array_green",
    "array_red",
    "array_to_surface",
    "blit_array",
    "get_arraytype",
    "get_arraytypes",
    "make_surface",
    "map_array",
    "pixels2d",
    "pixels3d",
    "pixels_alpha",
    "pixels_blue",
    "pixels_green",
    "pixels_red",
    "surface_to_array",
    "use_arraytype",
]


def blit_array(surface, array):
    if isinstance(array, numpy_ndarray) and array.dtype in numpy_floats:
        array = array.round(0).astype(numpy_uint32)
    return array_to_surface(surface, array)


def make_surface(array):
    if isinstance(array, numpy_ndarray) and array.dtype in numpy_floats:
        array = array.round(0).astype(numpy_uint32)
    return pix_make_surface(array)


def array2d(surface):
    bpp = surface.get_bytesize()
    try:
        dtype = (numpy.uint8, numpy.uint16, numpy.int32, numpy.int32)[bpp - 1]
    except IndexError:
        raise ValueError(f"unsupported bit depth {bpp * 8} for 2D array")
    size = surface.get_size()
    array = numpy.empty(size, dtype)
    surface_to_array(array, surface)
    return array


def pixels2d(surface):
    if surface.get_bitsize() not in _pixel2d_bitdepths:
        raise ValueError("unsupported bit depth for 2D reference array")
    try:
        return numpy_array(surface.get_view("2"), copy=False)
    except (ValueError, TypeError):
        raise ValueError(
            f"bit depth {surface.get_bitsize()} unsupported for 2D reference array"
        )


def array3d(surface):
    width, height = surface.get_size()
    array = numpy.empty((width, height, 3), numpy.uint8)
    surface_to_array(array, surface)
    return array


def pixels3d(surface):
    return numpy_array(surface.get_view("3"), copy=False)


def array_alpha(surface):
    size = surface.get_size()
    array = numpy.empty(size, numpy.uint8)
    surface_to_array(array, surface, "A")
    return array


def pixels_alpha(surface):
    return numpy.array(surface.get_view("A"), copy=False)


def pixels_red(surface):
    return numpy.array(surface.get_view("R"), copy=False)


def array_red(surface):
    size = surface.get_size()
    array = numpy.empty(size, numpy.uint8)
    surface_to_array(array, surface, "R")
    return array


def pixels_green(surface):
    return numpy.array(surface.get_view("G"), copy=False)


def array_green(surface):
    size = surface.get_size()
    array = numpy.empty(size, numpy.uint8)
    surface_to_array(array, surface, "G")
    return array


def pixels_blue(surface):
    return numpy.array(surface.get_view("B"), copy=False)


def array_blue(surface):
    size = surface.get_size()
    array = numpy.empty(size, numpy.uint8)
    surface_to_array(array, surface, "B")
    return array


def array_colorkey(surface):
    size = surface.get_size()
    array = numpy.empty(size, numpy.uint8)
    surface_to_array(array, surface, "C")
    return array


def map_array(surface, array):
    if array.ndim == 0:
        raise ValueError("array must have at least 1 dimension")
    shape = array.shape
    if shape[-1] != 3:
        raise ValueError("array must be a 3d array of 3-value color data")
    target = numpy_empty(shape[:-1], numpy.int32)
    pix_map_array(target, array, surface)
    return target


def use_arraytype(arraytype):
    warnings.warn(
        DeprecationWarning(
            "only numpy arrays are now supported, "
            "this function will be removed in a "
            "future version of the module"
        )
    )
    arraytype = arraytype.lower()
    if arraytype != "numpy":
        raise ValueError("invalid array type")


def get_arraytype():
    warnings.warn(
        DeprecationWarning(
            "only numpy arrays are now supported, "
            "this function will be removed in a "
            "future version of the module"
        )
    )
    return "numpy"


def get_arraytypes():
    warnings.warn(
        DeprecationWarning(
            "only numpy arrays are now supported, "
            "this function will be removed in a "
            "future version of the module"
        )
    )
    return ("numpy",)
