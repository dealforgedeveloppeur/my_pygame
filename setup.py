import os
import sys
import pathlib
import platform
import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

MIN_PYTHON_VERSION = (3, 12)
if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit(f"My_Pygame nécessite Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} ou plus récent.")

BASE_DIR = pathlib.Path(__file__).resolve().parent
IS_MSC = sys.platform == "win32" and "MSC" in sys.version

METADATA = {
    "name": "my_pygame",
    "version": "0.0.1",
    "description": "Mon fork personnalisé de Pygame",
    "python_requires": ">=3.12",
    "classifiers": [
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
}

def get_cython_extensions() -> list[Extension]:
    pyx_files = list((BASE_DIR / "src_c").rglob("*.pyx"))
    extensions = []
    
    c_include_dir = str(BASE_DIR / "src_c" / "include")
    src_c_dir = str(BASE_DIR / "src_c")
    
    for path in pyx_files:
        parts = path.with_suffix("").parts
        if "my_pygame" in parts:
            idx = parts.index("my_pygame")
            module_name = ".".join(parts[idx:])
        else:
            module_name = path.stem
            
        extensions.append(
            Extension(
                name=module_name, 
                sources=[str(path)],
                include_dirs=[c_include_dir, src_c_dir]
            )
        )
    return extensions

class CustomBuildExt(build_ext):
    def build_extensions(self):
        machine = platform.machine().lower()
        is_x86 = machine.startswith(("x86", "i686")) or machine == "amd64"
        is_arm32 = machine.startswith(("armv7", "armv8l"))

        detect_avx2 = os.environ.get("PYGAME_DETECT_AVX2", "").strip() != ""
        enable_arm_neon = os.environ.get("ENABLE_ARM_NEON", "").strip() == "1"

        for ext in self.extensions:
            if IS_MSC:
                ext.extra_compile_args.extend(["/W3", "/wd4142", "/wd4996"])
            else:
                ext.extra_compile_args.extend(["-Wall", "-Wno-error=unknown-pragmas"])

            if detect_avx2 and is_x86:
                if self.compiler.compiler_type == "msvc":
                    ext.extra_compile_args.append("/arch:AVX2")
                elif self.compiler.compiler_type in ["unix", "mingw32"]:
                    ext.extra_compile_args.append("-mavx2")

            if enable_arm_neon:
                ext.define_macros.append(("PG_ENABLE_ARM_NEON", "1"))
                if not IS_MSC and is_arm32:
                    ext.extra_compile_args.append("-mfpu=neon")

        super().build_extensions()

ext_modules = []
cython_exts = get_cython_extensions()

if cython_exts:
    try:
        from Cython.Build import cythonize
        ext_modules = cythonize(
            cython_exts,
            compiler_directives={"language_level": "3"},
            quiet=True
        )
    except ImportError:
        sys.exit("Cython est requis pour compiler ce projet. Veuillez l'installer.")

setup(
    **METADATA,
    packages=setuptools.find_packages(where="src_py"),
    package_dir={"": "src_py"},
    package_data={
        "": ["*.h", "*.pxd"],
    },
    ext_modules=ext_modules,
    cmdclass={
        "build_ext": CustomBuildExt,
    },
    zip_safe=False,
    include_package_data=True,
)
