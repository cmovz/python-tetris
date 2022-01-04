from sdl2 import *
from grid import Grid, Collision
from gameclock import GameClock

class ActionHandler:
  def __init__(self, grid, clock, actions_per_second):
    self.grid = grid
    self.clock = GameClock(clock, actions_per_second)
    self.move_left = False
    self.moved_left = True
    self.move_right = False
    self.moved_right = True
    self.rotate = False
    self.rotated = True
    self.accelerate = False
    self.accelerated = True
  
  def start(self):
    self.clock.start()
  
  def handle_keypress_event(self, event):
    if event.type == SDL_KEYDOWN:
      if event.key.keysym.scancode == SDL_SCANCODE_LEFT:
        self.move_left = True
        self.moved_left = False
      elif event.key.keysym.scancode == SDL_SCANCODE_RIGHT:
        self.move_right = True
        self.moved_right = False
      elif event.key.keysym.scancode == SDL_SCANCODE_DOWN:
        self.accelerate = True
        self.accelerated = False
      elif event.key.keysym.scancode == SDL_SCANCODE_UP:
        self.rotate = True
        self.rotated = False

    elif event.type == SDL_KEYUP:
      if event.key.keysym.scancode == SDL_SCANCODE_LEFT:
        self.move_left = False
      elif event.key.keysym.scancode == SDL_SCANCODE_RIGHT:
        self.move_right = False
      elif event.key.keysym.scancode == SDL_SCANCODE_DOWN:
        self.accelerate = False
      elif event.key.keysym.scancode == SDL_SCANCODE_UP:
        self.rotate = False
  
  def execute_actions(self):
    for _ in range(self.clock.get_ticks()):
      if self.move_left or not self.moved_left:
        self.moved_left = True
        try:
          self.grid.move_piece(-1, 0)
        except Collision:
          self.grid.move_piece(1, 0)
      
      if self.move_right or not self.moved_right:
        self.moved_right = True
        try:
          self.grid.move_piece(1, 0)
        except Collision:
          self.grid.move_piece(-1, 0)
      
      if self.accelerate or not self.accelerated:
        self.accelerated = True
        try:
          self.grid.move_piece(0, 1)
        except Collision:
          self.grid.move_piece(0, -1)
      
      if self.rotate or not self.rotated:
        self.rotated = True
        try:
          self.grid.rotate_piece()
        except Collision:
          self.grid.rotate_piece_backwards()