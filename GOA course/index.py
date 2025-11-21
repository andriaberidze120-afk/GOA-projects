# tetris.py
import pygame
import random
import sys

pygame.init()
pygame.display.set_caption("Tetris")

# ---------- CONFIG ----------
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
SIDE_PANEL = 6 * CELL_SIZE
FPS = 60

SCREEN = pygame.display.set_mode((WIDTH + SIDE_PANEL, HEIGHT))
CLOCK = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
COLORS = [
    (0, 240, 240),   # I - cyan
    (0, 0, 240),     # J - blue
    (240, 160, 0),   # L - orange
    (240, 240, 0),   # O - yellow
    (0, 240, 0),     # S - green
    (160, 0, 240),   # T - purple
    (240, 0, 0)      # Z - red
]

# Tetrimino shapes (clockwise rotation matrices)
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'T': [[0, 1, 0],
          [1, 1, 1]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
}

SHAPE_KEYS = list(SHAPES.keys())

# ---------- UTILITIES ----------
def rotate(shape):
    # rotate clockwise
    return [list(row) for row in zip(*shape[::-1])]

def create_empty_grid():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

def draw_text(surface, text, size, x, y, color=WHITE, center=False):
    font = pygame.font.SysFont('consolas', size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)

# ---------- CLASSES ----------
class Piece:
    def __init__(self, shape_key=None):
        if shape_key is None:
            shape_key = random.choice(SHAPE_KEYS)
        self.key = shape_key
        self.shape = [row[:] for row in SHAPES[self.key]]
        self.color = COLORS[SHAPE_KEYS.index(self.key)]
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self, grid):
        old_shape = self.shape
        new_shape = rotate(self.shape)
        # basic wall-kick: try offset 0, +1, -1, +2, -2
        for dx in (0, 1, -1, 2, -2):
            if not collide(grid, new_shape, self.x + dx, self.y):
                self.shape = new_shape
                self.x += dx
                return True
        return False

def collide(grid, shape, x, y):
    for r, row in enumerate(shape):
        for c, cell in enumerate(row):
            if cell:
                gx = x + c
                gy = y + r
                if gx < 0 or gx >= COLS or gy >= ROWS:
                    return True
                if gy >= 0 and grid[gy][gx] is not None:
                    return True
    return False

def lock_piece(grid, piece):
    for r, row in enumerate(piece.shape):
        for c, cell in enumerate(row):
            if cell:
                gx = piece.x + c
                gy = piece.y + r
                if 0 <= gy < ROWS and 0 <= gx < COLS:
                    grid[gy][gx] = piece.color

def clear_lines(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    cleared = ROWS - len(new_grid)
    for _ in range(cleared):
        new_grid.insert(0, [None for _ in range(COLS)])
    return new_grid, cleared

def draw_grid(surface, grid, offset_x=0, offset_y=0):
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(offset_x + c*CELL_SIZE, offset_y + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, GRAY, rect, 1)
            if grid[r][c] is not None:
                color = grid[r][c]
                inner = rect.inflate(-2, -2)
                pygame.draw.rect(surface, color, inner)

def draw_piece(surface, piece, offset_x=0, offset_y=0, ghost=False):
    for r, row in enumerate(piece.shape):
        for c, cell in enumerate(row):
            if cell:
                x = piece.x + c
                y = piece.y + r
                rect = pygame.Rect(offset_x + x*CELL_SIZE, offset_y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if 0 <= y < ROWS and 0 <= x < COLS:
                    inner = rect.inflate(-2, -2)
                    color = piece.color
                    if ghost:
                        color = tuple(min(255, int(ch * 0.4)) for ch in color)
                    pygame.draw.rect(surface, color, inner)

def get_ghost_y(grid, piece):
    y = piece.y
    while not collide(grid, piece.shape, piece.x, y + 1):
        y += 1
    return y

# ---------- GAME ----------
def new_bag():
    bag = SHAPE_KEYS[:]
    random.shuffle(bag)
    return bag

def draw_side_panel(surface, next_piece, score, level, lines):
    start_x = WIDTH + 10
    draw_text(surface, "NEXT", 20, start_x, 10)
    # draw next piece
    if next_piece:
        px = start_x + CELL_SIZE
        py = 40
        for r, row in enumerate(next_piece.shape):
            for c, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(px + c*CELL_SIZE, py + r*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, next_piece.color, rect.inflate(-2, -2))
    draw_text(surface, f"SCORE: {score}", 20, start_x, 150)
    draw_text(surface, f"LEVEL: {level}", 20, start_x, 190)
    draw_text(surface, f"LINES: {lines}", 20, start_x, 230)
    draw_text(surface, "CONTROLS:", 18, start_x, 280)
    draw_text(surface, "← → move", 16, start_x, 305)
    draw_text(surface, "↓ soft drop", 16, start_x, 325)
    draw_text(surface, "Space hard drop", 16, start_x, 345)
    draw_text(surface, "↑ / X rotate", 16, start_x, 365)
    draw_text(surface, "Z rotate CCW", 16, start_x, 385)
    draw_text(surface, "P pause", 16, start_x, 405)

def main():
    grid = create_empty_grid()

    bag = []
    def next_piece_from_bag():
        nonlocal bag
        if not bag:
            bag = new_bag()
        return Piece(bag.pop())

    current = next_piece_from_bag()
    next_piece = next_piece_from_bag()
    score = 0
    level = 1
    lines_cleared = 0
    fall_speed = 700  # milliseconds per step (lower => faster)
    pygame.time.set_timer(pygame.USEREVENT + 1, fall_speed)
    fast_fall = False
    running = True
    paused = False
    game_over = False

    while running:
        dt = CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if game_over:
                    if event.key == pygame.K_r:
                        # restart
                        return main()
                    continue
                if event.key == pygame.K_p:
                    paused = not paused
                if paused:
                    continue
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    if not collide(grid, current.shape, current.x - 1, current.y):
                        current.x -= 1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if not collide(grid, current.shape, current.x + 1, current.y):
                        current.x += 1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    fast_fall = True
                elif event.key in (pygame.K_UP, pygame.K_x):
                    current.rotate(grid)
                elif event.key == pygame.K_z:
                    # rotate CCW: three CW rotations
                    current.rotate(grid)
                    current.rotate(grid)
                    current.rotate(grid)
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while not collide(grid, current.shape, current.x, current.y + 1):
                        current.y += 1
                    lock_piece(grid, current)
                    grid, cleared = clear_lines(grid)
                    if cleared:
                        lines_cleared += cleared
                        score += (100 * (2 ** (cleared - 1))) * level
                        level = 1 + lines_cleared // 10
                        # speed up
                        fall_speed = max(100, 700 - (level - 1) * 50)
                        pygame.time.set_timer(pygame.USEREVENT + 1, fall_speed)
                    current = next_piece
                    next_piece = next_piece_from_bag()
                    if collide(grid, current.shape, current.x, current.y):
                        game_over = True
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    fast_fall = False
            if event.type == pygame.USEREVENT + 1 and not paused and not game_over:
                # gravity tick
                step = 1 if not fast_fall else 5
                moved = False
                for _ in range(step):
                    if not collide(grid, current.shape, current.x, current.y + 1):
                        current.y += 1
                        moved = True
                    else:
                        # lock
                        lock_piece(grid, current)
                        grid, cleared = clear_lines(grid)
                        if cleared:
                            lines_cleared += cleared
                            score += (100 * (2 ** (cleared - 1))) * level
                            level = 1 + lines_cleared // 10
                            fall_speed = max(100, 700 - (level - 1) * 50)
                            pygame.time.set_timer(pygame.USEREVENT + 1, fall_speed)
                        current = next_piece
                        next_piece = next_piece_from_bag()
                        if collide(grid, current.shape, current.x, current.y):
                            game_over = True
                        break

        # DRAW
        SCREEN.fill(BLACK)
        # play area background
        play_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        pygame.draw.rect(SCREEN, (10, 10, 10), play_rect)
        draw_grid(SCREEN, grid)
        # draw ghost
        ghost_piece = Piece(current.key)
        ghost_piece.shape = [row[:] for row in current.shape]
        ghost_piece.color = current.color
        ghost_piece.x = current.x
        ghost_piece.y = current.y
        ghost_piece.y = get_ghost_y(grid, ghost_piece)
        draw_piece(SCREEN, ghost_piece, ghost=True)
        # draw current
        draw_piece(SCREEN, current)
        # side panel
        draw_side_panel(SCREEN, next_piece, score, level, lines_cleared)

        if paused:
            draw_text(SCREEN, "PAUSED", 40, WIDTH // 2, HEIGHT // 2, center=True)
        if game_over:
            draw_text(SCREEN, "GAME OVER", 40, WIDTH // 2, HEIGHT // 2 - 20, center=True)
            draw_text(SCREEN, "Press R to restart", 20, WIDTH // 2, HEIGHT // 2 + 30, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()