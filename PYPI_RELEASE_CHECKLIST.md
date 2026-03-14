# PyPI Release Checklist

## Before tagging

- Ensure `py -3.12 -m pytest -q` passes.
- Ensure the working tree is in the state you want to publish.
- Review `CHANGELOG.md` and add a release entry.
- Update version in:
  - `__init__.py`
  - `pyproject.toml`
- Confirm `README.md` examples still match actual output.
- Confirm `LICENSE` is present.

## Install tooling

```bash
py -3.12 -m pip install -r requirements-dev.txt
```

## Clean local artifacts

```bash
py -3.12 scripts/dev.py clean
```

This removes local build/cache junk that should not affect the release:

- `build/`
- `dist/`
- `.tmp_dist/`
- `ru_normalizr.egg-info/`
- `.pytest_cache/`
- `.ruff_cache/`
- all `__pycache__/`
- dictionary cache files like `dictionaries/dictionaries_*.pkl`

## Release validation

Preferred full check:

```bash
py -3.12 scripts/dev.py check
```

Equivalent manual flow:

```bash
py -3.12 -m ruff check .
py -3.12 -m pytest -q
py -3.12 scripts/dev.py build
py -3.12 -m twine check dist/*
```

## Optional TestPyPI upload

```bash
py -3.12 scripts/dev.py publish --repository testpypi
```

## Final publish flow

```bash
py -3.12 scripts/dev.py publish
```

## Manual review items

- No generated cache files are committed.
- No `build/`, `dist/`, or `*.egg-info/` directories are committed.
- `examples/your_dictionary.dic` is not present in the built distributions.
- `scripts/` and `tests/` are absent from the built wheel.
- Optional `eng_to_ipa` behavior degrades gracefully when not installed.
- CLI works from stdin and inline text.
