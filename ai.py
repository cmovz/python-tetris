import ctypes
import random
import time
from sdl2 import *
from grid import Grid, Collision
from pieces import pieces
from settings import *

A = 0.21057928931169612
B = 0.1360316616998426
C = 0.05293062170804297
D = 0.9709974551768048
E = 0.17149011649058088

class PossibleFit:
  def __init__(self, fitness, x, rot, grid):
    self.fitness = fitness
    self.x = x
    self.rot = rot
    self.grid = grid

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
    possible_fits = []
  
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

        possible_fit = PossibleFit(fitness, x, rot, working_grid)
        possible_fits.append(possible_fit)

      self.grid.piece.rot = original_rot
    
    possible_fits.sort(reverse=True)
    self.original_choice = possible_fits[0]
    possible_fits = possible_fits[:10]
    for fit in possible_fits:
      fit.fitness = self.compute_median_fitness(fit.grid)

    self.best_fit = possible_fits[0]
    for possible_fit in possible_fits:
      if possible_fit.fitness > self.best_fit.fitness:
        self.best_fit = possible_fit
    
    if self.best_fit != self.original_choice:
      print('different choice')
      self.original_choice.grid.draw()
      SDL_UpdateWindowSurface(self.original_choice.grid.window)
      time.sleep(2)
    else:
      print('same choice')
  
  def compute_median_fitness(self, grid):
    possible_fits = []
  
    for piece in pieces:
      grid = grid.copy()
      grid.add_piece(piece, 4, 1)
      for rot in grid.piece.unique_rotations:
        grid.piece.rot = rot
        min_x, max_x = self.find_min_max_x(grid)
        for x in range(min_x, max_x + 1):
          working_grid = grid.copy()

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

          possible_fit = PossibleFit(fitness, x, rot, working_grid)
          possible_fits.append(possible_fit)
    
    possible_fits.sort()
    return (
      possible_fits[(len(possible_fits) - 1) // 2].fitness
      + possible_fits[len(possible_fits) // 2].fitness
    ) / 2
  
  def compute_fitness(self, grid, filled_rows):
    fitness = (
      filled_rows * self.a
      - grid.compute_bumpiness() * self.b
      - grid.compute_aggregate_height() * self.c
      - grid.compute_holes() * self.d
      - grid.compute_wells_depth() * self.e
    )

    if grid.compute_height() >= grid.h - 4:
      fitness -= 100
    
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
  simulate_game(1)