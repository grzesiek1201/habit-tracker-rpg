# Habit Tracker RPG

[CI status](https://github.com/USER/REPO/actions/workflows/ci.yml) · [Coverage](https://codecov.io/gh/USER/REPO)

## Local setup

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Tests

```bash
pytest -q
```

## Pre-commit

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Codecov

- Włącz GitHub App Codecov na repo (publiczne nie wymaga tokenu).
- Po uruchomieniu CI, raport coverage będzie widoczny. Podmień `USER/REPO` w linkach powyżej.
- CI wymusza minimalny próg: `coverage report --fail-under=85`.
