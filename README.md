# Expense Tracker

A minimal personal expense tracker built with Flask. There is no database and no configuration: everything lives in memory, so data resets whenever the server restarts.

## Features

- Add expenses with a title, amount and category (Food, Travel, Bills)
- Filter the expense list by category; the total follows the filter
- Set a monthly budget (must be greater than 0)
- Red warning banner showing Budget, Current Total and Overage when overall spending exceeds the budget

## Requirements

- Python 3.9 or newer

## Setup

```bash
# optional but recommended: create a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
playwright install chromium   # browser used by the end-to-end tests
```

## Run the app

```bash
python app.py
```

Open http://localhost:5000 in your browser.

## Test

The end-to-end tests (pytest + Playwright) start their own fresh server on port 5000 for every test, so **stop any running `python app.py` first**.

```bash
pytest tests/test_expense_tracker.py
```

## Build

The build runs the test suite and, only if it passes, packages `app.py`, `templates/` and `requirements.txt` into `dist/expense-mate-v1.0.zip`.

```bash
# Windows (PowerShell)
.\build.ps1
.\build.ps1 -SkipTests        # package without running tests

# Any platform
python build.py
python build.py --skip-tests
```

If PowerShell blocks the script, run it with:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

To change the version, edit `VERSION` in `build.py` (and the filename mentioned in `build.ps1`'s header comment).

## Deploy the artifact

```bash
unzip expense-mate-v1.0.zip -d expense-mate     # or extract with any zip tool
cd expense-mate
pip install -r requirements.txt
python app.py
```

`app.py` runs Flask's development server with debug mode on. For a real deployment, put the app behind a production WSGI server instead.

## Project structure

```
app.py                         Flask app and in-memory storage
templates/index.html           Single page (budget, add form, filter, table)
tests/test_expense_tracker.py  End-to-end tests
build.ps1                      Windows build wrapper
build.py                       Cross-platform build: test + package
requirements.txt
dist/                          Build output (created by the build)
```
