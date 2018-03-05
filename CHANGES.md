## v5.1.0
Added `session_id` to context in `messenger.py` (thanks @davidawad)

## v5.0.0
The most important change is the removal of `.converse()` and `.run_actions()`. Follow the migration tutorial [here](https://github.com/wit-ai/wit-stories-migration-tutorial), or [read more here](https://wit.ai/blog/2017/07/27/sunsetting-stories).

### Breaking changes

- `converse` and `run_actions` are removed
- updated and added new examples that leverage the /message API

## v4.3.0

- `message` now takes an optional `context` as second parameter
- `converse` and `run_actions` are deprecated
- `interactive` now calls `message`
- Python 3 compatibility (future imports)

## v4.2.0

- added a `speech()` method to send audio files to the API (thanks @willywongi)

## v4.1.0

### Breaking changes

- `converse` now takes `reset` as optional parameter.
- `run_actions` now resets the last turn on new messages and errors.

## v4.0.0

After a lot of internal dogfooding and bot building, we decided to change the API in a backwards-incompatible way. The changes are described below and aim to simplify user code and accommodate upcoming features.

See `./examples` to see how to use the new API.

### Breaking changes

- `say` renamed to `send` to reflect that it deals with more than just text
- Removed built-in actions `merge` and `error`
- Actions signature simplified with `request` and `response` arguments
- INFO level replaces LOG level
- adding verbose option for `message`, `converse` and `run_actions`

## v3.5

- allows for overriding API version, by setting `WIT_API_VERSION`
- fixes unicode error
- adds custom logging
- warns instead of throwing when validating actions

### breaking

- bumped default API version from `20160330` to `20160516`

## v3.4.1

- `interactive()` mode
- fixed default arg for `context`
- fixed `say` action in `examples/quickstart.py`
- examples to take the Wit access token in argument

## v3.4.0

Unifying action parameters

### breaking

- the `say` action now takes 3 parameters: `session_id`, `context`, `msg`
- the `error` action now takes 3 parameters: `session_id`, `context`, `e`

## v3.3.0

Updating action parameters

### breaking

- the `merge` action now takes 4 parameters: `session_id`, `context`, `entities`, `msg`
- the `error` action now takes `context` as second parameter
- custom actions now take 2 parameters: `session_id`, `context`

## v3.2

- Fixed request keyword arguments issue
- Better error messages

## v3.1

- Added `examples/template.py`
- Fixed missing type
- Updated `examples/weather.py` to `examples/quickstart.py` to reflect the docs

## v3.0

Bot Engine integration

### breaking

- the `message` API is wrapped around a `Wit` class, and doesn't take the token as first parameter

## v2.0

Rewrite in pure Python

### breaking

- audio recording and streaming have been removed because:
  - many people only needed access to the HTTP API, and audio recording did not make sense for server-side use cases
  - dependent on platform, choice best left to developers
  - forced us to maintain native bindings as opposed to a pure Pythonic library
- we renamed the functions to match the HTTP API more closely
  - `.text_query(string, access_token)` becomes `.message(access_token, string)`
- all functions now return a Python dict instead of a JSON string
