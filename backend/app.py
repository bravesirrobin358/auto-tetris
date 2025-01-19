from flask import Flask, request
from PIL import Image
import threading
import base64
import pygame
import os
from tetris import Tetris

# Make the pygame headless
os.environ["SDL_VIDEODRIVER"] = "dummy"

app = Flask(__name__)
CHOSEN_FRAME = None

colors = [
    (255, 255, 255),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
    (0, 0, 0),
    (255, 255, 255),
]

DIRECTION = None
SLAM = None
ROTATE = None
can_restart = False
can_start = False

@app.route("/", methods=["GET"])
def newFrame():
    if CHOSEN_FRAME is not None:
        return {"b64frame": base64.b64encode(CHOSEN_FRAME.tobytes()).decode()}
    else:
        return {"b64frame": None}

@app.route("/control", methods=["POST"])
def control():
    global DIRECTION, SLAM, ROTATE
    if request.method == "POST":
        response = request.get_json()
        DIRECTION = response["direction"]
        SLAM = response["slam"]
        ROTATE = response["rotate"]

@app.route("/restart", methods=["GET"])
def restart_game():
    global can_restart
    can_restart = True

@app.route("/start", methods=["GET"])
def start_game():
    global can_start
    can_start = True

def game():
    global CHOSEN_FRAME, DIRECTION, SLAM, ROTATE, can_restart, can_start
    # Initialize the game engine
    pygame.init()

    # Define some colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)

    size = (400, 500)
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Tetris")

    # Loop until the user clicks the close button.
    done = False
    clock = pygame.time.Clock()
    fps = 25
    game = Tetris(20, 10)
    counter = 0

    while not done and can_start:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (fps // game.level // 2) == 0 or SLAM:
            if game.state == "start":
                game.go_down()
        
        if ROTATE:
            game.rotate()
        if DIRECTION == "left":
            game.go_side(-1)
        if DIRECTION == "right":
            game.go_side(1)
        if can_restart:
            game.__init__(20, 10)

        screen.fill(WHITE)
        game.bad_ends_index += 0.1
        if game.bad_ends_index >= len(game.bad_ends):
            game.bad_ends_index = 0
        layer_shown = game.bad_ends[int(game.bad_ends_index)]
        for brick in layer_shown:
            # Time to display layer
            if game.bad_ends_index % 0.3 == 0:
                # For each tile in the brick
                for x, y in brick:
                    # Replace with hint tile if not occupied by active falling brick
                    if game.field[x][y] == 0:
                        game.field[x][y] = 7
            else:
                # Replace hint tiles with white tile so they don't linger,
                for x, y in brick:
                    if game.field[x][y] == 7:
                        game.field[x][y] = 0

        for i in range(game.height):
            for j in range(game.width):
                pygame.draw.rect(
                    screen,
                    GRAY,
                    [
                        game.x + game.zoom * j,
                        game.y + game.zoom * i,
                        game.zoom,
                        game.zoom,
                    ],
                    1,
                )
                pygame.draw.rect(
                    screen,
                    colors[game.field[i][j]],
                    [
                        game.x + game.zoom * j + 1,
                        game.y + game.zoom * i + 1,
                        game.zoom - 2,
                        game.zoom - 1,
                    ],
                )

        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(
                            screen,
                            colors[game.figure.color],
                            [
                                game.x + game.zoom * (j + game.figure.x) + 1,
                                game.y + game.zoom * (i + game.figure.y) + 1,
                                game.zoom - 2,
                                game.zoom - 2,
                            ],
                        )

        font = pygame.font.SysFont("Calibri", 25, True, False)
        font1 = pygame.font.SysFont("Calibri", 65, True, False)
        text = font.render("Score: " + str(game.score), True, BLACK)
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

        screen.blit(text, [0, 0])
        if game.state == "gameover":
            screen.blit(text_game_over, [20, 200])
            screen.blit(text_game_over1, [25, 265])

        CHOSEN_FRAME = Image.frombytes(
            "RGB", screen.size, pygame.image.tobytes(screen, "RGB")
        )
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    # Create thread for Flask
    flask_thread = threading.Thread(
        target=app.run, kwargs={"debug": False, "use_reloader": False}
    )
    flask_thread.start()
    # Start Tetris on main thread
    game()
