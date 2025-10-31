from flask import Flask, render_template, redirect, url_for, session, request
import random

app = Flask(__name__)
app.secret_key = "tic-tac-toe-ai"  # session storage

# Winning combinations
WIN_CONDITIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Cols
    [0, 4, 8], [2, 4, 6]              # Diagonals
]

# Initialize board
def init_game():
    return [""] * 9, "X", None, False  # board, current_player, winner, draw

# Initialize score
def init_score():
    return {"X": 0, "O": 0}

# Check winner
def check_winner(board):
    for combo in WIN_CONDITIONS:
        a, b, c = combo
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], combo
    if "" not in board:
        return "Draw", None
    return None, None

# Minimax AI
def minimax(board, is_max):
    winner, _ = check_winner(board)
    if winner == "O":
        return 1
    elif winner == "X":
        return -1
    elif winner == "Draw":
        return 0

    if is_max:
        best = -999
        for i in range(9):
            if board[i] == "":
                board[i] = "O"
                score = minimax(board, False)
                board[i] = ""
                best = max(best, score)
        return best
    else:
        best = 999
        for i in range(9):
            if board[i] == "":
                board[i] = "X"
                score = minimax(board, True)
                board[i] = ""
                best = min(best, score)
        return best

# Best move for AI
def best_move(board):
    best_score = -999
    move = None
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            score = minimax(board, False)
            board[i] = ""
            if score > best_score:
                best_score = score
                move = i
    return move

@app.route("/")
def index():
    if "board" not in session:
        session["board"], session["current"], session["winner"], session["draw"] = init_game()
    if "score" not in session:
        session["score"] = init_score()

    return render_template("index.html",
                           board=session["board"],
                           winner=session["winner"],
                           draw=session["draw"],
                           current_player=session["current"],
                           score=session["score"])

@app.route("/move", methods=["POST"])
def move():
    cell = int(request.form["cell"])
    board = session["board"]

    if board[cell] == "" and session["winner"] is None and not session["draw"]:
        # Human move (X)
        board[cell] = "X"
        winner, combo = check_winner(board)
        if winner:
            if winner != "Draw":
                session["score"][winner] += 1
            session["winner"], session["draw"] = (winner if winner != "Draw" else None, winner == "Draw")
        else:
            # AI move
            ai = best_move(board)
            if ai is not None:
                board[ai] = "O"
            winner, combo = check_winner(board)
            if winner:
                if winner != "Draw":
                    session["score"][winner] += 1
                session["winner"], session["draw"] = (winner if winner != "Draw" else None, winner == "Draw")

    session["board"] = board
    return redirect(url_for("index"))

@app.route("/reset")
def reset():
    session["board"], session["current"], session["winner"], session["draw"] = init_game()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
