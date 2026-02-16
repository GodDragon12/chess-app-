from flask import Flask, render_template, request, jsonify
import chess

app = Flask(__name__)

# Un solo tablero global para ejemplo simple
board = chess.Board()

@app.route("/")
def index():
    # Pasamos el FEN actual al frontend
    return render_template("index.html", fen=board.fen())

@app.route("/move", methods=["POST"])
def move():
    global board
    data = request.get_json()
    uci_move = data.get("move")  # ejemplo: "e2e4"

    try:
        move = chess.Move.from_uci(uci_move)
    except ValueError:
        return jsonify({"ok": False, "error": "Formato de movimiento inválido"}), 400

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

@app.route("/reset", methods=["POST"])
def reset():
    global board
    board = chess.Board()
    return jsonify({"ok": True, "fen": board.fen()})

if __name__ == "__main__":
    app.run(debug=True)
