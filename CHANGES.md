## v2.0

Rewrite in pure Python and integrate the Bot API

### breaking

- audio recording and streaming have been removed because:
  - many people only needed access to the HTTP API, and audio recording did not make sense for server-side use cases
  - dependent on platform, choice best left to developers
  - forced us to maintain native bindings as opposed to a pure Pythonic library
- we renamed the functions to match the HTTP API more closely
  - `.text_query(string, access_token)` becomes `.message(access_token, string)`
- all functions now return a Python dict instead of a JSON string
