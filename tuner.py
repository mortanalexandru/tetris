import random
from math import sqrt, floor
from ai import AI
from tetris_engine import Tetris

games = []


class Candidate:
    def __init__(self, heightWeight, linesWeight, holesWeight, bumpinessWeight):
        self.heightWeight = heightWeight
        self.linesWeight = linesWeight
        self.holesWeight = holesWeight
        self.bumpinessWeight = bumpinessWeight
        self.fitness = 0


def generateRandomCandidate():
    candidate = Candidate(random.random() - 0.5, random.random() - 0.5, random.random() - 0.5, random.random() - 0.5)
    normalize(candidate);
    return candidate;


def normalize(candidate):
    norm = sqrt(
        candidate.heightWeight * candidate.heightWeight + candidate.linesWeight * candidate.linesWeight + candidate.holesWeight * candidate.holesWeight + candidate.bumpinessWeight * candidate.bumpinessWeight);
    candidate.heightWeight /= norm;
    candidate.linesWeight /= norm;
    candidate.holesWeight /= norm;
    candidate.bumpinessWeight /= norm;
    return candidate

def compare_fitness(c):
    return c.fitness


def compute_fitness(candidates, nrGames):
    for candidate in candidates:
        ai = AI(candidate.heightWeight, candidate.linesWeight, candidate.holesWeight, candidate.bumpinessWeight)
        total_score = 0
        prev_score = {}
        for i in range(0, nrGames):
            game = games[i]
            board = Tetris(game)
            for piece in game:
                if not (game.won or game.lost):
                    move = ai.move(board)
                    board.make_move(move[0], move[1])
                else:
                    print("Game over")
            total_score += board.score
        candidate.fitness = total_score
    return candidates


def read_games():
    with open('games.txt') as games_file:
        for line in games_file:
            games.append(line.rstrip())


def randomInteger(min, max):
    return floor(random.random() * (max - min) + min);


def tournament_select(candidates, ways):
    indices = [];
    for i, c in enumerate(candidates):
        indices.append(i)

    fittestCandidateIndex1 = None;
    fittestCanddiateIndex2 = None;
    for i in range(0, ways):
        selectedIndex = indices.splice(randomInteger(0, indices.length), 1)[0]
        if (fittestCandidateIndex1 is None or selectedIndex < fittestCandidateIndex1):
            fittestCanddiateIndex2 = fittestCandidateIndex1;
            fittestCandidateIndex1 = selectedIndex;
        elif (fittestCanddiateIndex2 is None or selectedIndex < fittestCanddiateIndex2):
            fittestCanddiateIndex2 = selectedIndex;

    return [candidates[fittestCandidateIndex1], candidates[fittestCanddiateIndex2]];


def cross_over(candidate1, candidate2):
    candidate = Candidate(candidate1.fitness * candidate1.heightWeight + candidate2.fitness * candidate2.heightWeight,
                          candidate1.fitness * candidate1.linesWeight + candidate2.fitness * candidate2.linesWeight,
                          candidate1.fitness * candidate1.holesWeight + candidate2.fitness * candidate2.holesWeight,
                          candidate1.fitness * candidate1.bumpinessWeight + candidate2.fitness * candidate2.bumpinessWeight)
    normalize(candidate);
    return candidate;

def mutate(candidate):
    quantity = random.random() * 0.4 - 0.2;
    random_int = randomInteger(0, 4)
    if random_int == 0:
        candidate.heightWeight += quantity;
    if random_int == 1:
        candidate.linesWeight += quantity;
    if random_int == 2:
        candidate.holesWeight += quantity;
    if random_int == 3:
        candidate.bumpinessWeight += quantity;
    return candidate

def deleteNLastReplacement(candidates, newCandidates):
    candidates.slice(-newCandidates.length);
    for c in newCandidates:
        candidates.append(c)
    candidates.sort(key=compare_fitness)
    return candidates


def tune():
    candidates = []
    for i in range(0, 1000):
        candidates.push(generateRandomCandidate())

    # compute first generation
    candidates = compute_fitness(candidates, 60)
    candidates.sort(key=compare_fitness)

    count = 0;
    while True:
        newCandidates = [];
        for i in range(0, 30):
            pair = tournament_select(candidates, 10)
            candidate = cross_over(pair[0], pair[1])
            if(random.random() < 0.05):
                candidate = mutate(candidate)
            candidate = normalize(candidate)
            newCandidates.append(candidate)
        print("Computing fitnesses of new candidates {0}".format(count))
        candidates = compute_fitness(candidates, 60)
        candidates = deleteNLastReplacement(candidates, newCandidates)
        total_fitness = 0
        for c in candidates:
            total_fitness += c.fitness
        print("Average fitness = {0}".format((total_fitness / len(candidates))))
        print("Highest fitness = {0} for run nr {1}".format(candidates[0], count))
        print("Fittest candidate = {0} {1} {2} {3} for run nr {1}".format(candidates[0].heightWeight, candidates[0].linesWeight, candidates[0].holesWeight, candidates[0].bumpinessWeight, count))
        count += 1

if __name__ == '__main__':
    read_games()
    tune()
