import sys
import ctypes
import random
from sdl2 import *
from grid import Grid, Collision
from pieces import pieces
from gameclock import GameClock, Clock
from actionhandler import ActionHandler

CELL_SIZE = 24
MAP_SIZE = 12, 22
TICKS_PER_SECOND = 1
ACTIONS_PER_SECOND = 12

def run():
  SDL_Init(SDL_INIT_VIDEO)

  window = SDL_CreateWindow(
    b'Tetris', SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 
    MAP_SIZE[0] * CELL_SIZE, MAP_SIZE[1] * CELL_SIZE, SDL_WINDOW_SHOWN
  )
  window_surface = SDL_GetWindowSurface(window)

  grid = Grid(window_surface, MAP_SIZE[0], MAP_SIZE[1], CELL_SIZE)
  grid.add_piece(random.choice(pieces), 4, 1)

  clock = Clock()
  game_clock = GameClock(clock, TICKS_PER_SECOND)
  game_clock.start()
  action_handler = ActionHandler(grid, clock, ACTIONS_PER_SECOND)
  action_handler.start()

  running = True
  event = SDL_Event()
  while running:
    clock.update_time()

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
          grid.integrate_piece()
          grid.add_piece(random.choice(pieces), 4, 1)
        except Collision:
          print('Game over')
          running = False
    
    grid.draw()
    SDL_UpdateWindowSurface(window)
    SDL_Delay(1)
    
  SDL_DestroyWindow(window)
  SDL_Quit()
  return 0

if __name__ == '__main__':
  sys.exit(run())