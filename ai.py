import ctypes
import random
from sdl2 import *
from grid import Grid, Collision
from pieces import pieces
from settings import *
from multiprocessing import Pool

A = 0.11146253876595202
B = 0.12392743901965475
C = 0.029653844701920895
D = 0.9624658982587024
E = 0.32341412515044743

class PossibleFit:
  def __init__(self, fitness, x, rot, grid):
    self.fitness = fitness
    self.x = x
    self.rot = rot
    self.grid = grid
    self.hole_count = grid.holes

  def __lt__(self, other):
    return self.fitness < other.fitness

class AI:
  def __init__(self, grid, a=A, b=B, c=C, d=D, e=E):
    self.grid = grid
    self.a = a
    self.b = b
    self.c = c
    self.d = d
    self.e = e
  
  def run(self):
    # possible positions with their fitnesses
    best_fitness = -10000000000.0
    for rot in self.grid.piece.unique_rotations:
  
      original_rot = self.grid.piece.rot
      self.grid.piece.rot = rot
      min_x, max_x = self.find_min_max_x(self.grid)
      for x in range(min_x, max_x + 1):
        working_grid = self.grid.copy()

        working_grid.piece_pos = [x, 1]
        game_over = False
        try:
          while True:
            working_grid.move_piece(0, 1)
        except Collision:
          try:
            working_grid.move_piece(0, -1)
          except Collision:
            game_over = True
      
        if not game_over:
          filled_rows = working_grid.integrate_piece()
          fitness = self.compute_fitness(working_grid, filled_rows)
        else:
          fitness = -10000000000.0
        
        if fitness > best_fitness:
          best_fitness = fitness
          self.best_fit = PossibleFit(fitness, x, rot, working_grid)

      self.grid.piece.rot = original_rot    
 
  def compute_fitness(self, grid, filled_rows):
    fitness = (
      filled_rows * self.a
      - grid.bumpiness * self.b
      - grid.aggregate_height * self.c
      - grid.holes * self.d
      - grid.wells_depth * self.e
    )

    return fitness

  @staticmethod
  def find_min_max_x(grid):
    original_x = grid.piece_pos[0]
    min_x = original_x
    max_x = original_x

    try:
      while True:
        min_x -= 1
        grid.move_piece(-1, 0)
    except Collision:
      grid.move_piece(original_x - min_x, 0)
      min_x += 1

    try:
      while True:
        max_x += 1
        grid.move_piece(1, 0)
    except Collision:
      grid.move_piece(original_x - max_x, 0)
      max_x -= 1
    
    return min_x, max_x


class Bot(AI):  
  def adjust_position(self):
    moved = False
    x = self.grid.piece_pos[0]
    if x < self.best_fit.x:
      self.send_keypress(SDL_SCANCODE_RIGHT)
      moved = True
    elif x > self.best_fit.x:
      self.send_keypress(SDL_SCANCODE_LEFT)
      moved = True
    
    if self.grid.piece.rot != self.best_fit.rot:
      self.send_keypress(SDL_SCANCODE_UP)
      moved = True

    if not moved:
      self.send_keypress(SDL_SCANCODE_DOWN)
  
  def send_keypress(self, scancode):
    new_event = SDL_Event()
    new_event.type = SDL_KEYDOWN
    new_event.key.keysym.scancode = scancode
    SDL_PushEvent(ctypes.byref(new_event))
    new_event.type = SDL_KEYUP
    SDL_PushEvent(ctypes.byref(new_event))


class VirtualBot(AI):
  def adjust_position(self):
    self.grid.piece.rot = self.best_fit.rot
    self.grid.piece_pos[0] = self.best_fit.x

def simulate_game(count, a=A, b=B, c=C, d=D, e=E, print_stats=True, stop=False):
  scores = []
  for _ in range(count):
    score = 0
    grid = Grid(None, MAP_SIZE[0], MAP_SIZE[1], CELL_SIZE, None)
    grid.add_piece(random.choice(pieces), 4, 1)
    bot = VirtualBot(grid, a, b, c, d)
    bot.run()

    while True:
      bot.adjust_position()
      try:
        while True:
          grid.move_piece(0, 1)
      except Collision:
        try:
          grid.move_piece(0, -1)
          score += grid.integrate_piece()
          new_piece = random.choice(pieces)
          new_piece.reset_rotation()
          grid.add_piece(new_piece, 4, 1)
          bot.run()

          if stop and score >= 800:
            scores.append(score)
            break

        except Collision:
          scores.append(score)
          break      
    
  scores.sort()
  min_score = scores[0]
  max_score = scores[-1]
  total_score = sum(scores)
  avg_score = total_score / len(scores)
  median_score = (scores[(len(scores) - 1)//2] + scores[len(scores)//2]) / 2

  if print_stats:
    print('-' * 40)
    print('median     :', median_score)
    print('avg score  :', avg_score)
    print('min score  :', min_score)
    print('max score  :', max_score)
    print('-' * 40)
    print(sorted(scores))

  return median_score

if __name__ == '__main__':
  simulate_game(100)