from pygame import mixer
import numpy
import warnings


__all__ = [
    "array",
    "samples",
    "make_sound",
    "use_arraytype",
    "get_arraytype",
    "get_arraytypes",
]


def array(sound):
    return numpy.array(sound, copy=True)


def samples(sound):
    return numpy.array(sound, copy=False)


def make_sound(array):
    return mixer.Sound(array=array)


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