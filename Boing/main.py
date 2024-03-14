import pgzero, pgzrun, pygame
import math, sys, random
from enum import Enum

if sys.version_info < (3, 5):
    print(
        "This game requires at least version 3.5 of Python. Please download",
        "it from www.python.org",
    )
    sys.exit()

pgzero_version = [int(s) if s.isnumeric() else s for s in pgzero.__version__.split(".")]
if pgzero_version < [1, 2]:
    print(
        "This game requires atleast version 1.2 of Pygame Zero. You are"
        "using version {pgzero.__version__}. Please upgrade using the command"
        "'pip install --upgrade pgzero'"
    )
    sys.exit()

WIDTH = 800
HEIGHT = 480
TITLE = "Boing!"

HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
PLAYER_SPEED = 6
MAX_AI_SPEED = 6


def normalised(x, y):
    length = math.hypot(x, y)
    return (x / length, y / length)


def sign(x):
    return -1 if x < 0 else 1


class Impact(Actor):
    def __init__(self, pos):
        super().__init__("blank", pos)
        self.time = 0

    def update(self):
        self.image = "impact" + str(self.time // 2)
        self.time += 1


class Ball(Actor):
    def __init__(self, dx):
        super().__init__("ball", (0, 0))
        self.x, self.y = HALF_WIDTH, HALF_HEIGHT
        self.dx, self.dy = dx, 0
        self.speed = 5

    def update(self):
        for i in range(self.speed):
            original_x = self.x
            self.x += self.dx
            self.y += self.dy

            if abs(self.x - HALF_WIDTH) >= 344 and abs(original_x - HALF_WIDTH) < 344:
                if self.x < HALF_WIDTH:
                    new_dir_x = 1
                    bat = game.bats[0]
                else:
                    new_dir_x = -1
                    bat = game.bats[-1]

                difference_y = self.y - bat.y

                if difference_y > -64 and difference_y < 64:
                    self.dx = -self.dx
                    self.dy += difference_y / 128
                    self.dy = min(max(self.dy, -1), 1)
                    self.dx, self.dy = normalised(self.dx, self.dy)
                    game.impacts.append(Impact((self.x - new_dir_x * 10, self.y)))
                    self.speed += 1
                    game.ai_offset = random.randint(-10, 10)
                    bat.time = 10

                    game.play_sound("hit", 5)
                    if self.speed <= 10:
                        game.play_sound("hit_slow", 1)
                    elif self.speed <= 12:
                        game.play_sound("hit_medium", 1)
                    elif self.speed <= 16:
                        game.play_sound("hit_fast", 1)
                    else:
                        game.play_sound("hit_veryfast", 1)

            if abs(self.y - HALF_HEIGHT) > 220:
                self.dy = -self.dy
                self.y += self.dy
                game.impacts.append(Impact(self.pos))
                game.play_sound("bounce", 5)
                game.play_sound("bounce_synth", 1)

    def out(self):
        return self.x < 0 or self.x > WIDTH


class Bat(Actor):
    def __init__(self, player, move_func=None):
        x = 40 if player == 0 else 760
        y = HALF_HEIGHT
        super().__init__("blank", (x, y))

        self.player = player
        self.score = 0

    # TODO: Continue writing this class


def p1_controls():
    move = 0
    if keyboard.z or keyboard.down:
        move = PLAYER_SPEED
    elif keyboard.a or keyboard.up:
        move = -PLAYER_SPEED
    return move


def p2_controls():
    move = 0
    if keyboard.m:
        move = PLAYER_SPEED
    elif keyboard.k:
        move = -PLAYER_SPEED
    return move


class State(Enum):
    MENU = 1
    PLAY = 2
    GAME_OVER = 3


num_players = 1
space_down = False


def update():
    global state, game, num_players, space_down
    space_pressed = False
    if keyboard.space and not space_down:
        space_pressed = True
    space_down = keyboard.space

    if state == State.MENU:
        if space_pressed:
            state = State.PLAY
            controls = [p1_controls]
            controls.append(p2_controls if num_players == 2 else None)
            game = Game(controls)
        else:
            if num_players == 2 and keyboard.up:
                sounds.up.play()
                num_players = 2

        game.update()

    elif state == State.PLAY:
        if max(game.bats[0].score, game.bats[1].score) > 9:
            state = State.GAME_OVER
        else:
            game.update()

    elif state == State.GAME_OVER:
        if space_pressed:
            state = State.MENU
            num_players = 1
            game = Game()


def draw():
    game.draw()

    if state == State.MENU:
        menu_image = "menu" + str(num_players - 1)
        screen.blit(menu_image, (0, 0))
    elif state == State.GAME_OVER:
        screen.blit("over", (0, 0))


try:
    pygame.mixer.quit()
    pygame.mixer.init(44100, -16, 2, 1024)

    music.play("theme")
    music.mixer.set_volume(0.3)
except:
    pass


state = State.MENU
game = Game()

pgzrun.go()