# Wit Python SDK [![Latest Version](https://pypip.in/version/wit/badge.png)](https://pypi.python.org/pypi/wit)

`pywit` is the Python SDK for [Wit.AI](http://wit.ai).

## Prerequisites

This package requires:

* libsox (with -dev files on Debian/Ubuntu, `brew install sox` on OS X)
* libcurl (with -dev files on Debian/Ubuntu, `brew install curl` on OS X)
* a recent enough version of Python 2.7:
    * for OS X users: you can install it via Homebrew using `brew install python`. The version currently shipped with OS X is too old
    * for Linux users: make sure the python dev files are installed (`sudo apt-get install python-dev` on Debian)

## Installation instructions

### Using pip

```bash
pip install wit
```

### Regular way

Run the following commands into the main directory (where `setup.py` and `pywit.c` are located):
```bash
python setup.py build
sudo python setup.py install
```

## Usage

```python
import wit

access_token = 'ACCESS_TOKEN'

wit.init()
print('Reponse: {}'.format(wit.text_query('turn on the lights in the kitchen', access_token)))
print('Response: {}'.format(wit.voice_query_auto(access_token)))
wit.close()
```

See example files for further information.
