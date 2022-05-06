from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
# from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.widget import Widget


# GENERAL PROGRAM OVERVIEW
# 1. Scrape sudoku puzzle from New York Times
# 2. Parse scraped puzzle
# 3. Create visual puzzle representation
# 4. Solve for missing squares and update visual puzzle representation

# Rows will range in value from 0-8
# Columns will range in value from 0-8
# Boxes will range in value from 0-8

# Possible square solutions will depend on other squares in the same row, column, and box
# Solved cells remove their solution as a possibility from unsolved cells in the same row/column/box
# If a cell has only one possible solution, that must be the solution for that cell.
# If an unsolved value in a group (row, column, box) has only one possible group cell it can appear in, it must appear in that cell.
# If the puzzle is still not solved at that point, further processing is necessary.

# Scrape sudoku puzzle from New York Times site
def scrape_puzzle(puzzle_squares, solved_cells):
    # Prevent browser window from showing
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Generate puzzle by scraping NYT sudoku puzzle
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    driver.get("https://www.nytimes.com/puzzles/sudoku/hard")

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

            solved_cells.append(sq)

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
        puzzle_squares.append(sq)

    # Close selenium
    driver.close()

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

                    puzzle.rows[str(square.row)]["unsolved"].pop(str(square.solution), None)
                    puzzle.columns[str(square.column)]["unsolved"].pop(str(square.solution), None)
                    puzzle.boxes[str(square.box)]["unsolved"].pop(str(square.solution), None)
                    solved_list.append(square)

def refine_solutions(grouping, index, comparison):
    for cell in grouping[str(index)]["squares"]:
        # Ignore solved cells
        if not cell.solution:
            if comparison in cell.possible_solutions:
                cell.possible_solutions.remove(comparison)

# Find unsolved group values 
def find_unsolved(grouping, solved_list, box_group = False):
    for key, group in grouping.items():
        # What cells can contain each unsolved value?

        # num is an unsolved integer value represented as a string
        # frequency is the list of cells within the group that may contain num
        for num, frequency in group["unsolved"].items():
            for square in group["squares"]:
                # Only append square if value is possible solution and not already added
                if not square.solution and int(num) in square.possible_solutions:
                    if square not in frequency:
                        frequency.append(square)

                # Remove square if previously added and: 
                # A) value no longer possible solution or 
                # B) since solved
                elif square in frequency:
                    frequency.remove(square)

            # Only one cell can contain the unsolved value            
            if len(frequency) == 1:
                frequency[0].solution = int(num)
                frequency[0].possible_solutions = int(num)
                solved_list.append(frequency[0])

                refine_solutions(puzzle.rows, frequency[0].row, frequency[0].solution)

                refine_solutions(puzzle.columns, frequency[0].column, frequency[0].solution)

                refine_solutions(puzzle.boxes, frequency[0].box, frequency[0].solution)

            else:
                # If numbers A and B can only go in squares C and D of a grouping, no 
                # other squares in the grouping can have A or B as possible solutions.
                # More generally, when the same possible numbers can appear in the same 
                # potential cells, you know those numbers CAN'T appear anywhere else in the 
                # row/box/column.
                # Example:
                #             1 A 7
                # 6 X 2 X X X B C 8
                #             3 5 D
                # In the above example, the box containing squares squares A-D is missing a 
                # 4. Without any 4s in intersecting rows/columns, the 4 in this box seems to
                # be a potential solution for all of the squares A-D. However, this box is also
                # missing 2, 6, and 9. The row intersecting squares B and C already has a 2
                # and a 6. This means that squares B and C CANNOT contain 2 or 6, so they MUST 
                # contain 4 or 9. This means squares C and D CANNOT contain 4 or 9 and instead
                # MUST contain 2 or 6.                

                # Find unsolved values that share the same potential containing cells
                indices = [int(num)]
                for nnum, nfrequency in group["unsolved"].items():
                    if num != nnum:
                        if frequency == nfrequency:
                            indices.append(int(nnum))

                # Compare number of unsolved values against number of potential containing cells
                # i.e. if 1, 2, and 3 can each go in cells A, B, or C, then no other cells in
                # the grouping can contain 1, 2, or 3. The number of unsolved values must be equal
                # to the number of potential containing cells.
                if len(indices) == len(frequency):
                    for sq in frequency:
                        to_remove = []                
                        for sol in sq.possible_solutions:
                            if sol not in indices:
                                to_remove.append(sol)
                        for index in to_remove:
                            sq.possible_solutions.remove(index)

                # TODO: Immediately remove solution from possible solutions of groupmates
                # TODO: Remove unsolved value from unsolved value list. Will this cause a conflict by skipping over a dictionary value?
            if box_group:
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

# Consists of 9 rows, 9 columns, and 9 boxes, each of which contains 9 Square objects
class Puzzle():
    def __init__(self):
        self.rows = {}
        self.columns = {}
        self.boxes = {}

    # Add squares to puzzle class
    def create(self, puzzle_squares):
        loop = 0
        while loop < 9:
            row = {"squares": [], "unsolved": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": []}}
            column = {"squares": [], "unsolved": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": []}}
            box = {"squares": [], "unsolved": {"1": [], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": [], "9": []}}
            for square in puzzle_squares:
                if square.row == loop:
                    row["squares"].append(square)

                if square.column == loop:
                    column["squares"].append(square)

                if square.box == loop:
                    box["squares"].append(square)

            self.rows[str(loop)] = row
            self.columns[str(loop)] = column
            self.boxes[str(loop)] = box

            loop = loop + 1

        # Create puzzle text file
        file_create("puzzle.txt", puzzle_squares)

# Contains the row, column, and box in which the object is located, the potential solutions to the box, and the final solution once solved
class Square(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ID = None
        self.row = None
        self.column = None
        self.box = None
        self.possible_solutions = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.solution = None

class Screen(Widget):
    board = ObjectProperty(None)

    # Create initial visual puzzle representation
    def create_board(self):
        for key, cells in reversed(puzzle.boxes.items()):
            for cell in cells['squares']:
                if cell.solution != None:
                    cell.text=str(cell.solution)
                self.board.children[abs(int(key)-8)].add_widget(cell)

    def update(self, dt):
        # Check for if puzzle is solved
        if len(solved) < 81:        
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

            # Create puzzle solution text file
            file_create("solution.txt", squares)

            for key, cells in reversed(puzzle.boxes.items()):
                for cell in cells['squares']:
                    if cell.solution != None:
                        cell.text=str(cell.solution)

class SudokuApp(App):
    def build(self):
        content = Screen()

        # Read puzzle information and add to Puzzle object
        scrape_puzzle(squares, solved)
        puzzle.create(squares)

        # Add scraped puzzle to visual representation
        content.create_board()

        Clock.schedule_interval(content.update, 5.0)
        
        return content

        # TODO: Change square color once it's solved

if __name__ == '__main__':
    # Initialize globals
    squares = []  # List of squares in puzzle
    solved = []  # List of solved cells
    puzzle = Puzzle()  # Puzzle object

    app=SudokuApp()
    app.run()

# If a cell has all but one value in the same row, column, and box, that must be the value of the cell
#       3 6 8
#       E F 1
# 2 A 3 B 7 X 9 C D
#           4
# In the above example, X must be 5, since the box already contains 1, 3, 6, and 7,
# the column contains 4 and 8, and the row contains 2, 3, and 9.
# TODO: Account for when the values of a pair of cells could be either way:
# 1 2 3
# 4 5 6
# 7 A B 1 2 3 4 5 6
#   1 2
#   3 5
#   4 7
# 2 C D 3 4 5 6 7 1
# 3 6 1
# 5 7 4
# In the above example, A and B can both be 8 or 9, and C and D can both be 8 or 9. 