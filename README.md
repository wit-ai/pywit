# pywit

`pywit` is a Python client to easily use the [Wit.ai](http://wit.ai) HTTP API.

## Install

```bash
pip install wit
```

## Usage

```python
import wit
print(wit.message('MY_ACCESS_TOKEN', 'turn on the lights in the kitchen'))
```

See below for more examples.

## Install from source

```bash
git clone https://github.com/wit-ai/pywit
python setup.py install
```

## API

```python
import wit

if __name__ == '__main__':
	access_token = 'MY_ACCESS_TOKEN'

  # GET /message to extract intent and entities from user request
	response = wit.message('turn on the lights in the kitchen', access_token)
	print('/message -> {}'.format(response))
```
