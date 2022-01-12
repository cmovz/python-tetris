'''
This module implements a genetic algorithm to find A, B, C and D.
Run `python3 brkga.py` or `pypy3 brkga.py`, which is 10x faster.
'''

import math
import random
import pickle
import ai
from pathlib import Path
from multiprocessing import Pool 

class BRKGA:
  def __init__(
    self, alleles_per_individual, individual_count, elite_percentage,
    mutant_percentage, elite_chances
  ):
    self.alleles_per_individual = alleles_per_individual
    self.individual_count = individual_count
    self.elite_count = math.floor(elite_percentage * individual_count)
    self.mutant_count = math.floor(mutant_percentage * individual_count)
    self.elite_chances = elite_chances
    self.generation = 0

    self.population = []
    for _ in range(individual_count):
      # individual: fitness + alleles
      i = [random.uniform(0,1) for _ in range(alleles_per_individual + 1)]
      self.population.append(i)
      
  
  def evolve(self):
    # self.population.sort(reverse=True)
    # population must be sorted descending by fitness
    
    self.generation += 1
    elite_pool = self.population[:self.elite_count]
    general_pool = self.population[self.elite_count:]
    temp_pool = []
    mating_count = len(self.population) - self.elite_count - self.mutant_count

    for _ in range(mating_count):
      elite_individual = random.choice(elite_pool)
      random_individual = random.choice(general_pool)

      new_individual = [0.0]
      for allele in range(1, self.alleles_per_individual + 1):
        if random.uniform(0,1) < self.elite_chances:
          new_individual.append(elite_individual[allele])
        else:
          new_individual.append(random_individual[allele])
      
      temp_pool.append(new_individual)
    
    mutant_pool = [
      [random.uniform(0,1) for _ in range(self.alleles_per_individual + 1)]
      for _ in range(self.mutant_count)
    ]

    self.population = elite_pool + temp_pool + mutant_pool

class TetrisBRKGA(BRKGA):
  def __init__(self, fitness_simulation_count):
    BRKGA.__init__(self, 5, 50, 0.2, 0.4, 0.7)
    self.fitness_simulation_count = fitness_simulation_count
  
  def evolve(self):
    with Pool(processes=2) as pool:
      results = []
      for individual in self.population:
        _, a, b, c, d, e = individual
        r = pool.apply_async(ai.simulate_game, (16, a, b, c, d, e, False, True))
        results.append(r)
      
      for i, r in enumerate(results):
        fitness = r.get()
        self.population[i][0] = fitness
    
    self.population.sort(reverse=True)
    self.save_population()
    BRKGA.evolve(self)
  
  def save_population(self):
    file = open('./tmp/{}'.format(self.generation), 'wb')
    pickle.dump(self, file)
    file.close()

if __name__ == '__main__':
  Path('./tmp').mkdir(exist_ok=True)
  brkga = TetrisBRKGA(16)
  for generation in range(100):  
    brkga.evolve()

    best_individual = brkga.population[0]
    print('-' * 20)
    print('generation:', generation)
    print('fitness:', best_individual[0])
    print('A =', best_individual[1])
    print('B =', best_individual[2])
    print('C =', best_individual[3])
    print('D =', best_individual[4])
    print('E =', best_individual[5])
    print('-' * 20)