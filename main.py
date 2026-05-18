import pygame
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

pygame.init()

WIDTH, HEIGHT = 800, 860
SQUARE_SIZE   = WIDTH // 8

WHITE       = (255, 255, 255)
BROWN       = (139, 69, 19)
YELLOW      = (255, 255, 0)
GREEN       = (0, 200, 0)
BLACK_COLOR = (0, 0, 0)
GRAY        = (40, 40, 40)
RED         = (220, 50, 50)
LIGHT_GRAY  = (200, 200, 200)
GOLD        = (255, 215, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

font_large = pygame.font.SysFont("Arial", 36, bold=True)
font_med   = pygame.font.SysFont("Arial", 26, bold=True)

class ChessPiece:
    def __init__(self, color, piece_type, image_path):
        self.color = color
        self.type  = piece_type
        self.has_moved = False
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (SQUARE_SIZE, SQUARE_SIZE))
        except:
            self.image = None

board          = [[None for _ in range(8)] for _ in range(8)]
current_player = 'white'
selected_piece = None
selected_pos   = None
game_over      = False
winner         = None

def init_board():
    for col in range(8):
        board[1][col] = ChessPiece('black', 'pawn', 'images/black_pawn.png')
        board[6][col] = ChessPiece('white', 'pawn', 'images/white_pawn.png')

    board[0][0] = ChessPiece('black', 'rook',   'images/black_rook.png')
    board[0][7] = ChessPiece('black', 'rook',   'images/black_rook.png')
    board[7][0] = ChessPiece('white', 'rook',   'images/white_rook.png')
    board[7][7] = ChessPiece('white', 'rook',   'images/white_rook.png')

    board[0][1] = ChessPiece('black', 'knight', 'images/black_knight.png')
    board[0][6] = ChessPiece('black', 'knight', 'images/black_knight.png')
    board[7][1] = ChessPiece('white', 'knight', 'images/white_knight.png')
    board[7][6] = ChessPiece('white', 'knight', 'images/white_knight.png')

    board[0][2] = ChessPiece('black', 'bishop', 'images/black_bishop.png')
    board[0][5] = ChessPiece('black', 'bishop', 'images/black_bishop.png')
    board[7][2] = ChessPiece('white', 'bishop', 'images/white_bishop.png')
    board[7][5] = ChessPiece('white', 'bishop', 'images/white_bishop.png')

    board[0][3] = ChessPiece('black', 'queen', 'images/black_queen.png')
    board[7][3] = ChessPiece('white', 'queen', 'images/white_queen.png')
    board[0][4] = ChessPiece('black', 'king',  'images/black_king.png')
    board[7][4] = ChessPiece('white', 'king',  'images/white_king.png')


def get_valid_moves(piece, row, col, check_safety=True):
    moves = []

    if piece.type == 'pawn':
        d = -1 if piece.color == 'white' else 1
        if 0 <= row + d < 8 and board[row + d][col] is None:
            moves.append((row + d, col))
            if (piece.color == 'white' and row == 6) or (piece.color == 'black' and row == 1):
                if board[row + 2*d][col] is None:
                    moves.append((row + 2*d, col))
        for dc in [-1, 1]:
            if 0 <= row + d < 8 and 0 <= col + dc < 8:
                t = board[row + d][col + dc]
                if t and t.color != piece.color:
                    moves.append((row + d, col + dc))

    elif piece.type == 'rook':
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            r, c = row+dr, col+dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != piece.color:
                    moves.append((r, c)); break
                else:
                    break
                r += dr; c += dc

    elif piece.type == 'bishop':
        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            r, c = row+dr, col+dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != piece.color:
                    moves.append((r, c)); break
                else:
                    break
                r += dr; c += dc

    elif piece.type == 'queen':
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            r, c = row+dr, col+dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] is None:
                    moves.append((r, c))
                elif board[r][c].color != piece.color:
                    moves.append((r, c)); break
                else:
                    break
                r += dr; c += dc

    elif piece.type == 'knight':
        for dr, dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            r, c = row+dr, col+dc
            if 0 <= r < 8 and 0 <= c < 8 and (board[r][c] is None or board[r][c].color != piece.color):
                moves.append((r, c))

    elif piece.type == 'king':
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row+dr, col+dc
                if 0 <= r < 8 and 0 <= c < 8 and (board[r][c] is None or board[r][c].color != piece.color):
                    moves.append((r, c))

    if check_safety:
        moves = [m for m in moves if not move_leaves_king_in_check(piece, row, col, m)]

    return moves


def find_king(color):
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p.color == color and p.type == 'king':
                return (r, c)
    return None

def is_in_check(color):
    king_pos = find_king(color)
    if not king_pos:
        return False
    opponent = 'black' if color == 'white' else 'white'
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p.color == opponent:
                if king_pos in get_valid_moves(p, r, c, check_safety=False):
                    return True
    return False

def move_leaves_king_in_check(piece, from_r, from_c, to_pos):
    to_r, to_c    = to_pos
    original_dest = board[to_r][to_c]
    board[to_r][to_c]     = piece
    board[from_r][from_c] = None
    in_check = is_in_check(piece.color)
    board[from_r][from_c] = piece
    board[to_r][to_c]     = original_dest
    return in_check

def has_any_legal_moves(color):
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p.color == color:
                if get_valid_moves(p, r, c):
                    return True
    return False

def has_insufficient_material():
    pieces = [board[r][c] for r in range(8) for c in range(8) if board[r][c]]
    return len(pieces) == 2

def check_game_over(color):
    if has_insufficient_material():
        return True, "DRAW - Insufficient Material"
    if not has_any_legal_moves(color):
        if is_in_check(color):
            w = 'BLACK' if color == 'white' else 'WHITE'
            return True, f"CHECKMATE - {w} WINS!"
        else:
            return True, "STALEMATE - Draw!"
    return False, None


def draw_board():
    valid_moves = []
    if selected_piece and selected_pos:
        valid_moves = get_valid_moves(selected_piece, *selected_pos)

    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color,
                             (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

  
    king_pos = find_king(current_player)
    if king_pos and is_in_check(current_player):
        kr, kc = king_pos
        pygame.draw.rect(screen, RED,
                         (kc*SQUARE_SIZE, kr*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    if selected_pos:
        pygame.draw.rect(screen, YELLOW,
                         (selected_pos[1]*SQUARE_SIZE, selected_pos[0]*SQUARE_SIZE,
                          SQUARE_SIZE, SQUARE_SIZE))

   
    for (r, c) in valid_moves:
        cx = c*SQUARE_SIZE + SQUARE_SIZE//2
        cy = r*SQUARE_SIZE + SQUARE_SIZE//2
        if board[r][c]:
            pygame.draw.circle(screen, GREEN, (cx, cy), SQUARE_SIZE//2 - 4, 5)
        else:
            pygame.draw.circle(screen, GREEN, (cx, cy), SQUARE_SIZE//6)

def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.image:
                screen.blit(piece.image, (col*SQUARE_SIZE, row*SQUARE_SIZE))

def draw_ui():
   
    panel_y = 800
    pygame.draw.rect(screen, GRAY, (0, panel_y, WIDTH, 60))

  
    turn_label = "WHITE's Turn" if current_player == 'white' else "BLACK's Turn"
    turn_color = WHITE
    turn_text  = font_large.render(turn_label, True, turn_color)
    screen.blit(turn_text, (WIDTH//2 - turn_text.get_width()//2, panel_y + 10))

   
    if not game_over and is_in_check(current_player):
        check_surf = font_med.render("CHECK!", True, RED)
        screen.blit(check_surf, (WIDTH - check_surf.get_width() - 20, panel_y + 18))

def draw_game_over(message):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    box_w, box_h = 560, 200
    box_x = WIDTH//2 - box_w//2
    box_y = HEIGHT//2 - box_h//2
    pygame.draw.rect(screen, GRAY, (box_x, box_y, box_w, box_h), border_radius=16)
    pygame.draw.rect(screen, GOLD, (box_x, box_y, box_w, box_h), 3, border_radius=16)

    msg     = font_large.render(message, True, GOLD)
    restart = font_med.render("Press R to Restart", True, LIGHT_GRAY)
    screen.blit(msg,     (WIDTH//2 - msg.get_width()//2,     box_y + 55))
    screen.blit(restart, (WIDTH//2 - restart.get_width()//2, box_y + 120))


def handle_click(pos):
    global selected_piece, selected_pos, current_player, game_over, winner

    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE

    if row >= 8 or col >= 8:
        return

    if selected_piece is None:
        piece = board[row][col]
        if piece and piece.color == current_player:
            selected_piece = piece
            selected_pos   = (row, col)
        else:
            if piece:
                print(f"Not your piece! {current_player}'s turn.")
    else:
        if (row, col) == selected_pos:
            selected_piece = None
            selected_pos   = None
            return

        clicked = board[row][col]
        if clicked and clicked.color == current_player:
            selected_piece = clicked
            selected_pos   = (row, col)
            return

        valid_moves = get_valid_moves(selected_piece, *selected_pos)
        if (row, col) in valid_moves:
            board[row][col]                         = selected_piece
            board[selected_pos[0]][selected_pos[1]] = None
            selected_piece.has_moved                = True

            if selected_piece.type == 'pawn' and (row == 0 or row == 7):
                board[row][col] = ChessPiece(selected_piece.color, 'queen',
                                             f'images/{selected_piece.color}_queen.png')

            current_player = 'black' if current_player == 'white' else 'white'

            over, msg = check_game_over(current_player)
            if over:
                game_over = True
                winner    = msg
                print(f"GAME OVER: {msg}")
        else:
            print("Invalid move!")

        selected_piece = None
        selected_pos   = None


def restart_game():
    global board, current_player, selected_piece, selected_pos, game_over, winner
    board          = [[None for _ in range(8)] for _ in range(8)]
    current_player = 'white'
    selected_piece = None
    selected_pos   = None
    game_over      = False
    winner         = None
    init_board()


def main():
    init_board()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    handle_click(pygame.mouse.get_pos())

        screen.fill(BLACK_COLOR)
        draw_board()
        draw_pieces()
        draw_ui()

        if game_over and winner:
            draw_game_over(winner)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()