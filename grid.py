import ctypes
from sdl2 import SDL_BlitSurface, SDL_Rect
from colors import Color
from textures import textures
from pieces import Piece

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
  
  def copy(self):
    grid_copy = Grid(self.window_surface, self.w, self.h, self.cell_size)
    grid_copy.cells = [row.copy() for row in self.cells]
    try:
      grid_copy.piece = Piece(
        self.piece.matrices,
        self.piece.color,
        self.piece.unique_rotations
      )
      grid_copy.piece.rot = self.piece.rot
      grid_copy.piece_pos = self.piece_pos.copy()
    except AttributeError:
      pass

    return grid_copy
  
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
    
    try:
      self.draw_piece()
    except AttributeError:
      pass
  
  def draw_piece(self):
    dest_rect = SDL_Rect(w=self.cell_size, h=self.cell_size)

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
  
  def compute_height(self):
    for y in range(1, self.h - 1):
      for x in range(1, self.w -1):
        if self.cells[y][x] != Color.BLACK:
          return self.h - y - 1
    
    return 0
  
  def compute_aggregate_height(self):
    agg_height = 0
    for x in range(1, self.w - 1):
      for y in range(1, self.h - 1):
        if self.cells[y][x] != Color.BLACK:
          agg_height += self.h - y - 1
    
    return agg_height
  
  def compute_bumpiness(self):
    heights = []
    for x in range(1, self.w - 1):
      for y in range(1, self.h - 1):
        if self.cells[y][x] != Color.BLACK:
          heights.append(self.h - y - 1)
          break
    
    bumpiness = 0
    for i in range(1, len(heights)):
      bumpiness += abs(heights[i-1] - heights[i])
    
    return bumpiness
  
  def compute_holes(self):
    visited = set()
    total = 0

    for y in range(self.h - 1, 2, -1):
      row = self.cells[y]
      for x in range(1, self.w - 1):
        if row[x] == Color.BLACK:
          hole_size = 1
          for y1 in range(y - 1, 1, -1):
            if (x, y1) in visited:
              break

            visited.add((x, y1))
            if self.cells[y1][x] == Color.BLACK:
              hole_size += 1
            else:
              total += hole_size
              break
    
    return total

  def compute_wells_depth(self):
    total_depth = 0

    for x in range(1, self.w - 1):
      y = 1
      while y < self.h - 1:
        if (
          self.cells[y][x] == Color.BLACK
          and self.cells[y][x-1] != Color.BLACK
          and self.cells[y][x+1] != Color.BLACK
        ):
          depth = 1
          y += 1

          while self.cells[y][x] == Color.BLACK:
            depth += 1
            y += 1

          if depth >= 3:
            total_depth += depth
          
          break
        
        y += 1

    return total_depth