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
