import sys
import os
import ctypes
import random
from sdl2 import *
from sdl2.sdlttf import *
from grid import Grid, Collision
from pieces import pieces
from gameclock import GameClock, Clock
from actionhandler import ActionHandler

CELL_SIZE = 24
MAP_SIZE = 12, 22
FALLING_PER_SECOND = 1
ACTIONS_PER_SECOND = 12
MAX_FPS = 12
DRAW_TIME = 1000000000 // MAX_FPS

def run():
  SDL_Init(SDL_INIT_VIDEO)

  window = SDL_CreateWindow(
    b'Tetris', SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 
    MAP_SIZE[0] * CELL_SIZE, MAP_SIZE[1] * CELL_SIZE, SDL_WINDOW_SHOWN
  )
  window_surface = SDL_GetWindowSurface(window)

  path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'images',
    'OpenSans-Regular.ttf'
  )
  TTF_Init()
  font = TTF_OpenFont(path.encode(), 32)

  grid = Grid(window_surface, MAP_SIZE[0], MAP_SIZE[1], CELL_SIZE)
  grid.add_piece(random.choice(pieces), 4, 1)

  clock = Clock()
  game_clock = GameClock(clock, FALLING_PER_SECOND)
  game_clock.start()
  action_handler = ActionHandler(grid, clock, ACTIONS_PER_SECOND)
  action_handler.start()

  score = 0
  running = True
  event = SDL_Event()
  while running:
    clock.update_time()
    t0 = clock.time

    while SDL_PollEvent(ctypes.byref(event)):
      if event.type == SDL_QUIT:
        running = False

      action_handler.handle_keypress_event(event)
    
    action_handler.execute_actions()
    
    for _ in range(game_clock.get_ticks()):
      try:
        grid.move_piece(0, 1)
      except Collision:
        try:
          grid.move_piece(0, -1)
          score += grid.integrate_piece()
          new_piece = random.choice(pieces)
          new_piece.reset_rotation()
          grid.add_piece(new_piece, 4, 1)
        except Collision:
          print('Game over')
          running = False
    
    grid.draw()

    # draw score
    text = str(score).encode()
    w = ctypes.c_int()
    h = ctypes.c_int()
    TTF_SizeText(font, text, ctypes.byref(w), ctypes.byref(h))
    dest_rect = SDL_Rect(
      (MAP_SIZE[0] - 1) * CELL_SIZE - w.value - 8,
      CELL_SIZE,
      w.value,
      h.value
    )
    color = SDL_Color(255, 255, 255)
    text_surface = TTF_RenderText_Blended(font, text, color)
    SDL_BlitSurface(text_surface, None, window_surface, ctypes.byref(dest_rect))
    SDL_FreeSurface(text_surface)

    SDL_UpdateWindowSurface(window)
    
    clock.update_time()
    t1 = clock.time
    dt = t1 - t0
    if dt < DRAW_TIME:
      SDL_Delay((DRAW_TIME - dt) // 1000000)
    
  SDL_DestroyWindow(window)
  SDL_Quit()
  return 0

if __name__ == '__main__':
  sys.exit(run())