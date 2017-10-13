# import copy
import numpy as np
import math

class AI:
    def __init__(self, heightWeight, linesWeight, holesWeight, bumpinessWeight):
        self.heightWeight = heightWeight
        self.linesWeight = linesWeight
        self.holesWeight = holesWeight
        self.bumpinessWeight = bumpinessWeight
        self.grid_system = np.zeros((2304, 20, 10))
        self.index = 0

    def best_move_improved(self, tetris, count):
        best_score, move = -1000, 0
        for action in range(tetris.get_nr_of_actions()):
            # game = tetris.copy()
            self.grid_system[self.index % 2304] = tetris.grid
            game = tetris.copy(self.grid_system[self.index % 2304])
            self.index += 1
            game.make_move((action % 12) - 1, int(action / 12), True)
            if not game.lost:
                if count > 0 and game.shapeIndex < len(game.shapes):
                    new_move, reward = self.best_move_improved(game, count - 1)
                else:
                    reward = self.get_reward(game)
                if reward > best_score:
                    best_score, move = reward, action

        return move, best_score

    def get_reward(self, game):
        heights = np.zeros(10)
        max_height = 0
        min_height = 0
        holes = 0
        for col in range(10):
            column = game.grid[:, col]
            nonzeros = np.flatnonzero(column)
            heights[col] = (20 - nonzeros[0]) if len(nonzeros) > 0 else 0
            if heights[col] > max_height:
                max_height = heights[col]
            if heights[col] < min_height:
                min_height = heights[col]
            ceiling = False
            for i in column:
                if i == 0 and ceiling:
                    # found hole
                    holes += 1
                if i > 0:
                    ceiling = True

        weighted_height = math.pow(max_height, 1.5)
        relative_height = max_height - min_height
        agg_height = np.sum(heights)
        lines = 0
        for row in game.grid:
            if len(np.flatnonzero(row)) == len(row):
                lines += 1

        bumpiness = 0
        for col in range(9):
            bumpiness += abs(heights[col] - heights[col + 1])
        # reward = -self.heightWeight * agg_height + self.linesWeight * lines - self.holesWeight * holes - self.bumpinessWeight * bumpiness

        reward = 0.22568649650722883 * lines - 0.08679520494876472 * weighted_height - 0.6152727732730796 * agg_height + 0.15842464424735841 *relative_height -0.15452215909537684 * holes - 0.021586109522043928 * bumpiness

        return reward
