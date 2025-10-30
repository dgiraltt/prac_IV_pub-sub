import logging
import random


class TicTacToe:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.symbol = "X" if name == "agent1" else "O"


    def print_board(self):
        self.logger.info("-" * 5)
        for row in self.board:
            self.logger.info("|".join(row))
        self.logger.info("-" * 5)


    def make_move(self, row, col):
        if self.board[row][col] == " ":
            self.board[row][col] = self.symbol
            return True
        return False


    def check_win(self):
        # Check rows
        for row in self.board:
            if row.count(row[0]) == 3 and row[0] != " ":
                return True

        # Check columns
        for col in range(3):
            if (self.board[0][col] == self.board[1][col] == self.board[2][col]) and self.board[0][col] != " ":
                return True

        # Check diagonals
        if (self.board[0][0] == self.board[1][1] == self.board[2][2]) and self.board[0][0] != " ":
            return True
        if (self.board[0][2] == self.board[1][1] == self.board[2][0]) and self.board[0][2] != " ":
            return True

        return False


    def check_draw(self):
        return all(cell != " " for row in self.board for cell in row)


    def random_move(self):
        while True:
            row = random.randint(0, 2)
            col = random.randint(0, 2)
            if self.board[row][col] == " ":
                return row, col
