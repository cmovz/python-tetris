import ctypes
from sdl2 import *
from grid import Collision
from colors import Color

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
      for x in range(min_x, max_x):
        # save state
        original_cells_state = [row.copy() for row in self.grid.cells]
        original_piece_pos_state = self.grid.piece_pos.copy()
        original_piece = self.grid.piece
        original_piece_rot = self.grid.piece.pos

        holes0 = self.compute_holes_penalty(self.grid)

        self.grid.piece_pos = [x, 1]
        try:
          while True:
            self.grid.move_piece(0, 1)
        except Collision:
          self.grid.move_piece(0, -1)
      
        filled_rows = self.grid.integrate_piece()
        height = self.grid.compute_height()
        height_penalty = height * 100
        holes = self.compute_holes_penalty(self.grid)
        holes_penalty = (holes - holes0) * 10
        fitness = (
          filled_rows * 1000
          - height_penalty
          - holes_penalty
          - (self.grid.compute_horizontal_space())
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
      print(possible_fit.fitness)
      if possible_fit.fitness > self.best_fit.fitness:
        self.best_fit = possible_fit
    
    print('chose:', self.best_fit.fitness)
  
  @staticmethod
  def compute_holes_penalty(grid):
    visited = set()
    total_hole_penalty = 0
    height = grid.compute_height()

    for y in range(grid.h - 1, 2, -1):
      row = grid.cells[y]
      for x in range(1, grid.w - 1):
        if row[x] == Color.BLACK:
          hole_penalty = 1
          for y1 in range(y - 1, grid.h - height, -1):
            if (x, y1) in visited:
              break

            visited.add((x, y1))
            if grid.cells[y1][x] == Color.BLACK:
              hole_penalty += 1
            else:
              total_hole_penalty += hole_penalty
              break
    
    return total_hole_penalty

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
      #max_x -= 1
    
    return min_x, max_x
  
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