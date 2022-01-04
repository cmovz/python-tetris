from colors import Color
from sdl2 import SDL_LoadBMP
import os

textures = {}

for e in Color:
  path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'images',
    e.name.lower() + '.bmp',
  )
  textures[e] = SDL_LoadBMP(path.encode())