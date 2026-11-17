"""End-to-end tests for the Expense Tracker.

The fixtures start a fresh Flask server on http://localhost:5000 for every test,
so each test begins with empty in-memory state. Stop any server already running
on that port before running the tests.

Setup (once):
    pip install -r requirements.txt
    playwright install chromium
Run:
    pytest tests/test_expense_tracker.py
"""
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

PORT = 5000
BASE_URL = f"http://localhost:{PORT}"
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _port_in_use():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", PORT)) == 0


@pytest.fixture
def server():
    if _port_in_use():
        pytest.fail(
            f"Port {PORT} is already in use. Stop the running server; "
            "the tests start their own fresh instance."
        )
    proc = subprocess.Popen(
        [sys.executable, "-c", f"from app import app; app.run(port={PORT})"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 15
        while time.time() < deadline:
            try:
                urllib.request.urlopen(BASE_URL, timeout=1)
                break
            except OSError:
                time.sleep(0.2)
        else:
            pytest.fail("Server did not start within 15 seconds.")
        yield BASE_URL
    finally:
        proc.terminate()
        proc.wait(timeout=10)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(browser, server):
    context = browser.new_context()
    pg = context.new_page()
    pg.goto(server)
    yield pg
    context.close()


def add_expense(page, title, amount, category):
    form = page.locator("form:has(input[name=action][value=add_expense])")
    form.locator("input[name=title]").fill(title)
    form.locator("input[name=amount]").fill(str(amount))
    form.locator("select[name=category]").select_option(category)
    form.get_by_role("button", name="Add").click()
    expect(page.locator("tbody tr").filter(has_text=title)).to_be_visible()


def set_budget(page, value):
    form = page.locator("form:has(input[name=action][value=set_budget])")
    form.locator("input[name=budget]").fill(str(value))
    form.get_by_role("button").click()


def filter_by(page, category):
    page.locator("#category-filter").select_option(category)
    expect(page).to_have_url(re.compile(rf"category={category}$"))


def banner_value(page, label):
    row = page.locator(".banner div").filter(has=page.get_by_text(label, exact=True))
    return row.locator("span").nth(1)


def test_add_expenses_with_categories(page):
    expect(page.get_by_text("No expenses yet")).to_be_visible()

    add_expense(page, "Lunch", "12.50", "Food")
    add_expense(page, "Flight", "300", "Travel")
    add_expense(page, "Rent", "800.25", "Bills")

    rows = page.locator("tbody tr")
    expect(rows).to_have_count(3)
    for row, (title, category, amount) in zip(
        [rows.nth(0), rows.nth(1), rows.nth(2)],
        [("Lunch", "Food", "12.50"), ("Flight", "Travel", "300.00"), ("Rent", "Bills", "800.25")],
    ):
        cells = row.locator("td")
        expect(cells.nth(0)).to_have_text(title)
        expect(cells.nth(1)).to_have_text(category)
        expect(cells.nth(2)).to_have_text(amount)

    expect(page.locator("tfoot td").first).to_have_text("Total (All)")
    expect(page.locator("tfoot td.amount")).to_have_text("1112.75")


def test_filter_by_category_and_empty_state(page):
    add_expense(page, "Lunch", "10.00", "Food")
    add_expense(page, "Coffee", "5.50", "Food")
    add_expense(page, "Taxi", "40", "Travel")

    filter_by(page, "Food")
    expect(page.locator("tbody tr")).to_have_count(2)
    expect(page.get_by_text("Taxi")).to_have_count(0)
    expect(page.locator("tfoot td").first).to_have_text("Total (Food)")
    expect(page.locator("tfoot td.amount")).to_have_text("15.50")

    filter_by(page, "Travel")
    expect(page.locator("tbody tr")).to_have_count(1)
    expect(page.locator("tfoot td.amount")).to_have_text("40.00")

    filter_by(page, "Bills")
    expect(page.get_by_text("No expenses found in Bills")).to_be_visible()
    expect(page.locator("table")).to_have_count(0)

    filter_by(page, "All")
    expect(page.locator("tbody tr")).to_have_count(3)
    expect(page.locator("tfoot td.amount")).to_have_text("55.50")


def test_budget_warning_banner(page):
    expect(page.locator(".banner")).to_have_count(0)

    set_budget(page, "100")
    expect(page.get_by_text("Current budget: 100.00")).to_be_visible()

    add_expense(page, "Groceries", "60", "Food")
    expect(page.locator(".banner")).to_have_count(0)

    add_expense(page, "Train", "90", "Travel")
    banner = page.locator(".banner")
    expect(banner).to_be_visible()
    expect(banner).to_contain_text("Over budget")
    expect(banner).to_have_css("border-top-color", "rgb(220, 38, 38)")
    expect(banner_value(page, "Budget")).to_have_text("100.00")
    expect(banner_value(page, "Current total")).to_have_text("150.00")
    expect(banner_value(page, "Overage")).to_have_text("50.00")

    # The banner reflects overall spending, not the active filter.
    filter_by(page, "Bills")
    expect(page.locator(".banner")).to_be_visible()

    set_budget(page, "200")
    expect(page.locator(".banner")).to_have_count(0)
