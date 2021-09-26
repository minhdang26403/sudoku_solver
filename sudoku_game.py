import pygame
import time
pygame.init()
font = pygame.font.SysFont('Monospace', 32)


class Cell:
    def __init__(self, number):
        self.number = number
        self.editable = number == 0
        self.valid = True
        self.selected = False
        self.under_consideration = False


class SudokuGUI:
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREY = (105, 105, 105)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 180, 255)
    WIDTH = 9*79 + 6*1 + 2*3
    cell_centers = [40, 120, 200, 282, 362, 442, 524, 604, 684]

    def __init__(self):
        self.screen = pygame.display.set_mode((self.WIDTH, self.WIDTH))
        pygame.display.set_caption('Sudoku')
        self.selected_cell = None
        self.board = self.get_board()

    def get_board(self):
        return [
            [
                Cell(0), Cell(0), Cell(9),
                Cell(2), Cell(1), Cell(8),
                Cell(0), Cell(0), Cell(0)
            ],
            [
                Cell(1), Cell(7), Cell(0),
                Cell(0), Cell(9), Cell(6),
                Cell(8), Cell(0), Cell(0)
            ],
            [
                Cell(0), Cell(4), Cell(0),
                Cell(0), Cell(5), Cell(0),
                Cell(0), Cell(0), Cell(6)
            ],
            [
                Cell(4), Cell(5), Cell(1),
                Cell(0), Cell(6), Cell(0),
                Cell(3), Cell(7), Cell(0)
            ],
            [
                Cell(0), Cell(0), Cell(0),
                Cell(0), Cell(0), Cell(5),
                Cell(0), Cell(0), Cell(9)
            ],
            [
                Cell(9), Cell(0), Cell(2),
                Cell(3), Cell(7), Cell(0),
                Cell(5), Cell(0), Cell(0)
            ],
            [
                Cell(6), Cell(0), Cell(0),
                Cell(5), Cell(0), Cell(1),
                Cell(0), Cell(0), Cell(0)
            ],
            [
                Cell(0), Cell(0), Cell(0),
                Cell(0), Cell(4), Cell(9),
                Cell(2), Cell(5), Cell(7)
            ],
            [
                Cell(0), Cell(9), Cell(4),
                Cell(8), Cell(0), Cell(0),
                Cell(0), Cell(1), Cell(3)
            ]
        ]

    def draw_board(self):
        self.validate_board()
        self.draw_lines()
        self.draw_numbers()
        pygame.display.flip()

    def validate_board(self):
        for row in range(9):
            for col in range(9):
                cell = self.board[row][col]
                if cell.number == 0:
                    cell.valid = True
                else:
                    cell.valid = self.is_valid(cell.number, row, col)

    def draw_lines(self):
        self.screen.fill(self.WHITE)
        x = 80
        for i in range(1, 10):
            self.draw_line((x, 0), (x, self.WIDTH), self.BLACK)
            self.draw_line((0, x), (self.WIDTH, x), self.BLACK)
            if i % 3 == 0:
                x += 1
                self.draw_line((x, 0), (x, self.WIDTH), self.BLACK)
                self.draw_line((0, x), (self.WIDTH, x), self.BLACK)
                x += 1
                self.draw_line((x, 0), (x, self.WIDTH), self.BLACK)
                self.draw_line((0, x), (self.WIDTH, x), self.BLACK)
            x += 80

    def draw_line(self, start, end, color):
        pygame.draw.line(self.screen, color, start, end)

    def draw_numbers(self):
        for row in range(9):
            for col in range(9):
                cell = self.board[row][col]
                if cell.number != 0:
                    color = self.GREY if cell.editable else self.BLACK
                    self.draw_number(cell.number, row, col, color)
                if cell.under_consideration:
                    self.color_border(row, col, self.GREEN)
                elif not cell.valid:
                    self.color_border(row, col, self.RED)
                elif cell.selected:
                    self.color_border(row, col, self.BLUE)

    def draw_number(self, number, row, col, color):
        text = font.render(str(number), True, color, self.WHITE)
        text_rect = text.get_rect()

        row_center = self.cell_centers[row]
        col_center = self.cell_centers[col]

        text_rect.center = (col_center, row_center)

        self.screen.blit(text, text_rect)

    def color_border(self, row, col, color):
        row_center = self.cell_centers[row]
        col_center = self.cell_centers[col]

        self.draw_line((col_center - 40, row_center - 40), (col_center + 40, row_center - 40), color)
        self.draw_line((col_center - 40, row_center + 40), (col_center + 40, row_center + 40), color)
        self.draw_line((col_center - 40, row_center - 40), (col_center - 40, row_center + 40), color)
        self.draw_line((col_center + 40, row_center - 40), (col_center + 40, row_center + 40), color)

    def set_selected_cell(self, mouse_position):
        clicked_col = self.get_cell(mouse_position[0])
        clicked_row = self.get_cell(mouse_position[1])
        if self.selected_cell is not None:
            row, col = self.selected_cell
            self.board[row][col].selected = False
        self.selected_cell = (clicked_row, clicked_col)
        self.board[clicked_row][clicked_col].selected = True

    def get_cell(self, coordinate):
        for idx, center in enumerate(self.cell_centers):
            if center - 40 < coordinate < center + 40:
                return idx
        return -1

    def set_number(self, number):
        if self.selected_cell is None:
            return

        row, col = self.selected_cell
        cell = self.board[row][col]

        if cell.editable:
            cell.number = number

    def delete(self):
        if self.selected_cell is None:
            return
        self.set_number(0)

    def move_selected_cell(self, row_move, col_move):
        if self.selected_cell is None:
            return
        old_row, old_col = self.selected_cell
        new_row = old_row + row_move
        new_col = old_col + col_move

        if -1 < new_row < 9 and -1 < new_col < 9:
            self.selected_cell = (new_row, new_col)
            self.board[old_row][old_col].selected = False
            self.board[new_row][new_col].selected = True

    def solve_sudoku(self):
        self.board = self.get_board()
        self.solve_sudoku_helper(0, 0)

    def solve_sudoku_helper(self, row, col):
        last_row = len(self.board) - 1
        last_col = len(self.board[row]) - 1
        current_cell = self.board[row][col]

        if current_cell.number != 0:
            if col == last_col and row == last_row:
                return True
            elif col == last_col:
                return self.solve_sudoku_helper(row + 1, 0)
            else:
                return self.solve_sudoku_helper(row, col + 1)
        current_cell.under_consideration = True

        for candidate in range(1, 10):
            current_cell.number = candidate
            self.draw_board()
            time.sleep(0.02)
            if self.is_valid(candidate, row, col):
                if col == last_col and row == last_row:
                    current_cell.under_consideration = False
                    return True
                if col == last_col:
                    current_cell.under_consideration = False
                    result = self.solve_sudoku_helper(row + 1, 0)
                else:
                    current_cell.under_consideration = False
                    result = self.solve_sudoku_helper(row, col + 1)
                if result:
                    current_cell.under_consideration = False
                    return True
            current_cell.under_consideration = True
            self.draw_board()
            time.sleep(0.02)
            current_cell.number = 0
        current_cell.under_consideration = False
        return False

    def is_valid(self, number, row, col):
        for idx in range(9):
            if self.board[idx][col].number == number and idx != row:
                return False
            if self.board[row][idx].number == number and idx != col:
                return False
        square_row = (row // 3) * 3
        square_col = (col // 3) * 3
        for r in range(square_row, square_row + 3):
            for c in range(square_col, square_col + 3):
                if r == row and c == col:
                    continue
                if self.board[r][c].number == number:
                    return False
        return True


def main():
    sudoku = SudokuGUI()
    sudoku.draw_board()
    ALLOWED_INPUTS = {pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                      pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9}
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in ALLOWED_INPUTS:
                    number = int(chr(event.key))
                    sudoku.set_number(number)
                elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    sudoku.delete()
                elif event.key == pygame.K_UP:
                    sudoku.move_selected_cell(-1, 0)
                elif event.key == pygame.K_DOWN:
                    sudoku.move_selected_cell(1, 0)
                elif event.key == pygame.K_RIGHT:
                    sudoku.move_selected_cell(0, 1)
                elif event.key == pygame.K_LEFT:
                    sudoku.move_selected_cell(0, -1)
                elif event.key == pygame.K_SPACE:
                    sudoku.solve_sudoku()
                sudoku.draw_board()

            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                sudoku.set_selected_cell(pos)
                sudoku.draw_board()

            if event.type == pygame.QUIT:
                run = False
    pygame.quit()


main()