from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Consists of 9 rows, 9 columns, and 9 boxes, each of which contains 9 Square objects
class Puzzle():
    def __init__(self):
        self.rows = {}
        self.columns = {}
        self.boxes = {}

# Contains the row, column, and box in which the object is located, the potential solutions to the box, and the final solution once solved
class Square():
    def __init__(self):
        self.ID = None
        self.row = None
        self.column = None
        self.box = None
        self.possible_solutions = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.solution = None

# Create text representation of puzzle/solution and write to passed file
def file_create(filename, cells):
    with open(filename, "w") as file:
        for cell in cells:
            if(cell.solution):
                file.write(str(cell.solution))
            else:
                file.write("x")
            
            if cell.column == 8:
                if cell.row < 8:
                    file.write("\n")

# Remove solved cell values from potential solutions of cells in same grouping
def remove_same(grouping, index, solution, solved_list):
    # Remove solved cell values from grouping's unsolved value list
    grouping[str(index)]["unsolved"].pop(str(solution), None)
    
    for square in grouping[str(index)]["squares"]:
        # Ignore solved squares
        if not square.solution:
            # Remove solved cell values from square's potential value list
            try:
                square.possible_solutions.remove(solution)
            # ValueError means solution was already removed
            except ValueError:
                pass
            finally:
                # Add newly solved squares to solved square list
                if len(square.possible_solutions) == 1:
                    square.solution = int(square.possible_solutions[0])
                    square.possible_solutions = int(square.possible_solutions[0])
                    solved_list.append(square)

# Find unsolved group values 
def find_unsolved(grouping, solved_list, box_group = False):
    for key, group in grouping.items():
        # What cells can contain each unsolved value?
        for num, frequency in group["unsolved"].items():
            for square in group["squares"]:
                if not square.solution:
                    if int(num) in square.possible_solutions:
                        frequency.append(square)
                        # TODO: Fix repeatedly adding same squares on each function run
            # Only one cell can contain the unsolved value            
            if len(frequency) == 1:
                frequency[0].solution = int(num)
                frequency[0].possible_solutions = int(num)
                solved_list.append(frequency[0])

                # TODO: Remove unsolved value from unsolved value list. Will this cause a conflict by skipping over a dictionary value?
            elif box_group:
                # When you know the row or column within a box where a number must appear,
                # you know that number CAN'T appear on that row or column in neighboring boxes
                # Example:
                #                 2      
                #             5 7 X
                # A B C D E F X X X
                #             8 3 9
                # The 2 in this bottom box MUST appear below the 5 or 7
                # This means that 2 CANNOT appear anywhere else in the rest 
                # of the row, i.e., spots A-F. Therefore, 2 must be removed
                # as a possible solution for cells A-F.

                rows = []
                cols = []
                for cell in frequency:
                    if cell.row not in rows:
                        rows.append(cell.row)

                    if cell.column not in cols:
                        cols.append(cell.column)

                # Value for this row MUST appear in this box 
                if len(rows) == 1:
                    for cell in puzzle.rows[str(rows[0])]["squares"]:
                        # Ignore solved cells
                        if not cell.solution:
                            if cell.box != int(key) and int(num) in cell.possible_solutions:
                                cell.possible_solutions.remove(int(num))
                
                # Value for this column MUST appear in this box                 
                if len(cols) == 1:
                    for cell in puzzle.columns[str(cols[0])]["squares"]:
                        # Ignore solved cells
                        if not cell.solution:
                            if cell.box != int(key) and int(num) in cell.possible_solutions:
                                cell.possible_solutions.remove(int(num))


# Rows will range in value from 0-8
# Columns will range in value from 0-8
# Boxes will range in value from 0-8

# Possible square solutions will depend on other squares in the same row, column, and box
# Solved cells remove their solution as a possibility from unsolved cells in the same row/column/box
# If a cell has only one possible solution, that must be the solution for that cell.
# If an unsolved value in a group (row, column, box) has only one possible group cell it can appear in, it must appear in that cell.
# If the puzzle is still not solved at that point, further processing is necessary.

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

number = 0
row = 0
column = 0
box = 0
# Parse puzzle
for cell in cells:
    sq = Square()
    sq.ID = number
    sq.row = row
    sq.column = column
    sq.box = box

    # Find prefilled squares
    if cell.accessible_name != "empty":
        sq.solution = int(cell.accessible_name)
        sq.possible_solutions = int(cell.accessible_name)

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

    number = number + 1
    squares.append(sq)

# Create puzzle text file
file_create("puzzle.txt", squares)

# Add squares to puzzle class
puzzle = Puzzle()
loop = 0
while loop < 9:
    row = {"squares": [], "unsolved": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": []}}
    column = {"squares": [], "unsolved": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": []}}
    box = {"squares": [], "unsolved": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": []}}
    for square in squares:
        if square.row == loop:
            row["squares"].append(square)

        if square.column == loop:
            column["squares"].append(square)

        if square.box == loop:
            box["squares"].append(square)

    puzzle.rows[str(loop)] = row
    puzzle.columns[str(loop)] = column
    puzzle.boxes[str(loop)] = box

    loop = loop + 1

# Check for if puzzle is solved
while len(solved) < 81:
    # Remove solved cell values from potential solutions of cells in the same row/column/box
    for cell in solved:
        # Same row
        remove_same(puzzle.rows, cell.row, cell.solution, solved)

        # Same column
        remove_same(puzzle.columns, cell.column, cell.solution, solved)

        # Same box
        remove_same(puzzle.boxes, cell.box, cell.solution, solved)

    # Further processing is required
    
    # Find unsolved row values 
    find_unsolved(puzzle.rows, solved)

    # Find unsolved column values
    find_unsolved(puzzle.columns, solved)  

    # Find unsolved box values
    find_unsolved(puzzle.boxes, solved, box_group = True)

        for num, frequency in occurences.items():
            if len(frequency) == 1:
                frequency[0].solution = int(num)
                frequency[0].possible_solutions = int(num)
                solved.append(frequency[0])  

# Create puzzle solution text file
file_create("solution.txt", squares)

# Create puzzle solution text file
file_create("solution.txt", squares)