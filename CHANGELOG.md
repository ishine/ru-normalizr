# Changelog

All notable changes to `ru-normalizr` will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [0.1.0] - 2026-03-11

### Added
- Initial standalone `ru_normalizr` package extracted from private TTS workflow.
- Public Python API: `normalize`, `Normalizer`, `normalize_batch`, `run_stage`, and `preprocess_text`.
- Standalone CLI via `python -m ru_normalizr` and `ru-normalizr`.
- Fixed-order normalization pipeline for:
  - preprocess cleanup
  - Roman numerals
  - years, dates, and time
  - cardinal numerals, ordinals, decimals, fractions, and hyphenated numeric words
  - abbreviations, initials, and letter-by-letter expansions
  - optional dictionary normalization
  - optional Latin transliteration
- Native dictionary loader for `.dic` files.
- Library test suite moved into `ru_normalizr/tests`.
- Package metadata, typing marker, and wheel build support.
- PEP8 formatted.

### Changed
- Consolidated morphology loading through a shared cached helper.
- Expanded parity coverage against legacy normalization behavior.

### Notes
- TTS-specific pause hacks, pronunciation logic, accentization, and audio/model integration remain intentionally out of scope. ru-normalizr is only handling book normalization.
