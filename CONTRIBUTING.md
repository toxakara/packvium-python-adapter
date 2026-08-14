# Contributing

Thanks for looking. This package is small and additive — please keep it that way.

## Getting set up

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest
```

## The rules that matter here

**No hard dependency on `packvium`.** `dependencies = []` is deliberate: this package
must install on its own. `packvium` is only pulled in through the `test` extra, to
exercise the fallback path.

**A missing native wheel must never surface as an unhandled exception from the caller's
perspective beyond the one documented `RuntimeError`.** `backend()` and `pack()` catch
`ImportError` from the optional `packvium-native` wheel and fall through to the pure
Python package; only if *that* is also missing does `pack()` raise, with a message that
says what to install.

**Determinism.** The native and pure-Python paths must agree on every field that
`packvium` documents. A behavioural difference between them is a bug in whichever one is
wrong, not a documented quirk.

## Pull requests

- One logical change per pull request.
- Commit messages in imperative mood, under 72 characters:
  `type(scope): description` with `feat`, `fix`, `refactor`, `chore`, `docs` or `test`.
- Add or update tests. `pytest` must pass on Python 3.9 through 3.13.
- Do not bump the version; releases are cut separately.

## Reporting a bug

Please include the full request that reproduces it and `backend()`'s return value at the
time. For anything with security implications, follow [SECURITY.md](SECURITY.md) rather
than opening a public issue.
