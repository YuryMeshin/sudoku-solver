import os
from flask import Flask, render_template, request, redirect, url_for
from src.solver import SudokuGrid, SudokuSolver

app = Flask(__name__)

# Start page
@app.route("/", methods=["GET", "POST"])
def index():
    dimensions = ["2x2", "2x3", "3x2", "3x3"]
    if request.method == "POST":
        dimension = request.form["dimension"]
        return redirect(url_for("grid", dimension=dimension))
    return render_template("index.html", dimensions=dimensions)

# Grid input page
@app.route("/grid", methods=["GET", "POST"])
def grid():
    dimension = request.args.get("dimension", "3x3")
    m, n = map(int, dimension.split("x"))
    board_size = (m * n) ** 2

    if request.method == "POST":
        # Collect board from form inputs
        cells = request.form.getlist("cell")
        original_cells = [c for c in cells]  # copy of what the user typed
        board_str = ",".join(c if c.isdigit() else "." for c in cells)
        solver = SudokuSolver((m, n), board_str)
        solver.solve()
        solution = solver.board.flatten()
        if solution:
            return render_template("grid.html", dimension=dimension, board="".join(solution.split(",")), original=original_cells, solved=True)
        else:
            message = "No solution found!"
            return render_template("grid.html", dimension=dimension, board=cells, message=message, original=original_cells)

    # Blank board for GET request
    blank_board = [""] * board_size
    return render_template("grid.html", dimension=dimension, board=blank_board, original=blank_board)
    

if __name__ == "__main__":
    if all(var in os.environ for var in ["FLASK_APP", "FLASK_RUN_HOST", "FLASK_RUN_PORT", "FLASK_ENV"]):
        app.run(debug=True)
    else:
        app.run(host="0.0.0.0", port=8000, debug=True)