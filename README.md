# Wit Python SDK

`pywit` is the Python SDK for [Wit.AI](http://wit.ai).

Requires libsox (`sudo apt-get install libsox2` on Debian, `brew install sox` on OS X)

## Installation instructions

Make sure you have a recent enough version of Python 2.7 installed
* note for OS X users: you can install it via Homebrew using `brew install python`. The version currently shipped with OS X is too old
* note for Linux users: make sure the python dev files are installed (`sudo apt-get install python-dev` on Debian)

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
