# ru-normalizr

Normalization-only Russian text preprocessing extracted into a standalone package.

`ru-normalizr` focuses on deterministic Russian text normalization:
- years, dates, time, decimals, fractions, ordinals, and cardinal numerals
- abbreviations, initials, Roman numerals, cleanup rules, and glued OCR-like text
- Latin transliteration via dictionary rules or `eng_to_ipa`

Out of scope by design:
- accentization and stress dictionaries
- pronunciation and post-phoneme fixes
- TTS pause hacks and chunking
- audio, model, or engine integration

## Installation

```bash
pip install ru-normalizr
```

`eng_to_ipa` is installed by default, so the IPA backend is available out of the box.

## API

```python
from ru_normalizr import NormalizeOptions, Normalizer, normalize, preprocess_text

text = normalize("Глава IV. Встреча в 10:07.")
prepared = preprocess_text("10кг")

tts_normalizer = Normalizer(NormalizeOptions.tts())
batch = tts_normalizer.normalize_batch(["Глава IV.", "В 1980-е годы было 25 млн."])
roman_only = tts_normalizer.run_stage("roman", "Глава IV")
```

### Example outputs

```python
from ru_normalizr import normalize

print(normalize("Глава IV. Встреча в 10:07."))
# Глава четыре. Встреча в десять, ноль семь.

print(normalize("В 1980-е годы было 25 млн. $"))
# В тысяча девятьсот восьмидесятые годы было двадцать пять миллионов долларов

print(normalize("Добавьте 1/4 стакана воды."))
# Добавьте одну четвертую стакана воды.

print(normalize("И. О. Фамилия приехал."))
# и о фамилия приехал.
```

### Modes

`NormalizeOptions()` uses the conservative `safe` preset by default.
Use `NormalizeOptions.tts()` when you want the more aggressive TTS-oriented behavior.

`safe` is intended for general text where it is more important not to over-normalize:
- keeps all-caps headings as-is
- keeps initials like `И. О. Фамилия`
- keeps letter abbreviations like `ГИБДД`
- keeps bracketed numeric links like `(1)` and `[1]`
- keeps Latin transliteration disabled

`tts` is intended for speech-oriented pipelines:
- enables caps normalization and first-word decap
- removes confident bracketed numeric links
- expands initials and letter-by-letter abbreviations
- enables Latin transliteration
- keeps IPA stress markers disabled by default unless explicitly requested

### Configuring options

```python
from ru_normalizr import NormalizeOptions, normalize

options = NormalizeOptions.tts(
    latinization_backend="ipa",
    enable_latinization_stress_marks=False,
)

print(normalize("YouTube в 2024 г.", options))
```

You can also start from the conservative preset and override individual flags:

```python
from ru_normalizr import NormalizeOptions, normalize

options = NormalizeOptions.safe(
    enable_letter_abbreviation_expansion=True,
    enable_latinization=True,
    latinization_backend="dictionary",
)

print(normalize("USB drive", options))
```

Granular abbreviation controls:
- `enable_contextual_abbreviation_expansion` for contextual abbreviations such as `т. д.`, `т. п.`, `млн.`, `тыс.`
- `enable_initials_expansion` for patterns such as `И. О. Фамилия`
- `enable_letter_abbreviation_expansion` for letter-by-letter expansions such as `ГИБДД`, `ООН`, `USB`

Latinization controls:
- `enable_latinization`
- `latinization_backend="ipa" | "dictionary"`
- `enable_latinization_stress_marks`

When `latinization_backend="ipa"`, stress markers are omitted by default.
Enable `enable_latinization_stress_marks=True` if you want `+` markers in the output.

### Example dictionaries

Runtime dictionary assets shipped in the package live under `ru_normalizr/dictionaries/`.
Latinization rules live under `ru_normalizr/dictionaries/latinization/`.
The editable example override file lives in `examples/your_rules.dic` in the source tree and is not included in published wheels.

### Batch usage

```python
from ru_normalizr import Normalizer

normalizer = Normalizer(NormalizeOptions.tts())
texts = ["Глава IV.", "12.03.2025", "Цена 1.5 кг сахара."]
print(normalizer.normalize_batch(texts))
```

Available stage names for expert use:
- `preprocess`
- `roman`
- `years`
- `dates_time`
- `numerals`
- `abbreviations`
- `dictionary`
- `latinization`
- `finalize`

Stage order is fixed in the main pipeline. Stage-level calls are for debugging, testing, and focused use, not for arbitrary reordering.

## CLI

```bash
python -m ru_normalizr "Глава IV. Встреча в 10:07."
echo "В 1980-е годы было 25 млн." | python -m ru_normalizr
ru-normalizr --mode safe "ГИБДД"
ru-normalizr --mode tts --file ./sample.txt
ru-normalizr --mode tts --file ./sample.txt --output ./sample.normalized.txt
ru-normalizr --mode tts --latinization-backend ipa --with-latin-stress "YouTube в 2024 г."
```

Useful CLI flags:
- `--mode safe|tts`
- `--latinization-backend ipa|dictionary`
- `--with-latin-stress`
- `--no-latinization`
- `--no-first-word-decap`
- `--keep-links`

## Development

```bash
py -3.12 -m pip install -r ./ru_normalizr/requirements-dev.txt
py -3.12 ./ru_normalizr/scripts/dev.py test
py -3.12 ./ru_normalizr/scripts/dev.py lint
py -3.12 ./ru_normalizr/scripts/dev.py build
```

## Release Notes

- Changelog: `CHANGELOG.md`
- Versioning policy: `VERSIONING.md`
- Publish checklist: `PYPI_RELEASE_CHECKLIST.md`

## Packaging

The package is self-contained inside `ru_normalizr/` and builds as a standalone wheel from that directory:

```bash
python -m pip wheel --no-deps ./ru_normalizr
```

For repeatable local workflows, use the helper script:

```bash
py -3.12 ./ru_normalizr/scripts/dev.py clean
py -3.12 ./ru_normalizr/scripts/dev.py test
py -3.12 ./ru_normalizr/scripts/dev.py lint
py -3.12 ./ru_normalizr/scripts/dev.py build
```

The supported public Python imports are from the package root, for example:

```python
from ru_normalizr import NormalizeOptions, Normalizer, normalize, preprocess_text
```
