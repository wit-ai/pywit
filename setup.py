from distutils.core import setup, Extension
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.spawn import find_executable
from subprocess import call
from platform import platform
import os
import shutil

LIBWIT_NAME = "libwit.a"
LIBWIT_PATH = os.path.join("libwit", "lib", LIBWIT_NAME)

def fetch_libwit():
    LIBWIT_FILE = None
    arch = platform().lower()
    if "arm" in arch:
        LIBWIT_FILE = "libwit-armv6.a"
    elif "64" in arch:
        if "darwin" in arch:
            LIBWIT_FILE = "libwit-64-darwin.a"
        else:
            LIBWIT_FILE = "libwit-64-linux.a"
    else:
        LIBWIT_FILE = "libwit-32-linux.a"
    print("Retrieving platform-specific libwit library... {}".format(LIBWIT_FILE))
    if call(["curl", "-L", "-o", LIBWIT_NAME, "/".join(["https://github.com/wit-ai/libwit/releases/download/1.1.1", LIBWIT_FILE])], cwd="libwit/lib"):
        raise Exception("unable to retrieve libwit")

class build(_build):
    def run(self):
        if not os.path.isfile(LIBWIT_PATH):
            fetch_libwit()
        _build.run(self)

class clean(_clean):
    def run(self):
        try:
            os.remove(LIBWIT_PATH)
        except OSError:
            pass
        _clean.run(self)

def libraries():
    arch = platform().lower()
    if "darwin" in arch:
        return ['wit', 'ssl', 'crypto', 'z', 'sox', 'System', 'pthread', 'c', 'm']
    else:
        return ['wit', 'rt', 'sox', 'ssl', 'crypto', 'dl', 'pthread', 'rt', 'gcc_s', 'pthread', 'c', 'm']

wit = Extension(
    'wit',
    include_dirs=['libwit/include'],
    library_dirs=['libwit/lib'],
    sources=['pywit.c'],
    libraries=libraries(),
    extra_link_args=['-static']
)
setup(
    name='wit',
    version='1.0',
    description='Wit SDK for Python',
    author='Julien Odent',
    author_email='julien@wit.ai',
    url='http://wit.ai',
    ext_modules=[wit],
    cmdclass={
        'build': build,
        'clean': clean,
    }
)
