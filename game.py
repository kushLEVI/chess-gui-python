import tkinter as tk
import chess
import winsound

board = chess.Board()
selected_square = None
highlighted_squares = []

white_moves = 0
black_moves = 0

animating = False

piece_unicode = {
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
}

LIGHT = "#EEEED2"
DARK = "#769656"
HIGHLIGHT = "#F7EC59"
SELECT = "#ADD8E6"
CHECK = "#FF6B6B"

# ================= DRAW =================
def draw_board():
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)

            text = piece_unicode[piece.symbol()] if piece else ""

            color = LIGHT if (row + col) % 2 == 0 else DARK

            if square in highlighted_squares:
                color = HIGHLIGHT

            if square == selected_square:
                color = SELECT

            # highlight king in check
            if board.is_check():
                king_sq = board.king(board.turn)
                if square == king_sq:
                    color = CHECK

            buttons[row][col].config(
                text=text,
                bg=color,
                font=("Segoe UI Symbol", 32)
            )

    update_status()

# ================= HIGHLIGHT =================
def highlight_moves(square):
    global highlighted_squares
    highlighted_squares = [
        move.to_square for move in board.legal_moves
        if move.from_square == square
    ]

# ================= SOUND =================
def play_sound(capture=False):
    if capture:
        winsound.Beep(800, 120)
    else:
        winsound.Beep(500, 80)

# ================= STATUS =================
def update_status():
    turn = "White" if board.turn else "Black"

    status = f"{turn}'s Turn | White: {white_moves} | Black: {black_moves}"

    if board.is_checkmate():
        winner = "White" if not board.turn else "Black"
        status = f"🏆 CHECKMATE! {winner} Wins"
        status_label.config(text=status)
    
        show_winner(f"{winner.upper()} WINS!")
        return

    elif board.is_check():
        status += "  ⚠ CHECK!"

    elif board.is_stalemate():
        status = "DRAW (Stalemate)"

    status_label.config(text=status)

# ================= CLICK =================
def show_winner(winner_text):
    overlay = tk.Toplevel(root)
    overlay.attributes("-fullscreen", True)
    overlay.configure(bg="black")
    overlay.attributes("-alpha", 0.0)

    label = tk.Label(
        overlay,
        text=winner_text,
        font=("Arial", 60, "bold"),
        fg="white",
        bg="black"
    )
    label.place(relx=0.5, rely=0.5, anchor="center")

    # Fade-in effect
    def fade(alpha=0):
        if alpha < 0.9:
            overlay.attributes("-alpha", alpha)
            root.after(30, fade, alpha + 0.05)

    # Bounce animation
def animate(size=40, growing=True):
    if growing:
            size += 2
    if size >= 80:
            growing = False
    else:
            size -= 2
    if size <= 60:
            growing = True

    label.config(font=("Arial", size, "bold"))
    overlay.after(60, animate, size, growing)

    fade()
    animate()
def on_click(event):
    global selected_square, highlighted_squares
    global white_moves, black_moves

    if animating:
        return

    row = event.widget.grid_info()['row']
    col = event.widget.grid_info()['column']
    square = chess.square(col, 7 - row)

    piece = board.piece_at(square)

    # SELECT
    if selected_square is None:
        if piece and piece.color == board.turn:
            selected_square = square
            highlight_moves(square)

    # MOVE
    else:
        move = chess.Move(selected_square, square)
        selected_piece = board.piece_at(selected_square)

        # promotion
        if selected_piece and selected_piece.piece_type == chess.PAWN and chess.square_rank(square) in [0, 7]:
            move = chess.Move(selected_square, square, promotion=chess.QUEEN)

        if move in board.legal_moves:
            capture = board.is_capture(move)

            # COUNT BEFORE PUSH
            if board.turn:
                white_moves += 1
            else:
                black_moves += 1

            board.push(move)
            play_sound(capture)

        selected_square = None
        highlighted_squares = []

    draw_board()

# ================= UI =================
root = tk.Tk()
root.title("Chess Pro Max 😄")
root.state("zoomed")

frame = tk.Frame(root)
frame.pack(expand=True, fill="both")

buttons = []

for row in range(8):
    frame.grid_rowconfigure(row, weight=1)
    row_buttons = []

    for col in range(8):
        frame.grid_columnconfigure(col, weight=1)

        btn = tk.Button(frame, borderwidth=0)
        btn.grid(row=row, column=col, sticky="nsew")

        btn.bind("<Button-1>", on_click)

        row_buttons.append(btn)

    buttons.append(row_buttons)

status_label = tk.Label(root, font=("Arial", 14), bg="#222", fg="white")
status_label.pack(fill="x")

draw_board()
root.mainloop()
