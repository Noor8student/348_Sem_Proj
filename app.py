from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "nba.db")
SCHEMA = os.path.join(BASE_DIR, "schema.sql")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    with open("schema.sql", "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()
    db.close()


@app.route("/")
def home():
    return redirect(url_for("players"))


@app.route("/players", methods=["GET", "POST"])
def players():
    db = get_db()

    if request.method == "POST":
        player_name = request.form["player_name"].strip()
        team_name = request.form["team_name"].strip()
        ppg = request.form["ppg"]
        rpg = request.form["rpg"]
        apg = request.form["apg"]
        bpg = request.form["bpg"]
        spg = request.form["spg"]
        fg_pct = request.form["fg_pct"]
        three_pt_pct = request.form["three_pt_pct"]
        ft_pct = request.form["ft_pct"]

        db.execute("""
            INSERT INTO players
            (player_name, team_name, ppg, rpg, apg, bpg, spg, fg_pct, three_pt_pct, ft_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (player_name, team_name, ppg, rpg, apg, bpg, spg, fg_pct, three_pt_pct, ft_pct))

        db.commit()
        return redirect(url_for("players"))

    all_players = db.execute("""
        SELECT *
        FROM players
        ORDER BY player_name ASC
    """).fetchall()

    return render_template("players.html", players=all_players)


@app.route("/edit/<int:player_id>", methods=["GET", "POST"])
def edit_player(player_id):
    db = get_db()

    if request.method == "POST":
        player_name = request.form["player_name"].strip()
        team_name = request.form["team_name"].strip()
        ppg = request.form["ppg"]
        rpg = request.form["rpg"]
        apg = request.form["apg"]
        bpg = request.form["bpg"]
        spg = request.form["spg"]
        fg_pct = request.form["fg_pct"]
        three_pt_pct = request.form["three_pt_pct"]
        ft_pct = request.form["ft_pct"]

        db.execute("""
            UPDATE players
            SET player_name = ?, team_name = ?, ppg = ?, rpg = ?, apg = ?, bpg = ?, spg = ?,
                fg_pct = ?, three_pt_pct = ?, ft_pct = ?
            WHERE player_id = ?
        """, (player_name, team_name, ppg, rpg, apg, bpg, spg, fg_pct, three_pt_pct, ft_pct, player_id))

        db.commit()
        return redirect(url_for("players"))

    player = db.execute("""
        SELECT *
        FROM players
        WHERE player_id = ?
    """, (player_id,)).fetchone()

    return render_template("edit_player.html", player=player)


@app.route("/delete/<int:player_id>", methods=["POST"])
def delete_player(player_id):
    db = get_db()
    db.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
    db.commit()
    return redirect(url_for("players"))


@app.route("/report", methods=["GET"])
def report():
    db = get_db()

    team_name = request.args.get("team_name", "").strip()
    min_ppg = request.args.get("min_ppg", "").strip()
    max_ppg = request.args.get("max_ppg", "").strip()
    min_rpg = request.args.get("min_rpg", "").strip()
    max_rpg = request.args.get("max_rpg", "").strip()
    min_apg = request.args.get("min_apg", "").strip()
    max_apg = request.args.get("max_apg", "").strip()
    min_bpg = request.args.get("min_bpg", "").strip()
    min_spg = request.args.get("min_spg", "").strip()
    min_fg_pct = request.args.get("min_fg_pct", "").strip()
    min_three_pt_pct = request.args.get("min_three_pt_pct", "").strip()
    min_ft_pct = request.args.get("min_ft_pct", "").strip()

    query = """
        SELECT *
        FROM players
        WHERE 1=1
    """
    params = []

    if team_name:
        query += " AND team_name = ?"
        params.append(team_name)

    if min_ppg:
        query += " AND ppg >= ?"
        params.append(min_ppg)

    if max_ppg:
        query += " AND ppg <= ?"
        params.append(max_ppg)

    if min_rpg:
        query += " AND rpg >= ?"
        params.append(min_rpg)

    if max_rpg:
        query += " AND rpg <= ?"
        params.append(max_rpg)

    if min_apg:
        query += " AND apg >= ?"
        params.append(min_apg)

    if max_apg:
        query += " AND apg <= ?"
        params.append(max_apg)

    if min_bpg:
        query += " AND bpg >= ?"
        params.append(min_bpg)

    if min_spg:
        query += " AND spg >= ?"
        params.append(min_spg)

    if min_fg_pct:
        query += " AND fg_pct >= ?"
        params.append(min_fg_pct)

    if min_three_pt_pct:
        query += " AND three_pt_pct >= ?"
        params.append(min_three_pt_pct)

    if min_ft_pct:
        query += " AND ft_pct >= ?"
        params.append(min_ft_pct)

    query += " ORDER BY ppg DESC, player_name ASC"

    filtered_players = db.execute(query, params).fetchall()

    summary = db.execute(f"""
        SELECT
            COUNT(*) AS total_players,
            ROUND(AVG(ppg), 2) AS avg_ppg,
            ROUND(AVG(rpg), 2) AS avg_rpg,
            ROUND(AVG(apg), 2) AS avg_apg,
            ROUND(AVG(bpg), 2) AS avg_bpg,
            ROUND(AVG(spg), 2) AS avg_spg
        FROM ({query})
    """, params).fetchone()

    teams = db.execute("""
        SELECT DISTINCT team_name
        FROM players
        ORDER BY team_name ASC
    """).fetchall()

    return render_template(
        "report.html",
        players=filtered_players,
        teams=teams,
        selected_team=team_name,
        min_ppg=min_ppg,
        max_ppg=max_ppg,
        min_rpg=min_rpg,
        max_rpg=max_rpg,
        min_apg=min_apg,
        max_apg=max_apg,
        min_bpg=min_bpg,
        min_spg=min_spg,
        min_fg_pct=min_fg_pct,
        min_three_pt_pct=min_three_pt_pct,
        min_ft_pct=min_ft_pct,
        summary=summary
    )


if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=10000)