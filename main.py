from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class Square():
    def __init__(self):
        self.row = None
        self.column = None
        self.box = None
        self.possible_solutions = []
        self.solution = None

# Rows will range in value from 0-8
# Columns will range in value from 0-8
# Boxes will range in value from 0-8

# Possible square solutions will depend on other squares in the same column, row, and box

# Generate puzzle by scraping NYT sudoku puzzle
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://www.nytimes.com/puzzles/sudoku/easy")

squares = []

# Wait for page load
try:
    puzzle = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "su-board")))
finally:
    # Get squares
    cells = puzzle.find_elements(By.CLASS_NAME, "su-cell")

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
        sq.possible_solutions.append(int(cell.accessible_name))

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
    
