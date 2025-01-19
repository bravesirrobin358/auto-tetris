import random
from shared import colors

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