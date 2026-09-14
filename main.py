import tkinter as tk
from tkinter import messagebox

class Solver:
    def __init__(self):
        # Setup root window
        self.root = tk.Tk()
        self.root.title("Sudoku Solver")
        self.center_window()
        # Setup board
        self.board_frame = tk.Frame(self.root)
        self.board_frame.grid(row=0, column=0)
        self.font_size = 33
        self.board = []
        self.setup_board()
        # Setup buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.grid(row=1, column=0)
        self.solve_button = tk.Button(self.button_frame, text="Solve", font=("Calibri", 16), command=self.solve)
        self.solve_button.grid(row=0, column=0)
        self.reset_button = tk.Button(self.button_frame, text="Reset", font=("Calibri", 16), command=self.reset)
        self.reset_button.grid(row=0, column=1)
        # Cell tracking
        self.start_posits = [] # cells with starting values
        self.solved_posits = [] # cells with values solved by algorithm

    def center_window(self):
        """
        Centers the root window using the screen size and window size
        """
        # Screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Window dimensions
        window_width = 486
        window_height = 500
        # (x,y) starts at top left of window (0, 0)
        # x increases moving right, decreases moving left
        # y increases moving down, decreases moving up
        x = screen_width / 2 - window_width / 2  # position top left corner's x at this x
        y = screen_height / 2 - window_height  # position top left corner's y at a smaller y (otherwise window too low)
        self.root.geometry(
            "%dx%d+%d+%d" % (window_width, window_height, x, y))  # Adds x and y offsets to window dimensions
        self.root.resizable(width=False, height=False)  # Prevent window from being resizable

    def setup_board(self):
        """
        Sets up the sudoku board for the solver
        """
        for i in range(9):
            row = []
            for j in range(9):
                cell = tk.Entry(master=self.board_frame, width=2, font=("Calibri", self.font_size), justify="center")
                cell.grid(row=i, column=j)
                row.append(cell)
            self.board.append(row)

    def reset(self):
        """
        Resets everything, including the board
        """
        for i in range(9):
            for j in range(9):
                self.board[i][j].config(state="normal", fg="white")
                self.board[i][j].delete(0, "end")
        self.start_posits = []
        self.solved_posits = []

    def row_has_dupe(self, row, col, num) -> bool:
        """
        Checks if the cell's current value already exists in the cell's row
        :param row: the current row of the cell
        :param col: the current column of the cell
        :param num: the current value of the cell
        :return: True if there is a duplicate in the row, False otherwise
        """
        for i in range(9):
            if i == col: # Skip over current col
                continue
            if self.board[row][i].get() == num: # Row duplicate found
                return True
        return False

    def col_has_dupe(self, row, col, num) -> bool:
        """
        Checks if the cell's current value already exists in the cell's column
        :param row: the current row of the cell
        :param col: the current column of the cell
        :param num: the current value of the cell
        :return: True if there is a duplicate in the column, False otherwise
        """
        for i in range(9):
            if i == row: # Skip over current row
                continue
            if self.board[i][col].get() == num: # Column duplicate found
                return True
        return False

    def grid_has_dupe(self, row, col, num) -> bool:
        """
        Checks if the cell's current value already exists in the cell's grid
        :param row: the current row of the cell
        :param col: the current column of the cell
        :param num: the current value of the cell
        :return: True if there is a duplicate in the grid, False otherwise
        """
        # Starting row and col will always be a multiple of 3 since grids are 3x3
        start_row = 3 * (row // 3)
        start_col = 3 * (col // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if i == row and j == col:
                    continue
                if self.board[i][j].get() == num:
                    return True
        return False

    def cells_valid(self) -> bool:
        """
        Check the validity of each cell's value
        Valid = a number between 1 and 9 inclusive and has no duplicates in row, column, or grid
        :return: True if the cells are all valid, False otherwise
        """
        for i in range(9):
            for j in range(9):
                if self.board[i][j].get() != "": # Come across a cell with a numerical value
                    # Attempt to convert the value into an int, starts out as a string
                    try:
                        num = int(self.board[i][j].get())
                    except ValueError: # Cannot convert string to int
                        return False
                    else:
                        # Resulting int is not between 1 and 9 inclusive or duplicates are found
                        if (not 0 < num < 10 or self.row_has_dupe(i, j, str(num)) or self.col_has_dupe(i, j, str(num))
                                or self.grid_has_dupe(i, j, str(num))):
                            return False
                        else: # Resulting int is a valid number
                            self.start_posits.append((i, j))
                            self.board[i][j].config(state="readonly", readonlybackground="#1e1e1d")
        return True

    def solve(self):
        """
        Solves the given Sudoku puzzle
        """
        if not self.start_posits:
            if self.cells_valid():
                self.root.focus_set()
                self.backtrack()
            else:
                messagebox.showerror(message="ERROR: Cells must have numbers 1-9 or be blank. No row, column, or grid duplicates.")
                self.reset()

    def backtrack(self):
        """
        Utilizes the backtracking/brute force method to solve the Sudoku
        """
        i = 0
        while i < 9: # Until we go past the last row on the board
            j = 0
            while j < 9: # Until we go past the last column in the current row
                valid_found = False
                if (i, j) not in self.start_posits: # Check if the current cell is a starting one (can't change it)
                    start_num = 1
                    if self.board[i][j].get() != "":
                        start_num = int(self.board[i][j].get()) + 1
                    for k in range(start_num, 10): # Cycle through numbers 1-9 for each nonstarting cell
                        k_str = str(k)
                        # Insert number into cell if valid (no row, column, or grid dupes)
                        if k_str != self.board[i][j].get() and not (self.row_has_dupe(i, j, k_str)
                        or self.col_has_dupe(i, j, k_str) or self.grid_has_dupe(i, j, k_str)):
                            self.board[i][j].config(state="normal", fg="white")
                            self.board[i][j].delete(0, "end")
                            self.board[i][j].insert(0, k_str)
                            self.board[i][j].config(state="readonly", fg="red", readonlybackground="#1e1e1d")
                            self.solved_posits.append((i, j))
                            valid_found = True
                            break
                    if not valid_found:
                        self.board[i][j].config(state="normal", fg="white")
                        self.board[i][j].delete(0, "end")
                        i = self.solved_posits[-1][0]
                        j = self.solved_posits[-1][1]
                        self.solved_posits.pop(-1)
                        continue
                j += 1
            i += 1


if __name__ == "__main__":
    solver = Solver()
    solver.root.mainloop()