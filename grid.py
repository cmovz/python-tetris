import ctypes
from sdl2 import SDL_BlitSurface, SDL_Rect
from colors import Color
from textures import textures
from pieces import pieces

class Collision(Exception):
  pass

class Grid:
  def __init__(self, window_surface, width, height, cell_size):
    self.window_surface = window_surface
    self.w = width
    self.h = height
    self.cell_size = cell_size
    self.cells = []

    # top wall
    self.cells.append([Color.GRAY for _ in range(self.w)])

    for _ in range(self.h - 2):
      # walls + empty cells
      row = [Color.GRAY] + [Color.BLACK for _ in range(self.w-2)] + [Color.GRAY]
      self.cells.append(row)
    
    # bottom wall
    self.cells.append([Color.GRAY for _ in range(self.w)])
  
  def add_piece(self, piece, x, y):
    self.piece = piece
    self.piece_pos = [x, y]
    if self.is_there_collision():
      raise Collision()
  
  def rotate_piece(self):
    self.piece.rotate()
    if self.is_there_collision():
      raise Collision()
  
  def rotate_piece_backwards(self):
    self.piece.rotate_backwards()
    if self.is_there_collision():
      raise Collision()
  
  def move_piece(self, x, y):
    self.piece_pos[0] += x
    self.piece_pos[1] += y
    if self.is_there_collision():
      raise Collision()

  def integrate_piece(self):
    '''
    Adds the piece's cells to the grid and remove the piece.
    Clears the filled rows and returns how many rows were cleared.
    '''
    cleared_rows = 0

    for y, row in enumerate(self.piece.matrix):
      for x, filled in enumerate(row):
        if not filled:
          continue

        self.cells[self.piece_pos[1]+y][self.piece_pos[0]+x] = self.piece.color
    
    for y, row in enumerate(self.piece.matrix):
      for has_block in row:
        if has_block:
          break

      if has_block:
        for _, color in enumerate(self.cells[self.piece_pos[1] + y]):
          if color == Color.BLACK:
            break
        else:
          cleared_rows += 1
          first_row = [Color.GRAY for _ in range(self.w)]
          second_row = (
            [Color.GRAY] + [Color.BLACK for _ in range(self.w-2)] + [Color.GRAY]
          )
          del self.cells[self.piece_pos[1] + y]
          del self.cells[0]
          self.cells[:0] = first_row, second_row

    del self.piece
    del self.piece_pos

    return cleared_rows

  def is_there_collision(self):
    for y, row in enumerate(self.piece.matrix):
      for x, filled in enumerate(row):
        if not filled:
          continue
        if self.cells[self.piece_pos[1]+y][self.piece_pos[0]+x] != Color.BLACK:
          return True

    return False
  
  def draw(self):
    dest_rect = SDL_Rect()
    dest_rect.w = self.cell_size
    dest_rect.h = self.cell_size
    for y, row in enumerate(self.cells):
      for x, cell in enumerate(row):
        dest_rect.x = x * self.cell_size
        dest_rect.y = y * self.cell_size
        SDL_BlitSurface(
          textures[cell],
          None,
          self.window_surface,
          ctypes.byref(dest_rect)
        )
    
    if self.piece:
      self.draw_piece()
  
  def draw_piece(self):
    dest_rect = SDL_Rect()
    dest_rect.w = self.cell_size
    dest_rect.h = self.cell_size

    for y, row in enumerate(self.piece.matrix):
      for x, filled in enumerate(row):
        if not filled:
          continue
        
        dest_rect.x = (self.piece_pos[0] + x) * self.cell_size
        dest_rect.y = (self.piece_pos[1] + y) * self.cell_size
        SDL_BlitSurface(
          textures[self.piece.color],
          None,
          self.window_surface,
          ctypes.byref(dest_rect)
        )