from tetris_engine import Tetris, OFFSETS
# from tetris import Tetris
from ai import AI
from joblib import Parallel, delayed
import multiprocessing
import time
from datetime import datetime
import cProfile
import numpy as np

games = []
def read_games():
    with open('games.txt') as games_file:
        for line in games_file:
            games.append(line.rstrip())

def play_game(game, counter, candidate = None):
    if candidate is not None:
        ai = AI(candidate.heightWeight, candidate.linesWeight, candidate.holesWeight, candidate.bumpinessWeight, candidate.weighted
                , candidate.relative)
    else:
        ai = AI(0.510066, 0.760666, 0.35663, 0.184483)
    moves = []
    tetris = Tetris(game, np.zeros((20, 10)))
    for i in range(len(game)):
        if not (tetris.won or tetris.lost):
            action, score = ai.best_move_improved(tetris, 1)
            move = (int((action % 12) - 1), int(action / 12))
            tetris.make_move(move[0], move[1])
            moves.append((move[0] + OFFSETS[game[i]][move[1]], move[1]))
        else:
            if tetris.lost:
                print("Game over")
                break
    print("Game with number {0} has score {1}".format(counter, tetris.score))
    return ';'.join(['{}:{}'.format(a,b) for a,b in moves]), tetris.score, counter



def test():
    num_cores = multiprocessing.cpu_count()
    print("Number of cores {0}".format(num_cores))
    results = Parallel(n_jobs=num_cores)(delayed(play_game)(game, i) for i, game in enumerate(games))
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    total_score = 0
    with open('submissions/{0}.txt'.format(timestamp), 'w') as submission:
        for result in results:
            total_score += result[1]
            submission.write('{0},{1}\n'.format(result[2], result[0]))
    print("Total score is {0} ".format(total_score))



if __name__ == '__main__':
    start = time.time()
    read_games()
    test()
    print("ran in %d s" % (time.time() - start))
