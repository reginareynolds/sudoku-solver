from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class Puzzle():
    def __init__(self):
        self.rows = {}
        self.columns = {}
        self.boxes = {}

class Square():
    def __init__(self):
        self.row = None
        self.column = None
        self.box = None
        self.possible_solutions = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.solution = None

# Rows will range in value from 0-8
# Columns will range in value from 0-8
# Boxes will range in value from 0-8

# Possible square solutions will depend on other squares in the same column, row, and box

# Generate puzzle by scraping NYT sudoku puzzle
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.nytimes.com/puzzles/sudoku/easy")

squares = []
solved = []  # List of solved cells

# Wait for page load
try:
    page = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "su-board")))
finally:
    # Get squares
    cells = page.find_elements(By.CLASS_NAME, "su-cell")

row = 0
column = 0
box = 0
# Parse puzzle
for cell in cells:
    sq = Square()
    sq.row = row
    sq.column = column
    sq.box = box

    # Find prefilled squares
    if cell.accessible_name != "empty":
        sq.solution = int(cell.accessible_name)
        sq.possible_solutions = int(cell.accessible_name) #.append(int(cell.accessible_name))

        solved.append(sq)

    # Increment location values as necessary
    if not (column+1)%3:
        box = box + 1
    if column<8:
        column = column + 1
    else:
        column = 0
        row = row + 1

        if row%3:
            box = box-3

    squares.append(sq)

# Create text representation of puzzle
with open("puzzle.txt", "w") as file:
    x = 0
    for square in squares:
        if(square.solution):
            file.write(str(square.solution))
        else:
            file.write("x")
        
        if square.column == 8:
            if square.row < 8:
                file.write("\n")

puzzle = Puzzle()

loop = 0
# Add squares to puzzle class
while loop < 9:
    row = []
    column = []
    box = []
    for square in squares:
        if square.row == loop:
            row.append(square)

        if square.column == loop:
            column.append(square)

        if square.box == loop:
            box.append(square)

    puzzle.rows[str(loop)] = row
    puzzle.columns[str(loop)] = column
    puzzle.boxes[str(loop)] = box

    loop = loop + 1
# Remove solved cell values from potential solutions of cells in the same row/column/box
for cell in solved:
    # Same row
    for square in puzzle.rows[str(cell.row)]:
        # Ignore solved squares
        if not square.solution:
            try:
                square.possible_solutions.remove(cell.solution)
            # ValueError means cell.solution was already removed
            except ValueError:
                pass
            finally:
                # Add newly solved squares to solved square list
                if len(square.possible_solutions) == 1:
                    square.solution = int(square.possible_solutions[0])
                    square.possible_solutions = int(square.possible_solutions[0])
                    solved.append(square)

    # Same column
    for square in puzzle.columns[str(cell.column)]:
        # Ignore solved squares
        if not square.solution:
            try:
                square.possible_solutions.remove(cell.solution)
            # ValueError means cell.solution was already removed
            except ValueError:
                pass
            finally:
                # Add newly solved squares to solved square list
                if len(square.possible_solutions) == 1:
                    square.solution = int(square.possible_solutions[0])
                    square.possible_solutions = int(square.possible_solutions[0])
                    solved.append(square)

    # Same box
    for square in puzzle.boxes[str(cell.box)]:
        # Ignore solved squares
        if not square.solution:
            try:
                square.possible_solutions.remove(cell.solution)
            # ValueError means cell.solution was already removed
            except ValueError:
                pass
            finally:
                # Add newly solved squares to solved square list
                if len(square.possible_solutions) == 1:
                    square.solution = int(square.possible_solutions[0])
                    square.possible_solutions = int(square.possible_solutions[0])
                    solved.append(square)

