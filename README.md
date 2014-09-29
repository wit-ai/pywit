# Wit Python SDK

`pywit` is the Python SDK for [Wit.AI](http://wit.ai).

Requires [libwit](http://github.com/wit-ai/libwit).
Tested on Mac OS X 64 bits, running Python 2.7.8 from the official [64-bit/32-bit x86-64/i386 Installer](http://www.python.org/download).

## Installation instructions

Install [libwit](http://github.com/wit-ai/libwit) and copy `libwit.a` into the `lib` directory.

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
