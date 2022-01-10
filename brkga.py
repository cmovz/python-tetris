'''
This module implements a genetic algorithm to find A, B, C and D.
Run `python3 brkga.py` or `pypy3 brkga.py`, which is 10x faster.
'''

import math
import random
import ai

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

    self.population = []
    for _ in range(individual_count):
      # individual: fitness + alleles
      i = [random.uniform(0,1) for _ in range(alleles_per_individual + 1)]
      self.population.append(i)
      
  
  def evolve(self):
    self.population.sort(reverse=True)
    
    elite_pool = self.population[:self.elite_count]
    general_pool = self.population[self.elite_count:]
    temp_pool = []
    mating_count = len(self.population) - self.elite_count - self.mutant_count

    for _ in range(mating_count):
      elite_individual = random.choice(elite_pool)
      random_individual = random.choice(general_pool)

      new_individual = []
      for allele in range(1, len(self.alleles_per_individual + 1)):
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

if __name__ == '__main__':
  brkga = BRKGA(4, 100, 10, 10, 0.7)
  for generation in range(100):
    for individual in brkga.population:
      _, a, b, c, d = individual
      fitness = ai.simulate_game(16, a, b, c, d, False)
      individual[0] = fitness
    
    brkga.evolve()

    best_individual = brkga.population[0]
    print('-' * 20)
    print('generation:', generation)
    print('fitness:', best_individual[0])
    print('a:', best_individual[1])
    print('b:', best_individual[2])
    print('c:', best_individual[3])
    print('d:', best_individual[4])
    print('-' * 20, flush=True)