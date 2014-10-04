from distutils.core import setup, Extension
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.spawn import find_executable
from subprocess import call
from platform import platform
import os
import shutil

class build(_build):
    def run(self):
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
	if call(["curl", "-o", "libwit.a", "/".join(["https://raw.githubusercontent.com/wit-ai/libwit/master/releases", LIBWIT_FILE])], cwd="libwit/lib"):
		print("[error] unable to retrieve libwit")
		return
        _build.run(self)

wit = Extension(
    'wit',
    include_dirs=['libwit/include'],
    library_dirs=['libwit/lib'],
    sources=['pywit.c'],
    libraries=['wit', 'sox', 'curl']
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
    }
)
