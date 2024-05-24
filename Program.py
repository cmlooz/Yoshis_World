import pygame
import pygame_gui
import sys
import random
import math

from pygame import Clock

from Classes import Yoshi, MiniMax, Heuristic

# Definimos algunas constantes
WIDTH = 1000
HEIGHT = 800
BOARD_WIDTH = 800
ROWS = 10
COLS = 10
SQUARE_SIZE = BOARD_WIDTH // COLS
INFO_WIDTH = WIDTH - BOARD_WIDTH
INFO_FONT_SIZE = 24

# Definimos los colores
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# Para guardar las jugadas
green_painted = set()
red_painted = set()

class World:
    def __init__(self):
        # Definimos los turnos de los jugadores
        self.clock = Clock()
        self.TURN_GREEN = 0
        self.TURN_RED = 1
        self.current_turn = 0
        self.setupPyGame()

        self.manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        self.difficulty = 2  # Default difficulty level

        # Elementos de la interfaz
        self.difficulty_selector = pygame_gui.elements.UIDropDownMenu(
            options_list=["principiante", "intermedio", "avanzado"],
            starting_option="principiante",
            relative_rect=pygame.Rect((BOARD_WIDTH + 20, 50), (INFO_WIDTH - 40, 30)),
            manager=self.manager
        )

        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((BOARD_WIDTH + 20, 100), (INFO_WIDTH - 40, 50)),
            text='Comenzar Juego',
            manager=self.manager
        )

        self.is_game_started = False
        self.green_moves = 0
        self.red_moves = 0

        #self.green_yoshi = None
        #self.red_yoshi = None

    def setupPyGame(self):
        # Inicializamos pygame
        pygame.init()
        self.WIN = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Yoshi's World")
        self.info_font = pygame.font.Font(None, INFO_FONT_SIZE)
        # Cargamos las imágenes de los Yoshis
        self.green_image = pygame.image.load("green_yoshi.png").convert_alpha()
        self.red_image = pygame.image.load("red_yoshi.png").convert_alpha()
        self.green_image = pygame.transform.scale(self.green_image, (SQUARE_SIZE, SQUARE_SIZE))
        self.red_image = pygame.transform.scale(self.red_image, (SQUARE_SIZE, SQUARE_SIZE))

    def draw_info(self):
        # Dibujamos el texto de información
        info_surface = pygame.Surface((INFO_WIDTH, HEIGHT))
        info_surface.fill(GRAY)
        green_text = self.info_font.render(f"Green: {len(green_painted)} squares", True, GREEN)
        red_text = self.info_font.render(f"Red: {len(red_painted)} squares", True, RED)
        turn_text = self.info_font.render(f"Turn: {'Green' if self.current_turn == self.TURN_GREEN else 'Red'}", True,
                                          WHITE)
        info_surface.blit(green_text, (10, 150))
        info_surface.blit(red_text, (10, 190))
        info_surface.blit(turn_text, (10, 230))
        self.WIN.blit(info_surface, (BOARD_WIDTH, 0))

    def draw(self):
        if not self.is_game_started:
            return False

        # Dibujamos el tablero
        for row in range(ROWS):
            for col in range(COLS):
                color = WHITE
                if (row, col) in green_painted:
                    color = GREEN
                elif (row, col) in red_painted:
                    color = RED
                pygame.draw.rect(self.WIN, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                pygame.draw.rect(self.WIN, GRAY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 1)

        # Dibujamos las casillas disponibles para mover en amarillo o azul según el turno
        if self.current_turn == self.TURN_GREEN:
            for move in self.green_yoshi.possible_moves(green_painted,red_painted):
                pygame.draw.rect(self.WIN, WHITE,
                                 (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE, SQUARE_SIZE-5, SQUARE_SIZE-5))
                pygame.draw.rect(self.WIN, YELLOW,
                                 (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),1)
        elif self.current_turn == self.TURN_RED:
            for move in self.red_yoshi.possible_moves(green_painted,red_painted):
                pygame.draw.rect(self.WIN, WHITE,
                                 ((move[1] * SQUARE_SIZE), (move[0] * SQUARE_SIZE), SQUARE_SIZE-5, SQUARE_SIZE-5))
                pygame.draw.rect(self.WIN, BLUE,
                                 (move[1] * SQUARE_SIZE, move[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),1)

        # Dibujamos los Yoshis
        self.green_yoshi.draw(self.WIN)
        self.red_yoshi.draw(self.WIN)

    def best_move(self,x, y, player, depth):
        best_val = float(-math.inf)
        move = None
        possible_moves_ = []
        print("_____")
        for m in MiniMax().get_valid_moves(x, y, ROWS, COLS, green_painted, red_painted):
            green_painted.add(m)
            move_val = MiniMax().minimax((m[0], m[1]), (self.red_yoshi.row,self.red_yoshi.col), depth, False, -math.inf, math.inf, player, ROWS, COLS, green_painted, red_painted)
            green_painted.remove(m)
            #print("Best move", move_val, best_val, m)
            possible_moves_.append({'green': m, 'red':(self.red_yoshi.row,self.red_yoshi.col), 'heuristic': move_val})

            if move_val > best_val:
                best_val = move_val
                move = m

        for move_ in possible_moves_:
            print("Green pos",move_['green'],"Red pos",move_['red'], "Heu",move_['heuristic'])

        return move

    def move_green_yoshi_auto(self, x, y):
        target_position = self.best_move(x, y, self.TURN_GREEN, self.difficulty)
        if target_position:
            green_painted.add(target_position)
            self.green_yoshi.row, self.green_yoshi.col = target_position
        self.green_moves += 1
        self.current_turn = self.TURN_RED

    def start_game(self):
        # Generamos posiciones iniciales aleatorias para los Yoshis
        green_start = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
        red_start = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
        # Nos aseguramos de que las posiciones iniciales no coincidan
        while green_start == red_start:
            red_start = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))

        # Creamos dos Yoshis (uno verde y uno rojo) en posiciones aleatorias
        self.green_yoshi = Yoshi(GREEN, green_start[0], green_start[1], self.green_image, SQUARE_SIZE,ROWS, COLS)
        self.red_yoshi = Yoshi(RED, red_start[0], red_start[1], self.red_image, SQUARE_SIZE,ROWS, COLS)

        self.current_turn = self.TURN_GREEN
        self.is_game_started = True
        self.green_moves = 0
        self.red_moves = 0

    def game_loop(self):
        pass_turn_counter = 0

        while True:
            time_delta = self.clock.tick(60) / 1000.0
            self.manager.update(time_delta)

            x, y = pygame.mouse.get_pos()
            # Check if the current player has no possible moves
            if self.current_turn == self.TURN_GREEN and self.is_game_started:
                self.move_green_yoshi_auto(self.green_yoshi.row, self.green_yoshi.col)
                pygame.time.wait(1000)  # Espera 1 segundo antes de hacer el movimiento
            elif self.current_turn == self.TURN_RED and len(self.red_yoshi.possible_moves(green_painted,red_painted)) == 0 and self.is_game_started:
                self.red_moves += 1
                self.current_turn = self.TURN_GREEN
                pass_turn_counter += 1

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.start_button:
                        self.start_game()
                elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == self.difficulty_selector:
                        selected_text = event.text
                        if selected_text == "principiante":
                            self.difficulty = 2
                        elif selected_text == "intermedio":
                            self.difficulty = 6
                        elif selected_text == "avanzado":
                            self.difficulty = 10
                elif event.type == pygame.MOUSEBUTTONDOWN and self.is_game_started:
                    col = x // SQUARE_SIZE
                    row = y // SQUARE_SIZE
                    target_position = (row, col)
                    if target_position in self.red_yoshi.possible_moves(green_painted,red_painted) and self.current_turn == self.TURN_RED:
                        red_painted.add(target_position)
                        self.red_yoshi.row, self.red_yoshi.col = target_position
                        self.red_moves += 1
                        self.current_turn = self.TURN_GREEN

                self.manager.process_events(event)

            # Dibujamos el tablero y la información
            self.WIN.fill(WHITE)
            self.draw()
            self.draw_info()
            self.manager.draw_ui(self.WIN)

            # Verificamos si el juego ha terminado
            if len(green_painted) + len(red_painted) == ROWS * COLS or pass_turn_counter > 2:
                pygame.time.wait(2000)  # Espera 2 segundos antes de mostrar el resultado final
                if len(green_painted) > len(red_painted):
                    winner_text = self.info_font.render("Green wins!", True, GREEN)
                elif len(green_painted) < len(red_painted):
                    winner_text = self.info_font.render("Red wins!", True, RED)
                else:
                    winner_text = self.info_font.render("It's a draw!", True, WHITE)
                self.WIN.blit(winner_text, (BOARD_WIDTH + INFO_WIDTH // 2 - 100, HEIGHT // 2 - INFO_FONT_SIZE))
                pygame.display.update()
                pygame.time.wait(5000)  # Espera 5 segundos antes de salir del juego
                pygame.quit()
                sys.exit()

            pygame.display.update()


if __name__ == "__main__":
    world = World()
    #world.start_game()
    world.game_loop()