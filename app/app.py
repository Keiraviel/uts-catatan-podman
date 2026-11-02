import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify


def create_app(db_path=None):
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path or os.environ.get("DB_PATH", "/data/catatan.db")

    def get_db():
        folder = os.path.dirname(app.config["DB_PATH"])
        if folder:
            os.makedirs(folder, exist_ok=True)
        conn = sqlite3.connect(app.config["DB_PATH"])
        conn.row_factory = sqlite3.Row
        return conn

    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS catatan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT NOT NULL,
                isi TEXT NOT NULL
            )"""
        )

    @app.route("/")
    def index():
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM catatan ORDER BY id DESC").fetchall()
        return render_template("index.html", catatan=rows, edit=None)

    @app.route("/tambah", methods=["POST"])
    def tambah():
        judul = request.form.get("judul", "").strip()
        isi = request.form.get("isi", "").strip()
        if judul and isi:
            with get_db() as conn:
                conn.execute("INSERT INTO catatan (judul, isi) VALUES (?, ?)", (judul, isi))
        return redirect(url_for("index"))

    @app.route("/edit/<int:id>")
    def edit(id):
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM catatan ORDER BY id DESC").fetchall()
            item = conn.execute("SELECT * FROM catatan WHERE id = ?", (id,)).fetchone()
        if item is None:
            return redirect(url_for("index"))
        return render_template("index.html", catatan=rows, edit=item)

    @app.route("/update/<int:id>", methods=["POST"])
    def update(id):
        judul = request.form.get("judul", "").strip()
        isi = request.form.get("isi", "").strip()
        if judul and isi:
            with get_db() as conn:
                conn.execute("UPDATE catatan SET judul = ?, isi = ? WHERE id = ?", (judul, isi, id))
        return redirect(url_for("index"))

    @app.route("/hapus/<int:id>", methods=["POST"])
    def hapus(id):
        with get_db() as conn:
            conn.execute("DELETE FROM catatan WHERE id = ?", (id,))
        return redirect(url_for("index"))

    @app.route("/health")
    def health():
        return jsonify(status="ok", versi=os.environ.get("APP_VERSION", "dev"))

    return app
