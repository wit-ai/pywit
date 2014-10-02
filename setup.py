from distutils.core import setup, Extension
from distutils.command.build import build as _build
from distutils.command.clean import clean as _clean
from distutils.spawn import find_executable
from subprocess import call
import os
import shutil

class build(_build):
    def run(self):
        if not find_executable("cargo"):
            print("Building pywit requires cargo. See installation instructions at http://crates.io/")
            return
        if not os.path.isdir("libwit"):
            print("Cloning libwit repository...")
            if call(["git", "clone", "https://github.com/wit-ai/libwit"]):
                print("[error] could not clone libwit repository, aborting.")
                return
        else:
            print("Updating libwit repository...")
            if call(["git", "pull"], cwd="libwit"):
                print("[error] could not update libwit repository, aborting.")
                return
        if not os.path.isfile("libwit/lib/libwit.a"):
            print("Compiling libwit...")
            if call(["./build_c.sh"], shell=True, cwd="libwit"):
                print("[error] could not build libwit, aborting.")
                return
        _build.run(self)

class clean(_clean):
    def run(self):
        call(["./clean_c.sh"], shell=True, cwd="libwit")
        _clean.run(self)

wit = Extension(
    'wit',
    include_dirs=['libwit/include'],
    library_dirs=['libwit/lib'],
    sources=['pywit.c'],
    libraries=['wit', 'sox', 'curl']
)
setup(
    name='PyWit',
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
