# import copy
import numpy as np
from tetris import SHAPES

class AI:
    def __init__(self, landingHeightW, linesWeight, rowTransitionW, columnTransitionW, holesWeight, wellsWeight):
        self.landingHeightW = landingHeightW
        self.linesWeight = linesWeight
        self.rowTransitionW = rowTransitionW
        self.columnTransitionW = columnTransitionW
        self.holesWeight = holesWeight
        self.wellsWeight = wellsWeight
        self.grid_system = np.zeros((2304, 20, 10))
        self.index = 0

    def best_move_improved(self, tetris, count):
        best_score, move = -1000, 0
        for action in range(tetris.get_nr_of_actions()):
            # game = tetris.copy()
            self.grid_system[self.index % 2304] = tetris.grid
            game = tetris.copy(self.grid_system[self.index % 2304])
            self.index += 1
            col = (action % 12) - 1
            rot = int(action / 12)
            game.make_move((action % 12) - 1, int(action / 12), True)
            if not game.lost:
                if count > 0 and game.shapeIndex < len(game.shapes):
                    new_move, reward = self.best_move_improved(game, count - 1)
                else:
                    reward = self.get_reward(game, col, rot)
                if reward > best_score:
                    best_score, move = reward, action

        return move, best_score

    def get_reward(self, game, column, rot):
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

        # agg_height = np.sum(heights)
        lines = 0
        for row in game.grid:
            if len(np.flatnonzero(row)) == len(row):
                lines += 1

        reward = self.get_landing_height(game, column,
                                         rot) * -4.500158825082766 + lines * 3.4181268101392694 + self.get_row_transitions(
            game) * -3.2178882868487753 + self.get_column_transitions(
            game) * -9.348695305445199 + holes * -7.899265427351652 + self.get_wells_sum(game) * -3.3855972247263626
        return reward

    def get_landing_height(self, game, column, rot):
        nonzeros = np.flatnonzero(column)
        height = (20 - nonzeros[0]) if len(nonzeros) > 0 else 0
        shape = np.array(SHAPES[game.shapes[game.shapeIndex]])
        shape = np.rot90(shape, -rot)
        return height + (len(shape) / 2)

    def get_row_transitions(self, game):
        transitions = 0;
        last_bit = 1;
        for row in game.grid:
            for j in range(len(row)):
                bit = (row.tolist() >> j) & 1
                if (bit != last_bit):
                    transitions += 1
                last_bit = bit
            if bit == 0:
                transitions += 1
            last_bit = 1
        return transitions

    def get_column_transitions(self, game):
        transitions = 0;
        last_bit = 1;
        for i in range(10):
            for j in range(20):
                row = game.grid[j]
                bit = (row >> i) & 1
                if (bit != last_bit):
                    transitions += 1
                    last_bit = bit
            last_bit = 1
        return transitions

    def get_wells_sum(self, game):
        wells_sum = 0
        for i in range(1, 9):
            for j in range(19, 0, -1):
                if ((((game.grid[j] >> i) & 1) == 0) and
                        (((game.grid[j] >> (i - 1)) & 1) == 1) and
                        (((game.grid[j] >> (i + 1)) & 1) == 1)):
                    wells_sum += 1
                    for k in range(j - 1, 0, -1):
                        if (((game.grid[k] >> i) & 1) == 0):
                            wells_sum += 1
                        else:
                            break

        for j in range(19, 0, -1):
            if ((((game.grid[j] >> 0) & 1) == 0) and
                    (((game.grid[j] >> (0 + 1)) & 1) == 1)):
                wells_sum += 1
            for k in range(j - 1, 0, -1):
                if (((game.grid[k] >> 0) & 1) == 0):
                    wells_sum += 1
                else:
                    break

        for j in range(19, 0, -1):
            if ((((game.grid[j] >> (10 - 1)) & 1) == 0) and
                    (((game.grid[j] >> (10 - 2)) & 1) == 1)):
                wells_sum += 1
                for k in range(j - 1, 0, -1):
                    if (((game.grid[k] >> (10 - 1)) & 1) == 0):
                        wells_sum += 1
                    else:
                        break

        return wells_sum
