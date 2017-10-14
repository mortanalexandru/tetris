import random
from math import sqrt, floor
from ai import AI
from tetris_engine import Tetris
import solution
from joblib import Parallel, delayed
import multiprocessing
import random
import time
from datetime import datetime

games = []


class Candidate:
    def __init__(self, heightWeight, linesWeight, holesWeight, bumpinessWeight, weighted, relative):
        self.heightWeight = heightWeight
        self.linesWeight = linesWeight
        self.holesWeight = holesWeight
        self.bumpinessWeight = bumpinessWeight
        self.weighted = weighted
        self.relative = relative
        self.fitness = 0


def generateRandomCandidate():
    candidate = Candidate(random.random() - 0.5, random.random() - 0.5, random.random() - 0.5, random.random() - 0.5)
    normalize(candidate);
    return candidate;



def normalize(candidate):
    norm = sqrt(
        candidate.heightWeight * candidate.heightWeight + candidate.linesWeight * candidate.linesWeight + candidate.holesWeight * candidate.holesWeight + candidate.bumpinessWeight * candidate.bumpinessWeight + candidate.weighted * candidate.weighted + candidate.relative * candidate.relative);
    candidate.heightWeight /= norm;
    candidate.linesWeight /= norm;
    candidate.holesWeight /= norm;
    candidate.bumpinessWeight /= norm;
    candidate.weighted /= norm;
    candidate.relative /= norm;
    return candidate

def compare_fitness(c):
    return c.fitness


def compute_fitness(candidates):
    for count,candidate in enumerate(candidates):
        start = time.time()
        total_score = 0
        num_cores = multiprocessing.cpu_count()
        print("Number of cores {0}".format(num_cores))
        results = Parallel(n_jobs=num_cores)(delayed(solution.play_game)(game, i, candidate) for i, game in enumerate(games))
        for result in results:
            total_score += result[1]
        candidate.fitness = total_score
        print("candidate {0} has fitness {1}".format(count, total_score))
        print("ran in %d s" % (time.time() - start))
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


def generate_close_values(height, lines, holes, bumpiness, weighted, relative):
    case = random.randint(1, 11);
    if case == 1:
        return Candidate(height + random.uniform(0, 0.9), lines, holes, bumpiness, weighted, relative)
    if case == 2:
        return Candidate(height, lines + random.uniform(0, 0.9),
                         holes, bumpiness, weighted, relative)
    if case == 3:
        return Candidate(height, lines,
                         holes + random.uniform(0, 0.9), bumpiness, weighted, relative)
    if case == 4:
        return Candidate(height, lines,
                         holes, bumpiness + random.uniform(0, 0.9), weighted, relative)
    if case == 5:
        return Candidate(height - random.uniform(0, 0.9), lines, holes, bumpiness, weighted, relative)
    if case == 6:
        return Candidate(height, lines - random.uniform(0, 0.9),
                         holes, bumpiness, weighted, relative)
    if case == 7:
        return Candidate(height, lines,
                         holes - random.uniform(0, 0.9), bumpiness, weighted, relative)
    if case == 8:
        return Candidate(height, lines,
                         holes, bumpiness - random.uniform(0, 0.9), weighted, relative)
    if case == 8:
        return Candidate(height, lines,
                         holes, bumpiness, weighted + random.uniform(0, 0.9), relative)
    if case == 9:
        return Candidate(height, lines,
                         holes, bumpiness, weighted - random.uniform(0, 0.9), relative)
    if case == 10:
        return Candidate(height, lines,
                         holes, bumpiness - random.uniform(0, 0.9), weighted, relative + random.uniform(0, 0.9))
    if case == 11:
        return Candidate(height, lines,
                         holes, bumpiness - random.uniform(0, 0.9), weighted, relative - random.uniform(0, 0.9))


def tune():
    candidates = []
    for i in range(0, 100):
        candidates.append(normalize(generate_close_values(- 0.6152727732730796, 0.22568649650722883, -0.15452215909537684, -0.021586109522043928, -0.6152727732730796 , -0.15452215909537684)))

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
