import random
from math import sqrt, floor
from ai import AI
from tetris_engine import Tetris
import solution
from joblib import Parallel, delayed
import multiprocessing
import random

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


def compute_fitness(candidates):
    for candidate in candidates:
        # ai = AI(candidate.heightWeight, candidate.linesWeight, candidate.holesWeight, candidate.bumpinessWeight)
        total_score = 0
        num_cores = multiprocessing.cpu_count()
        print("Number of cores {0}".format(num_cores))
        results = Parallel(n_jobs=num_cores)(delayed(solution.play_game)(game, i, candidate) for i, game in enumerate(games))
        for result in results:
            total_score += result[1]
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
        idx = randomInteger(0, len(indices))
        selectedIndex = indices[idx: idx+1][0]
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
    candidates[-len(newCandidates):]
    for c in newCandidates:
        candidates.append(c)
    candidates.sort(key=compare_fitness)
    return candidates


def generate_close_values(height, lines, holes, bumpiness):
    case = random.randint(1, 8);
    if case == 1:
        return Candidate(height + random.uniform(0, 0.09), lines, holes, bumpiness)
    if case == 2:
        return Candidate(height, lines + random.uniform(0, 0.09),
                         holes, bumpiness)
    if case == 3:
        return Candidate(height, lines,
                         holes + random.uniform(0, 0.09), bumpiness)
    if case == 4:
        return Candidate(height, lines,
                         holes, bumpiness + random.uniform(0, 0.09))
    if case == 5:
        return Candidate(height - random.uniform(0, 0.09), lines, holes, bumpiness)
    if case == 6:
        return Candidate(height, lines - random.uniform(0, 0.09),
                         holes, bumpiness)
    if case == 7:
        return Candidate(height, lines,
                         holes - random.uniform(0, 0.09), bumpiness)
    if case == 8:
        return Candidate(height, lines,
                         holes, bumpiness - random.uniform(0, 0.9))


def tune():
    candidates = []
    for i in range(0, 100):
        candidates.append(generate_close_values(0.510066, 0.760666, 0.35663, 0.184483))

    # compute first generation
    candidates = compute_fitness(candidates)
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
        candidates = compute_fitness(candidates)
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
