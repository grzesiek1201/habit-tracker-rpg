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

- Install the Codecov GitHub App for this repository (no token needed for public repos).
- After the first CI run, the coverage report will be available. Replace `USER/REPO` in the links above.
- CI enforces a minimum threshold: `coverage report --fail-under=85`.
