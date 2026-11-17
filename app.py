from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# In-memory storage: resets whenever the server restarts.
expenses = []


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        try:
            amount = float(request.form.get("amount", ""))
        except ValueError:
            amount = None

        if not title:
            error = "Please enter a title."
        elif amount is None or amount <= 0:
            error = "Please enter a valid amount greater than 0."
        else:
            expenses.append({"title": title, "amount": amount})
            return redirect(url_for("index"))

    total = sum(e["amount"] for e in expenses)
    return render_template("index.html", expenses=expenses, total=total, error=error)


if __name__ == "__main__":
    app.run(debug=True)
