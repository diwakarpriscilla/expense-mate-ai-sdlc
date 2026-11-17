# Expense Tracker

A minimal personal expense tracker built with Flask. No database and no setup: expenses are kept in an in-memory Python list, so they reset when the server restarts.

## Features

- Add an expense (title and amount)
- View the list of expenses, with a running total

## Run

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Structure

```
app.py              Flask app and in-memory storage
templates/index.html  Single page (form + expense list)
requirements.txt
```
