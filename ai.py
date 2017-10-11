import copy
import numpy as np
from joblib import Parallel, delayed
import multiprocessing

class AI:
    def __init__(self, heightWeight, linesWeight, holesWeight, bumpinessWeight):
        self.heightWeight = heightWeight
        self.linesWeight = linesWeight
        self.holesWeight = holesWeight
        self.bumpinessWeight = bumpinessWeight

    def best(self, board):
        max_score = -1000
        best_move = 0
        for action in range(48):
            reward = self.score_move(board, action)
            if reward >= max_score:
                max_score = reward
                best_move = action

        return best_move, max_score

    def score_move(self, tetris, action):
        game = copy.deepcopy(tetris)
        game.make_move((action % 12) - 1, int(action / 12), True)

        heights = np.zeros(10)
        holes = 0
        for col in range(10):
            column = game.grid[:, col]
            nonzeros = np.flatnonzero(column)
            heights[col] = (20 - nonzeros[0]) if len(nonzeros) > 0 else 0
            ceiling = False
            for i in column:
                if i == 0 and ceiling:
                    # found hole
                    holes += 1
                    ceiling = False
                if i > 0:
                    ceiling = True

        agg_height = np.sum(heights)
        lines = 0
        for row in game.grid:
            if len(np.flatnonzero(row)) == len(row):
                lines += 1

        bumpiness = 0
        for col in range(9):
            bumpiness += abs(heights[col] - heights[col + 1])

        reward = self.heightWeight * agg_height + self.linesWeight * lines + self.holesWeight * holes + self.bumpinessWeight * bumpiness

        return reward

    def best_move(self, tetris, count):
        # tetris.print_grid()
        best_score = -1000
        move = 0
        for action in range(48):
            game = copy.deepcopy(tetris)
            game.make_move((action % 12) - 1, int(action / 12), True)
            if not game.lost:
                if count > 0 and game.shapeIndex < len(game.shapes):
                    new_move, reward = self.best_move(game, count - 1)
                else:
                    # game.print_grid()
                    heights = np.zeros(10)
                    holes = 0
                    for col in range(10):
                        column = game.grid[:, col]
                        nonzeros = np.flatnonzero(column)
                        heights[col] = (20 - nonzeros[0]) if len(nonzeros) > 0 else 0
                        ceiling = False
                        for i in column:
                            if i == 0 and ceiling:
                                # found hole
                                holes += 1
                            if i > 0:
                                ceiling = True

                    agg_height = np.sum(heights)
                    lines = 0
                    for row in game.grid:
                        if len(np.flatnonzero(row)) == len(row):
                            lines += 1

                    bumpiness = 0
                    for col in range(9):
                        bumpiness += abs(heights[col] - heights[col + 1])
                    # print(agg_height)
                    # print(lines)
                    # print(holes)
                    # print(bumpiness)
                    reward = -self.heightWeight * agg_height + self.linesWeight * lines - self.holesWeight * holes - self.bumpinessWeight * bumpiness
                    # print(reward)
                if reward > best_score:
                    best_score = reward
                    move = action

        return move, best_score

    def best_move_improved(self, tetris, count):
        best_score = -1000
        move = 0
        for action in range(48):
            game = copy.deepcopy(tetris)
            game.make_move((action % 12) - 1, int(action / 12), True)
            if not game.lost:
                if count > 0 and game.shapeIndex < len(game.nextShapes):
                    new_move, reward = self.best_move(game, count - 1)
                else:
                    reward = self.get_reward(game)
                if reward > best_score:
                    best_score = reward
                    move = action

        return move, best_score

    def get_reward(self, game):
        heights = np.zeros(10)
        holes = 0
        for col in range(10):
            column = game.grid[:, col]
            nonzeros = np.flatnonzero(column)
            heights[col] = (20 - nonzeros[0]) if len(nonzeros) > 0 else 0
            ceiling = False
            for i in column:
                if i == 0 and ceiling:
                    # found hole
                    holes += 1
                if i > 0:
                    ceiling = True

        agg_height = np.sum(heights)
        lines = 0
        for row in game.grid:
            if len(np.flatnonzero(row)) == len(row):
                lines += 1

        bumpiness = 0
        for col in range(9):
            bumpiness += abs(heights[col] - heights[col + 1])
        reward = -self.heightWeight * agg_height + self.linesWeight * lines - self.holesWeight * holes - self.bumpinessWeight * bumpiness
        return reward
