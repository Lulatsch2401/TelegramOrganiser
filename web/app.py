import logging
import os
import re
from functools import wraps
from pathlib import Path

import yaml
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

load_dotenv()

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

LISTS_FILE = Path(os.environ.get("LISTS_FILE", str(Path(__file__).parent.parent / "lists.yaml")))
WEB_PASSWORD = os.environ.get("WEB_PASSWORD", "")
SECRET_KEY = os.environ.get("WEB_SECRET_KEY", "dev-secret-change-me")
KEY_RE = re.compile(r"^[a-z0-9_-]+$")

if not WEB_PASSWORD:
    logger.warning("WEB_PASSWORD is not set — the web UI has no password protection!")

app = Flask(__name__)
app.secret_key = SECRET_KEY


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not WEB_PASSWORD or session.get("authenticated"):
            return f(*args, **kwargs)
        return redirect(url_for("login"))
    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    if not WEB_PASSWORD:
        session["authenticated"] = True
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        if request.form.get("password") == WEB_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("index"))
        error = "Falsches Passwort"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/api/lists", methods=["GET"])
@login_required
def get_lists():
    try:
        with open(LISTS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {}
    return jsonify(data)


@app.route("/api/lists", methods=["POST"])
@login_required
def save_lists():
    data = request.get_json(force=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Ungültige Daten"}), 400

    for key in data:
        if not KEY_RE.match(str(key)):
            return jsonify({"error": f"Ungültiger Schlüssel '{key}': nur a-z, 0-9, - und _ erlaubt"}), 400

    with open(LISTS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    logger.info("Lists saved by web UI: %d entries", len(data))
    return jsonify({"ok": True, "count": len(data)})


if __name__ == "__main__":
    port = int(os.environ.get("WEB_PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
