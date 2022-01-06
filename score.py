import ctypes
from sdl2.sdlttf import *
from sdl2 import SDL_BlitSurface, SDL_Color, SDL_FreeSurface, SDL_Rect
from utils import get_resource_path

class Score:
  def __init__(self, dest_surface, x=0, y=0):
    path = get_resource_path('images', 'OpenSans-Regular.ttf')
    self.font = TTF_OpenFont(path.encode(), 32)
    self.score = 0
    self.dest_surface = dest_surface
    self.x = x
    self.y = y

    self.make_surface()
  
  def __del__(self):
    SDL_FreeSurface(self.text_surface)
    TTF_CloseFont(self.font)
  
  def make_surface(self):
    try:
      SDL_FreeSurface(self.text_surface)
    except AttributeError:
      pass
    
    text = str(self.score).encode()
    w = ctypes.c_int()
    h = ctypes.c_int()
    TTF_SizeText(self.font, text, ctypes.byref(w), ctypes.byref(h))
    self.dest_rect = SDL_Rect(self.x - w.value, self.y, w.value, h.value)
    color = SDL_Color(255, 255, 255)
    self.text_surface = TTF_RenderText_Blended(self.font, text, color)
  
  def draw(self):
    SDL_BlitSurface(
      self.text_surface,
      None,
      self.dest_surface,
      ctypes.byref(self.dest_rect)
    )
  
  def add(self, count=1):
    self.score += count
    self.make_surface()