from flask import Flask, render_template, request, jsonify, redirect, url_for
import chess
import uuid

app = Flask(__name__)

# Diccionario en memoria: id_partida -> datos
games = {}

def create_game():
    game_id = str(uuid.uuid4())
    games[game_id] = {
        "board": chess.Board(),
        "players": {
            "white": None,
            "black": None
        }
    }
    return game_id

@app.route("/")
def index_root():
    return redirect(url_for("new_game"))

@app.route("/new")
def new_game():
    game_id = create_game()
    return redirect(url_for("setup_game", game_id=game_id))

@app.route("/setup/<game_id>", methods=["GET", "POST"])
def setup_game(game_id):
    game = games.get(game_id)
    if not game:
        return "Partida no encontrada", 404

    if request.method == "POST":
        name = request.form.get("name")
        color = request.form.get("color")

        if color not in ["white", "black"]:
            return "Color inválido", 400

        # Asignar jugador
        if game["players"][color] is None:
            game["players"][color] = name
        else:
            return "Ese color ya está ocupado", 400

        return redirect(url_for("view_game", game_id=game_id))

    return render_template("setup.html", game_id=game_id, players=game["players"])

@app.route("/game/<game_id>")
def view_game(game_id):
    game = games.get(game_id)
    if not game:
        return "Partida no encontrada", 404

    return render_template(
        "index.html",
        fen=game["board"].fen(),
        game_id=game_id,
        players=game["players"]
    )

@app.route("/move/<game_id>", methods=["POST"])
def move(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"ok": False, "error": "Partida no encontrada"}), 404

    board = game["board"]
    data = request.get_json()
    uci_move = data.get("move")

    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return jsonify({"ok": False, "error": "Formato inválido"}), 400

    if move in board.legal_moves:
        board.push(move)
        return jsonify({
            "ok": True,
            "fen": board.fen(),
            "is_game_over": board.is_game_over(),
            "result": board.result() if board.is_game_over() else None
        })
    else:
        return jsonify({"ok": False, "error": "Movimiento ilegal"}), 400

@app.route("/reset/<game_id>", methods=["POST"])
def reset(game_id):
    game = games.get(game_id)
    if not game:
        return jsonify({"ok": False, "error": "Partida no encontrada"}), 404

    game["board"] = chess.Board()
    return jsonify({"ok": True, "fen": game["board"].fen()})

if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)


