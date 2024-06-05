import tkinter as tk
from tkinter import messagebox
from queue import PriorityQueue
from PIL import Image, ImageTk
import random
# import pygame  # Import the pygame library



class Puzzle:
    def  __init__(self, board, parent=None, move="Initial"):
        self.board = board
        self.goal = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.parent = parent
        self.move = move
        if self.parent:
            self.depth = self.parent.depth + 10
        else:
            self.depth = 0

    def is_goal(self):
        return self.board == self.goal

    def __eq__(self, other):
        return self.board == other.board

    def __lt__(self, other):
        return self.heuristic() < other.heuristic()

    def heuristic(self):
        h = 0
        for i in range(9):
            if self.board[i] != self.goal[i]:
                h += 1
        return h + self.depth

    def get_neighbors(self):
        neighbors = []
        blank_index = self.board.index(0)
        possible_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in possible_moves:
            x = blank_index // 3 + dx
            y = blank_index % 3 + dy
            if 0 <= x < 3 and 0 <= y < 3:
                new_board = self.board[:]
                new_blank_index = x * 3 + y
                new_board[blank_index], new_board[new_blank_index] = new_board[new_blank_index], new_board[blank_index]
                move = f"Move {new_board[blank_index]} {self.move}"
                neighbors.append(Puzzle(new_board, self, move))
        return neighbors

def solve_puzzle(puzzle):
    visited = set()
    pq = PriorityQueue()
    pq.put(puzzle)

    while not pq.empty():
        current_puzzle = pq.get()
        if current_puzzle.is_goal():
            return reconstruct_path(current_puzzle)
        visited.add(tuple(current_puzzle.board))

        for neighbor in current_puzzle.get_neighbors():
            if tuple(neighbor.board) not in visited:
                pq.put(neighbor)

    return None

def reconstruct_path(puzzle):
    path = []
    while puzzle is not None:
        path.insert(0, puzzle.board)
        puzzle = puzzle.parent
    return path

def shuffle_board(board):
    # Shuffle the board by performing random moves
    shuffled_board = board.copy()
    for _ in range(100):
        possible_moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        blank_index = shuffled_board.index(0)
        dx, dy = random.choice(possible_moves)
        x = blank_index // 3 + dx
        y = blank_index % 3 + dy
        if 0 <= x < 3 and 0 <= y < 3:
            new_blank_index = x * 3 + y
            shuffled_board[blank_index], shuffled_board[new_blank_index] = shuffled_board[new_blank_index], shuffled_board[blank_index]
    return shuffled_board

class PuzzleApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Image Puzzle Solver")

        self.image = Image.open(image_path)
        self.image = self.image.resize((300, 300))
        self.image_tiles = self.split_image_into_tiles(self.image)  #returned the list of tiles
        self.puzzle = Puzzle(list(range(9)), move="Initial")  #sets up the starting configuration of the puzzle for the user to interact with and solve.
        self.bg_colors = [['#FFFFFF', '#FFFFFF', '#FFFFFF'], ['#FFFFFF', '#FFFFFF', '#FFFFFF'], ['#FFFFFF', '#FFFFFF', '#FFFFFF']]

        self.tiles = []
        for i in range(3):
            row = []
            for j in range(3):
                img_tile = ImageTk.PhotoImage(self.image_tiles[i * 3 + j])
                tile = tk.Button(root, image=img_tile)
                tile.image = img_tile
                tile.grid(row=i, column=j)
                tile.config(command=lambda tile=tile: self.tile_click(tile))
                row.append(tile)
            self.tiles.append(row)
        for i in range(3):
            spacer_label = tk.Label(root, text="   ", font=('Helvetica', 24))
            spacer_label.grid(row=i, column=3)
                
        self.goal_image = Image.open(image_path)  # Load the goal image
        self.goal_image = self.goal_image.resize((300, 300))
        self.goal_image_tiles = self.split_image_into_tiles(self.goal_image)
        
        self.goal_tiles = []  # Tiles for the goal state
        for i in range(3):
            row = []
            for j in range(3):
                img_tile = ImageTk.PhotoImage(self.goal_image_tiles[i * 3 + j])
                tile = tk.Button(root, image=img_tile)
                tile.image = img_tile
                tile.grid(row=i, column=j + 4)  # Place the goal tiles to the right of the puzzle
                row.append(tile)
            self.goal_tiles.append(row)

        self.special_tile_pos = (0, 0)
        self.solve_button = tk.Button(root, text="AI Help", font=('Helvetica', 18), command=self.solve)
        self.solve_button.grid(row=3, column=0, columnspan=3)
        self.shuffle_button = tk.Button(root, text="Shuffle", font=('Helvetica', 18), command=self.shuffle)
        self.shuffle_button.grid(row=4, column=0, columnspan=3)
        self.unclickable_button = tk.Button(root, text="GOAL", font=('Helvetica', 18), state="disabled")
        self.unclickable_button.grid(row=3, column=5)
              
        self.goal_reached = False  # Flag to track if the goal has been reached
    
    def split_image_into_tiles(self, image):
        tile_width = image.width // 3      #floor division operator
        tile_height = image.height // 3   #dim are integers and not floating nos
        tiles = []
        for i in range(3):
            for j in range(3):                 #left,up,right,low are the coordinates of rectangle that define tile within a image
                left = j * tile_width
                upper = i * tile_height
                right = left + tile_width
                lower = upper + tile_height
                tile = image.crop((left, upper, right, lower)) #extract a rectangular region corresponding to a single tile.
                tiles.append(tile)   #resulting tile added to tiles list
        return tiles    #return list of tiles
    
    
    
    def shuffle(self):
        # Shuffle the puzzle and update the UI
        shuffled_board = shuffle_board(self.puzzle.board)
        self.puzzle.board = shuffled_board
        self.update_ui()
        
        
    def tile_click(self, tile):
        for i in range(3):
            for j in range(3):
                if self.tiles[i][j] == tile:
                    blank_row, blank_col = self.puzzle.board.index(0) // 3, self.puzzle.board.index(0) % 3
                    if abs(i - blank_row) + abs(j - blank_col) == 1:
                        self.puzzle.board[i * 3 + j], self.puzzle.board[blank_row * 3 + blank_col] = self.puzzle.board[blank_row * 3 + blank_col], self.puzzle.board[i * 3 + j]
                        self.puzzle.move = f"Move {self.puzzle.board[i * 3 + j]} {self.puzzle.move}"
                        self.update_background_colors(i, j, blank_row, blank_col)
                        self.update_ui()
                        return
    
    def update_background_colors(self, i, j, blank_row, blank_col):
        # Swap the background color of the clicked tile with the blank tile
        self.bg_colors[i][j], self.bg_colors[blank_row][blank_col] = self.bg_colors[blank_row][blank_col], self.bg_colors[i][j]

    def update_ui(self):
        for i in range(3):
            for j in range(3):
                value = self.puzzle.board[i * 3 + j]
                img_tile = ImageTk.PhotoImage(self.image_tiles[value])
                self.tiles[i][j].config(image=img_tile, bg=self.bg_colors[i][j])
                self.tiles[i][j].image = img_tile

    def animate_solution(self, path, index=0):
     if index < len(path):
        board = path[index]
        self.puzzle.board = board
        self.update_ui()
        self.update_special_tile_color()
        self.root.after(500, self.animate_solution, path, index + 1)

    
    def update_special_tile_color(self):
        # Get the current position of the blank tile
        blank_row, blank_col = self.puzzle.board.index(0) // 3, self.puzzle.board.index(0) % 3
        # Check if the special tile has changed its position
        if blank_row != self.special_tile_pos[0] or blank_col != self.special_tile_pos[1]:
            # Swap the background color of the special tile with the previous blank tile
             self.tiles[self.special_tile_pos[0]][self.special_tile_pos[1]].config(bg='#FFFFFF')
            # Set the background color of the current special tile
             self.tiles[blank_row][blank_col].config(bg='#FFFFFF')
            # Update the position of the special tile
             self.special_tile_pos = (blank_row, blank_col)
             
    def solve(self):
        self.puzzle.parent = None                              # making current state as a starting state to reach goal
        path = solve_puzzle(self.puzzle)                       #implementation of A* algorithm 
        if path:
            self.animate_solution(path)
        else:
            messagebox.showinfo("No Solution", "There is no solution to this puzzle.")             



if __name__ == "__main__":
    root = tk.Tk()
    image_path = r"C:/Users/Shradha_PC/OneDrive/Pictures/narutoimg.png" # Provide the path to your image
    app = PuzzleApp(root, image_path)
    root.mainloop()
