import os
import re
import sys
import glob
import pathlib
import platform
import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install_headers import install_headers

MIN_PYTHON_VERSION = (3, 12)
if sys.version_info < MIN_PYTHON_VERSION:
    sys.exit(f"My_Pygame nécessite Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]} ou plus récent.")

BASE_DIR = pathlib.Path(__file__).resolve().parent
IS_MSC = sys.platform == "win32" and "MSC" in sys.version
IS_MAC = sys.platform == "darwin"

METADATA = {
    "name": "my_pygame",
    "version": "0.0.1",
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
    pyx_pattern = str(BASE_DIR / "src_c" / "cython" / "my_pygame" / "**" / "*.pyx")
    pyx_files = glob.glob(pyx_pattern, recursive=True)
    extensions = []
    for pyx in pyx_files:
        path = pathlib.Path(pyx)
        parts = path.with_suffix("").parts
        if "my_pygame" in parts:
            idx = parts.index("my_pygame")
            module_name = ".".join(parts[idx:])
        else:
            module_name = path.stem
        extensions.append(Extension(name=module_name, sources=[pyx]))
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

class CustomInstallHeaders(install_headers):
    def run(self):
        if not self.distribution.headers:
            return
        self.mkpath(self.install_dir)
        for header in self.distribution.headers:
            header_path = pathlib.Path(header)
            if header_path.is_dir():
                dest_dir = pathlib.Path(self.install_dir) / header_path.name
                self.mkpath(str(dest_dir))
                for file in header_path.iterdir():
                    if file.is_file():
                        out, _ = self.copy_file(str(file), str(dest_dir))
                        self.outfiles.append(out)
            else:
                out, _ = self.copy_file(str(header_path), self.install_dir)
                self.outfiles.append(out)

ext_modules = []
cython_exts = get_cython_extensions()
if cython_exts:
    from Cython.Build import cythonize
    ext_modules = cythonize(
        cython_exts,
        compiler_directives={"language_level": "3"},
        quiet=True
    )

headers = [str(file) for file in (BASE_DIR / "src_c").glob("*.h") if file.name != "scale.h"]
headers.append(str(BASE_DIR / "src_c" / "include"))

setup(
    **METADATA,
    packages=setuptools.find_packages(where="src_py"),
    package_dir={"": "src_py"},
    ext_modules=ext_modules,
    headers=headers,
    cmdclass={
        "build_ext": CustomBuildExt,
        "install_headers": CustomInstallHeaders,
    },
    zip_safe=False,
    include_package_data=True,
)
