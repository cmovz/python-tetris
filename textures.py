import os
from colors import Color
from sdl2 import SDL_LoadBMP
from utils import get_resource_path

textures = {}

for e in Color:
  path = get_resource_path('images', e.name.lower() + '.bmp')
  textures[e] = SDL_LoadBMP(path.encode())