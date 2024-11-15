import tkinter as tk
from tkinter import messagebox
import random


class CheckersGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo de Damas")

        self.board_size = 8
        self.square_size = 60
        self.canvas = tk.Canvas(self.root, width=self.board_size * self.square_size, height=self.board_size * self.square_size)
        self.canvas.pack()

        self.turn_label = tk.Label(self.root, text="Vez de: Branco", font=("Arial", 14), fg="blue")
        self.turn_label.pack()

        self.turn = "white"  # Branco sempre começa
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.selected_piece = None
        self.player_vs_ai = False

        self.create_menu()
        self.draw_board()
        self.place_pieces()

        self.canvas.bind("<Button-1>", self.handle_click)

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        game_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Jogo", menu=game_menu)

        game_menu.add_command(label="Jogar contra outro jogador", command=self.start_two_players)
        game_menu.add_command(label="Jogar contra a máquina", command=self.start_vs_ai)
        game_menu.add_separator()
        game_menu.add_command(label="Sair", command=self.root.quit)

    def start_two_players(self):
        self.player_vs_ai = False
        self.reset_game()

    def start_vs_ai(self):
        self.player_vs_ai = True
        self.reset_game()

    def reset_game(self):
        self.turn = "white"
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.selected_piece = None
        self.turn_label.config(text="Vez de: Branco", fg="blue")
        self.draw_board()
        self.place_pieces()

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(self.board_size):
            for col in range(self.board_size):
                color = "#D18B47" if (row + col) % 2 == 0 else "#FFCE9E"
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

    def place_pieces(self):
        for row in range(3):
            for col in range(self.board_size):
                if (row + col) % 2 == 1:
                    self.board[row][col] = {"color": "black", "king": False}
                    self.draw_piece(row, col, "black")

        for row in range(5, self.board_size):
            for col in range(self.board_size):
                if (row + col) % 2 == 1:
                    self.board[row][col] = {"color": "white", "king": False}
                    self.draw_piece(row, col, "white")

    def draw_piece(self, row, col, color, king=False):
        x1 = col * self.square_size + 10
        y1 = row * self.square_size + 10
        x2 = x1 + self.square_size - 20
        y2 = y1 + self.square_size - 20
        self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black", tags="piece")
        if king:
            self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="♔", font=("Arial", 20), fill="gold")

    def handle_click(self, event):
        col = event.x // self.square_size
        row = event.y // self.square_size

        if self.selected_piece:
            self.move_piece(self.selected_piece[0], self.selected_piece[1], row, col)
        elif self.board[row][col] and self.board[row][col]["color"] == self.turn:
            self.selected_piece = (row, col)

    def move_piece(self, start_row, start_col, end_row, end_col):
        if self.is_valid_move(start_row, start_col, end_row, end_col):
            # Captura de peça adversária
            if abs(start_row - end_row) > 1:
                row_step = 1 if end_row > start_row else -1
                col_step = 1 if end_col > start_col else -1
                row, col = start_row + row_step, start_col + col_step
                while row != end_row and col != end_col:
                    if self.board[row][col]:
                        self.board[row][col] = None  # Remove a peça capturada
                        break
                    row += row_step
                    col += col_step

            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = None

            # Promove a peça a "dama" se alcançar o outro lado do tabuleiro
            if (self.turn == "white" and end_row == 0) or (self.turn == "black" and end_row == self.board_size - 1):
                self.board[end_row][end_col]["king"] = True

            self.draw_board()
            self.update_pieces()
            self.selected_piece = None

            if self.check_game_over():
                return

            self.switch_turn()
        else:
            self.selected_piece = None

    def switch_turn(self):
        if self.turn == "white":
            self.turn = "black"
            self.turn_label.config(text="Vez de: Preto", fg="black")
        else:
            self.turn = "white"
            self.turn_label.config(text="Vez de: Branco", fg="blue")

        if self.player_vs_ai and self.turn == "black":
            self.ai_move()

    def is_valid_move(self, start_row, start_col, end_row, end_col):
        piece = self.board[start_row][start_col]
        if not piece or piece["color"] != self.turn:
            return False

        if (end_row + end_col) % 2 == 0 or self.board[end_row][end_col] is not None:
            return False

        row_diff = end_row - start_row
        col_diff = end_col - start_col

        if piece["king"]:
            return abs(row_diff) == abs(col_diff) and self.check_king_capture_path(start_row, start_col, end_row, end_col)
        else:
            # Movimentos normais para peças não-reis
            direction = -1 if self.turn == "white" else 1
            if row_diff == direction and abs(col_diff) == 1:
                return True
            if row_diff == 2 * direction and abs(col_diff) == 2:
                return self.check_capture(start_row, start_col, end_row, end_col)

        return False

    def check_king_capture_path(self, start_row, start_col, end_row, end_col):
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        captured = False
        row, col = start_row + row_step, start_col + col_step
        while row != end_row and col != end_col:
            if self.board[row][col]:
                if captured or self.board[row][col]["color"] == self.turn:
                    return False
                captured = True
            row += row_step
            col += col_step
        return True

    def check_capture(self, start_row, start_col, end_row, end_col):
        mid_row = (start_row + end_row) // 2
        mid_col = (start_col + end_col) // 2
        return self.board[mid_row][mid_col] and self.board[mid_row][mid_col]["color"] != self.turn

    def update_pieces(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col]:
                    self.draw_piece(row, col, self.board[row][col]["color"], self.board[row][col]["king"])

    def check_game_over(self):
        white_pieces = sum(1 for row in self.board for piece in row if piece and piece["color"] == "white")
        black_pieces = sum(1 for row in self.board for piece in row if piece and piece["color"] == "black")

        if white_pieces == 0:
            messagebox.showinfo("Fim de Jogo", "Preto venceu!")
            self.reset_game()
            return True
        elif black_pieces == 0:
            messagebox.showinfo("Fim de Jogo", "Branco venceu!")
            self.reset_game()
            return True

        return False

    def ai_move(self):
        # IA básica: movimentos aleatórios válidos
        possible_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] and self.board[row][col]["color"] == "black":
                    for d_row in [-1, 1]:
                        for d_col in [-1, 1]:
                            for step in range(1, self.board_size):
                                new_row, new_col = row + step * d_row, col + step * d_col
                                if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
                                    if self.is_valid_move(row, col, new_row, new_col):
                                        possible_moves.append((row, col, new_row, new_col))

        if possible_moves:
            move = random.choice(possible_moves)
            self.move_piece(move[0], move[1], move[2], move[3])

if __name__ == "__main__":
    root = tk.Tk()
    game = CheckersGame(root)
    root.mainloop()
