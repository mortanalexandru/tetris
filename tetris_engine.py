import numpy as np

GRID_W = 10
GRID_H = 20

ALL_SHAPES = 'IJLOSTZ'

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'Z': [[1, 1, 0], [0, 1, 1]]
}

OFFSETS = {
    'I': [0, -2, 0, -1],
    'J': [0, -1, 0, 0],
    'L': [0, -1, 0, 0],
    'O': [0, 0, 0, 0],
    'S': [0, -1, 0, 0],
    'T': [0, -1, 0, 0],
    'Z': [0, -1, 0, 0]
}

ACTIONS = {
    'I': 24,
    'J': 48,
    'L': 48,
    'O': 12,
    'S': 24,
    'T': 48,
    'Z': 24
}

def getShapePositionBounds(shape):
    return 0, GRID_W - len(shape[0])

class Tetris:
    def __init__(self, shapes, grid):
        self.shapes = shapes
        self.shapeIndex = 0
        self.grid = grid

        self.score = 0
        self.lost = False
        self.won = False
        self.over = False

    def get_nr_of_actions(self):
        return ACTIONS[self.shapes[self.shapeIndex]]

    def copy(self):
        new = Tetris(self.shapes, np.copy(self.grid))
        new.shapeIndex = self.shapeIndex
        new.score = self.score
        new.lost = self.lost
        new.won = self.won
        new.over = self.over
        return new

    def clone(self):
        c = Tetris(self.shapes)
        c.shapeIndex = self.shapeIndex
        c.grid = np.copy(self.grid)

        c.score = self.score
        c.lost = self.lost
        c.won = self.won
        c.over = self.over

        return c

    def make_move(self, pos, rot, is_test=False):
        shape = np.array(SHAPES[self.shapes[self.shapeIndex]])
        shape = np.rot90(shape, -rot)

        x = self.getBoundedX(shape, pos)

        y = self.getDropLocation(shape, x)

        if self.isLoss(shape, y):
            self.lost = True
            self.over = True
        else:
            self.score += 1
            self.applyShape(shape, x, y)
            if not is_test:
                self.score += self.clearRows()
            self.shapeIndex += 1
            if self.shapeIndex >= len(self.shapes):
                self.won = True
                self.over = True

    def isLoss(self, shape, y):
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j] != 0 and y + i < 0:
                    return True
        return False

    def applyShape(self, shape, x, y):
        for i in range(len(shape)):
            for j in range(len(shape[i])):
                if shape[i][j] != 0:
                    if x + j < GRID_W and y + i >= 0 and y + i < GRID_H:
                        self.grid[y + i][x + j] = shape[i][j]

    def clearRows(self):
        sum = np.sum(self.grid, 1)
        cleared = [x for x in range(GRID_H) if sum[x] == GRID_W]

        n = len(cleared)
        self.grid = np.delete(self.grid, cleared, 0)
        self.grid = np.concatenate((np.zeros((n, GRID_W)), self.grid), 0)

        score = [0, 100, 200, 400, 800][n]
        return score

    def getDropLocation(self, shape, x):
        for i in range(GRID_H - len(shape) + 1):
            if self.collides(self.grid, shape, x, i):
                return i - 1
        return GRID_H - len(shape)

    def collides(self, grid, shape, x, y):
        # # TODO improve this, use real shape bounds
        # minX, minY, maxX, maxY = self.getShapeOffset(shape)
        # shape = shape[minY:maxY, minX:maxX]
        # egrid = np.concatenate((np.zeros((4, GRID_W)), grid, np.zeros((4, GRID_W))), 0)
        # egrid = np.concatenate((np.zeros((GRID_H + 8, 4)), egrid, np.zeros((GRID_H + 8, 4))), 1)
        # egrid = egrid[(y+4):(y+4+len(shape)),x+4:x+4+len(shape[0])]
        # if len(egrid) != len(shape) or len(egrid[0]) != len(shape[0]):
        #     return False
        # egrid = np.logical_and(egrid, shape)
        # return np.sum(egrid) > 0

        i_size = len(shape)
        j_size = len(shape[0])
        mini_grid = self.grid[y:y + i_size, x:x + j_size]

        overlap = mini_grid * shape

        for i in range(i_size):
            for j in range(j_size):
                if overlap[i][j] != 0:
                    return True

        return False

    def getBoundedX(self, shape, x):
        minX, maxX = getShapePositionBounds(shape)
        if (x < minX):
            return minX
        if (x > maxX):
            return maxX
        return x

    def valid(self, shape, x):
        minX, maxX = getShapePositionBounds(shape)
        if (x < minX):
            return minX
        if (x > maxX):
            return maxX
        return x