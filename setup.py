from distutils.core import setup, Extension

wit = Extension('wit', include_dirs=['include'], library_dirs=['lib'], sources=['pywit.c'], libraries=['wit', 'sox', 'curl'])
setup(name='PyWit SDK', version='1.0', description='Wit SDK for Python', ext_modules=[wit])
