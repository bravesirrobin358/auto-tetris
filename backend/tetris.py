from figure import Figure


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
                    if (
                        i + figure.y > self.height - 1
                        or j + figure.x > self.width - 1
                        or j + figure.x < 0
                        or 7 > self.field[i + figure.y][j + figure.x] > 0
                    ):
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
        self.score += lines**2

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
        for x, y in figure_to_field(self.figure, self.figure.x, self.figure.y):
            self.field[x][y] = self.figure.color
        self.break_lines()
        self.new_figure()

        for layer in self.bad_ends:
            for brick in layer:
                for bx, by in brick:
                    if self.field[bx][by] in [7, 8]:
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
                    if j + figure.x > self.width - 1 or j + figure.x < 0:
                        intersection = True
        return intersection

    def get_bad_ends(self):
        copy_figure = Figure(other_figure=self.figure)
        copy_figure.color = 0  # Gray
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
                        # Set to previous position
                        ycoor -= 1
                        copy_figure.y = ycoor
                        if self.intersects(copy_figure):
                            # Meaning we skip the intersects that wouldn't be possible to achieve anyway
                            break

                        # Temp set
                        to_field = figure_to_field(copy_figure, xcoor, ycoor)
                        for x, y in to_field:
                            default_field_copy[x][y] = (128, 128, 128)
                        # Determine if it's a bad end and add it to the list
                        bad_end_layers = (
                            add_to_bad_layers(bad_end_layers, copy_figure, xcoor, ycoor)
                            if is_bad_brick(default_field_copy, self.holes)
                            else bad_end_layers
                        )

                        # Remove temp
                        for x, y in figure_to_field(copy_figure, xcoor, ycoor):
                            if default_field_copy[x][y] == (128, 128, 128):
                                default_field_copy[x][y] = 0
        return bad_end_layers


def figure_to_field(figure, x, y):
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

            if (
                0 not in surrounded
                and default_field_copy[row][sq] == 0
                and (row, sq) not in old_holes
            ):
                holes.append((row, sq))
    return holes


def add_to_bad_layers(bad_end_layers, copy_figure, xcoor, ycoor):
    added = False
    for layer in range(len(bad_end_layers)):
        overlap = False
        for placement in bad_end_layers[layer]:
            if (
                set(tuple(placement)).intersection(
                    set(tuple(figure_to_field(copy_figure, xcoor, ycoor)))
                )
                != set()
            ):
                overlap = True
                break
        if not overlap:
            bad_end_layers[layer].append(figure_to_field(copy_figure, xcoor, ycoor))
            added = True
            break
    if not added:
        bad_end_layers.append([figure_to_field(copy_figure, xcoor, ycoor)])
    return bad_end_layers
