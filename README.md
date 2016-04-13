# pywit

`pywit` is the Python SDK for [Wit.ai](http://wit.ai).

## Install

Using `pip`:
```bash
pip install wit
```

From source:
```bash
git clone https://github.com/wit-ai/pywit
python setup.py install
```

## Usage

See the `examples` folder for examples.

## API

`pywit` provides a Wit class with the following methods:
* `message` - the Wit message API
* `converse` - the low-level Wit converse API
* `run_actions` - a higher-level method to the Wit converse API

See the [docs](https://wit.ai/docs) for more information.
