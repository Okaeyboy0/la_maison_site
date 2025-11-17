from flask import Flask, render_template, request, redirect
import requests
import csv
import sqlite3
from datetime import datetime

from datetime import datetime

app = Flask(__name__)
app.jinja_env.globals['datetime'] = datetime


# ==========================================================
#  CURRENCY FETCHER (Live Updates)
# ==========================================================
def get_rates():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        data = requests.get(url).json()

        usd_to_ngn = data["rates"]["NGN"]
        usd_to_gbp = 1 / data["rates"]["USD"] * data["rates"]["GBP"]
        usd_to_cfa = data["rates"]["XOF"]

        return {
            "USD_NGN": round(usd_to_ngn, 2),
            "USD_GBP": round(usd_to_gbp, 2),
            "USD_CFA": round(usd_to_cfa, 2)
        }

    except:
        return {"USD_NGN": "-", "USD_GBP": "-", "USD_CFA": "-"}


# ==========================================================
#  NEWSLETTER DATABASE INIT
# ==========================================================
def init_db():
    conn = sqlite3.connect("newsletter.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            created TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# Initialize DB on startup
init_db()


# ==========================================================
#  ROUTES
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html", rates=get_rates())


@app.route("/trackify")
def trackify():
    return render_template("trackify.html", rates=get_rates())


@app.route("/services")
def services():
    return render_template("services.html", rates=get_rates())


@app.route("/about")
def about():
    return render_template("about.html", rates=get_rates())

@app.route("/pricing")
def pricing():
    return render_template("pricing.html", rates=get_rates())
@app.route("/currency")
def currency():
    return render_template("currency.html", rates=get_rates())

# ==========================================================
#  CONTACT FORM
# ==========================================================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        # Store messages in CSV (simple inbox)
        with open("contact_messages.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), name, email, message])

        return redirect("/contact?success=1")

    return render_template("contact.html", rates=get_rates())


# ==========================================================
#  NEWSLETTER SUBSCRIBE (SQLite)
# ==========================================================
@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    msg = ""

    if request.method == "POST":
        email = request.form.get("email")

        try:
            conn = sqlite3.connect("newsletter.db")
            c = conn.cursor()
            c.execute("INSERT INTO subscribers (email, created) VALUES (?, ?)",
                      (email, datetime.now()))
            conn.commit()
            conn.close()
            msg = "success"

        except:
            msg = "exists"      # Duplicate email or DB error

    return render_template("newsletter.html", msg=msg, rates=get_rates())


# ==========================================================
#  RUN APP
# ==========================================================
if __name__ == "__main__":
    app.run(debug=True)
