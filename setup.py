from distutils.core import setup, Extension
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.errors import CompileError
from distutils.spawn import find_executable
from subprocess import call
from platform import platform
import os
import shutil

LIBWIT_NAME = "libwit.a"
LIBWIT_PATH = os.path.join("libwit", "lib", LIBWIT_NAME)

def fetch_libwit():
    if not os.path.exists("libwit/lib"):
      os.makedirs("libwit/lib")
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
    print("Retrieving platform-specific libwit library... {0}".format(LIBWIT_FILE))
    try:
        if call(["curl", "-L", "-Ss", "-o", LIBWIT_NAME, "/".join(["https://github.com/wit-ai/libwit/releases/download/1.1.2", LIBWIT_FILE])], cwd="libwit/lib") != 0:
            raise Exception("Unable to retrieve libwit.")
    except OSError as exc:
        raise Exception("Could not find curl. Please install curl and retry.")
    except Exception as exc:
        raise Exception("Unable to retrieve libwit: {0}".format(exc))

class build(_build):
    def run(self):
        if not os.path.isfile(LIBWIT_PATH):
            fetch_libwit()
        try:
            _build.run(self)
        except CompileError as exc:
            print("")
            print("Compilation failed. Do you have all dependencies installed?")
            print("    On Debian/Ubuntu  try: sudo apt-get install python-dev python-pip curl libcurl4-openssl-dev libsox-dev")
            print("    On RHEL/Centos    try: sudo yum install python-devel python-pip curl sox-devel openssl-devel")
            print("    On OS X           try: brew install curl python sox")

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
    libraries=libraries()
)
setup(
    name='wit',
    version='1.1',
    description='Wit SDK for Python',
    author='Julien Odent',
    author_email='julien@wit.ai',
    url='http://github.com/wit-ai/pywit',
    ext_modules=[wit],
    cmdclass={
        'build': build,
        'clean': clean
    },
    data_files=[('', ['libwit/include/wit.h', 'libwit/lib/libwit.a'])]
)
