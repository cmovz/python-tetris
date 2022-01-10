import ctypes
import random
from sdl2 import *
from grid import Grid, Collision
from colors import Color
from pieces import pieces
from settings import *

CELL_SIZE = 24
MAP_SIZE = 12, 22
FALLING_PER_SECOND = 1
ACTIONS_PER_SECOND = 12
MAX_FPS = 12
DRAW_TIME = 1000000000 // MAX_FPS

class PossibleFit:
  def __init__(self, fitness, x, rot):
    self.fitness = fitness
    self.x = x
    self.rot = rot

class AI:
  def __init__(self, grid):
    self.grid = grid

  def run(self):
    # possible positions with their fitnesses
    possible_fits = []
  
    for rot in range(4):
      self.grid.piece.pos = rot
      min_x, max_x = self.find_min_max_x()
      for x in range(min_x, max_x + 1):
        # save state
        original_cells_state = [row.copy() for row in self.grid.cells]
        original_piece_pos_state = self.grid.piece_pos.copy()
        original_piece = self.grid.piece
        original_piece_rot = self.grid.piece.pos

        self.grid.piece_pos = [x, 1]
        try:
          while True:
            self.grid.move_piece(0, 1)
        except Collision:
          self.grid.move_piece(0, -1)
      
        filled_rows = self.grid.integrate_piece()
        fitness = (
          filled_rows * 2000
          - self.grid.compute_bumpiness()
          - self.grid.compute_aggregate_height()
          - self.grid.compute_holes()
        )

        possible_fit = PossibleFit(fitness, x, rot)
        possible_fits.append(possible_fit)

        # restore state
        self.grid.cells = original_cells_state
        self.grid.piece_pos = original_piece_pos_state
        self.grid.piece = original_piece
        self.grid.piece.pos = original_piece_rot
    
    self.best_fit = possible_fits[0]
    for possible_fit in possible_fits:
      if possible_fit.fitness > self.best_fit.fitness:
        self.best_fit = possible_fit

  def find_min_max_x(self):
    original_x = self.grid.piece_pos[0]
    min_x = original_x
    max_x = original_x

    try:
      while True:
        min_x -= 1
        self.grid.move_piece(-1, 0)
    except Collision:
      self.grid.move_piece(original_x - min_x, 0)
      min_x += 1

    try:
      while True:
        max_x += 1
        self.grid.move_piece(1, 0)
    except Collision:
      self.grid.move_piece(original_x - max_x, 0)
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
    
    if self.grid.piece.pos != self.best_fit.rot:
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
    while self.grid.piece.pos != self.best_fit.rot:
      self.grid.rotate_piece()

    self.grid.piece_pos[0] = self.best_fit.x

def simulate_game(count):
  scores = []
  for _ in range(count):
    score = 0
    grid = Grid(None, MAP_SIZE[0], MAP_SIZE[1], CELL_SIZE)
    grid.add_piece(random.choice(pieces), 4, 1)
    bot = VirtualBot(grid)
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
        except Collision:
          scores.append(score)
          break
    
  total_score = sum(scores)
  avg_score = total_score // len(scores)
  min_score = min(scores)
  max_score = max(scores)

  print('avg score  :', avg_score)
  print('min score  :', min_score)
  print('max score  :', max_score)

if __name__ == '__main__':
  simulate_game(32)