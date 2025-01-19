from flask import Flask
import streamlit as st
from PIL import Image
import threading
import base64
import pygame
import random
import os

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

@app.route("/", methods=['GET'])
def newFrame():
    if CHOSEN_FRAME != None:
        return {"b64frame": base64.b64encode(CHOSEN_FRAME.tobytes()).decode()}
    else:
        return {"b64frame": None}

class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x=None, y=None, other_figure=None):
        if other_figure:
            self.x = other_figure.x
            self.y = other_figure.y
            self.type = other_figure.type
            self.color = other_figure.color
            self.rotation = other_figure.rotation
        else:
            self.x = x
            self.y = y
            # TODO, return  self.type = random.randint(0, len(self.figures) - 1)
            self.type = 1
            # TODO, self.color = random.randint(1, len(colors) - 1)
            self.color = random.randint(1, 6)
            self.rotation = 0



    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class Tetris:
    def __init__(self, height, width):
        self.level = 2
        self.score = 0
        self.state = "start"
        self.field = []
        self.height = 0
        self.width = 0
        self.x = 100
        self.y = 60
        self.zoom = 20
        self.figure = None
    
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"
        self.bad_ends = [[]]
        self.bad_ends_index = 0
        self.holes = []
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure = Figure(3, 0)

    def intersects(self, figure):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in figure.image():
                    if i + figure.y > self.height - 1 or \
                            j + figure.x > self.width - 1 or \
                            j + figure.x < 0 or \
                            7 > self.field[i + figure.y][j + figure.x] > 0:
                        return True
        return False

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

    def go_space(self):
        while not self.intersects(self.figure):

            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects(self.figure):
            self.figure.y -= 1
            self.freeze()


    def freeze(self):
        for x,y in figure_to_field(self.figure,self.figure.x,self.figure.y):
            self.field[x][y] = self.figure.color
        self.break_lines()
        self.new_figure()

        for layer in self.bad_ends:
            for brick in layer:
                for bx,by in brick:
                    if self.field[bx][by] in [7,8]:
                        self.field[bx][by] = 0

        self.holes = is_bad_brick(self.field)
        self.bad_ends_index = 0
        self.bad_ends = self.get_bad_ends()

        if self.intersects(self.figure):
            self.state = "gameover"

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects(self.figure):
            self.figure.x = old_x

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects(self.figure):
            self.figure.rotation = old_rotation

    def horizontal_out_of_bounds(self, figure):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in figure.image():
                    if j + figure.x > self.width - 1 or \
                            j + figure.x < 0:
                        intersection = True
        return intersection

    def get_bad_ends(self):
        copy_figure = Figure(other_figure=self.figure)
        copy_figure.color = 0 # Gray
        default_field_copy = [i for i in self.field]
        bad_end_layers = [[]]

        for formation in range(len(copy_figure.figures[copy_figure.type])):
            copy_figure.rotation = formation
            for xcoor in range(10):
                copy_figure.x = xcoor
                for ycoor in range(20):
                    copy_figure.y = ycoor
                    if self.horizontal_out_of_bounds(copy_figure):
                        continue
                    if self.intersects(copy_figure):
                        #Set to previous position
                        ycoor -= 1
                        copy_figure.y = ycoor
                        if self.intersects(copy_figure):
                            # Meaning we skip the intersects that wouldn't be possible to achieve anyway
                            break

                        # Temp set
                        to_field = figure_to_field(copy_figure,xcoor,ycoor)
                        for x, y in to_field:
                            default_field_copy[x][y] = (128,128,128)
                        #Determine if it's a bad end and add it to the list
                        bad_end_layers = add_to_bad_layers(bad_end_layers,copy_figure,xcoor,ycoor) \
                            if is_bad_brick(default_field_copy,self.holes) else bad_end_layers

                        # Remove temp
                        for x, y in figure_to_field(copy_figure,xcoor,ycoor):
                            if default_field_copy[x][y] == (128,128,128):
                                default_field_copy[x][y] = 0
        return bad_end_layers


def figure_to_field(figure,x,y):
    field_placement = []
    for i in range(4):
        for j in range(4):
            if i * 4 + j in figure.image():
                field_placement.append((i + y, j + x))

    return field_placement

def is_bad_brick(default_field_copy, old_holes=()):
    holes = []
    for row in range(len(default_field_copy)):
        for sq in range(len(default_field_copy[row])):
            surrounded = []
            if row != 0:
                surrounded.append(default_field_copy[row - 1][sq])

            if row != 19:
                surrounded.append(default_field_copy[row + 1][sq])
            if sq != 0:
                surrounded.append(default_field_copy[row][sq - 1])

            if sq != 9:
                surrounded.append(default_field_copy[row][sq + 1])

            if 0 not in surrounded and default_field_copy[row][sq] == 0 and (row,sq) not in old_holes:
                holes.append((row,sq))
    return holes

def add_to_bad_layers(bad_end_layers,copy_figure,xcoor,ycoor):
    added = False
    for layer in range(len(bad_end_layers)):
        overlap = False
        for placement in bad_end_layers[layer]:
            if set(tuple(placement)).intersection(set(tuple(figure_to_field(copy_figure, xcoor, ycoor)))) != set():
                overlap = True
                break
        if not overlap:
            bad_end_layers[layer].append(figure_to_field(copy_figure, xcoor, ycoor))
            added = True
            break
    if not added:
        bad_end_layers.append([figure_to_field(copy_figure, xcoor, ycoor)])
    return bad_end_layers

def game():
    global CHOSEN_FRAME
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

    pressing_down = False

    while not done:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % (fps // game.level // 2) == 0 or pressing_down:
            if game.state == "start":
                game.go_down()



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    game.rotate()
                if event.key == pygame.K_DOWN:
                    pressing_down = True
                if event.key == pygame.K_LEFT:
                    game.go_side(-1)
                if event.key == pygame.K_RIGHT:
                    game.go_side(1)
                if event.key == pygame.K_SPACE:
                    game.go_space()
                if event.key == pygame.K_ESCAPE:
                    game.__init__(20, 10)

        if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        screen.fill(WHITE)
        game.bad_ends_index += 0.1
        if game.bad_ends_index >= len(game.bad_ends): game.bad_ends_index = 0
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
                pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                    [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])

        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(screen, colors[game.figure.color],
                                        [game.x + game.zoom * (j + game.figure.x) + 1,
                                        game.y + game.zoom * (i + game.figure.y) + 1,
                                        game.zoom - 2, game.zoom - 2])

        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text = font.render("Score: " + str(game.score), True, BLACK)
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

        screen.blit(text, [0, 0])
        if game.state == "gameover":
            screen.blit(text_game_over, [20, 200])
            screen.blit(text_game_over1, [25, 265])
        
        CHOSEN_FRAME = Image.frombytes("RGB", screen.size, pygame.image.tobytes(screen, "RGB"))
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

if __name__ == '__main__':
    # Create thread for Flask
    flask_thread = threading.Thread(target=app.run, kwargs={'debug': False, 'use_reloader': False})
    flask_thread.start()
    # Start Tetris on main thread
    game()