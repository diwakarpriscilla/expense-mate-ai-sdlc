from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

CATEGORIES = ["Food", "Travel", "Bills"]

# In-memory storage: resets whenever the server restarts.
expenses = []
budget = None


@app.route("/", methods=["GET", "POST"])
def index():
    global budget
    expense_error = None
    budget_error = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "add_expense":
            title = request.form.get("title", "").strip()
            category = request.form.get("category", "")
            try:
                amount = float(request.form.get("amount", ""))
            except ValueError:
                amount = None

            if not title:
                expense_error = "Please enter a title."
            elif amount is None or amount <= 0:
                expense_error = "Please enter a valid amount greater than 0."
            elif category not in CATEGORIES:
                expense_error = "Please choose a category."
            else:
                expenses.append({"title": title, "amount": amount, "category": category})
                return redirect(url_for("index"))

        elif action == "set_budget":
            try:
                value = float(request.form.get("budget", ""))
            except ValueError:
                value = None

            if value is None or value <= 0:
                budget_error = "Budget must be a number greater than 0."
            else:
                budget = value
                return redirect(url_for("index"))

    selected_category = request.args.get("category", "All")
    if selected_category not in CATEGORIES:
        selected_category = "All"

    visible = [
        e for e in expenses
        if selected_category == "All" or e["category"] == selected_category
    ]
    filtered_total = sum(e["amount"] for e in visible)

    overall_total = sum(e["amount"] for e in expenses)
    overage = None
    if budget is not None and overall_total > budget:
        overage = overall_total - budget

    return render_template(
        "index.html",
        expenses=visible,
        filtered_total=filtered_total,
        overall_total=overall_total,
        budget=budget,
        overage=overage,
        categories=CATEGORIES,
        selected_category=selected_category,
        expense_error=expense_error,
        budget_error=budget_error,
    )


if __name__ == "__main__":
    app.run(debug=True)
