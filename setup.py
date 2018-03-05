import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

install_requires = ['prompt_toolkit']
if sys.version_info < (2, 6):
    warnings.warn(
        'Python 2.5 is no longer officially supported by Wit. '
        'If you have any questions, please file an issue on Github or '
        'contact us at help@wit.ai.',
        DeprecationWarning)
    install_requires.append('requests >= 0.8.8, < 0.10.1')
    install_requires.append('ssl')
else:
    install_requires.append('requests >= 0.8.8')

if sys.version_info < (3, 0):
    try:
        from util import json
    except ImportError:
        install_requires.append('simplejson')

setup(
    name='wit',
    version='5.1.0',
    description='Wit SDK for Python',
    author='The Wit Team',
    author_email='help@wit.ai',
    cmdclass={'build_py': build_py},
    install_requires=install_requires,
    packages=['wit'],
    url='http://github.com/wit-ai/pywit',
)
