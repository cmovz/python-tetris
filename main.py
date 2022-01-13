import sys
import ctypes
import random
from sdl2 import *
from sdl2.sdlttf import TTF_Init, TTF_Quit
from grid import Grid, Collision
from pieces import pieces
from gameclock import GameClock, Clock
from actionhandler import ActionHandler
from score import Score
from ai import Bot
from settings import *

def run():
  SDL_Init(SDL_INIT_VIDEO)
  TTF_Init()

  window = SDL_CreateWindow(
    b'Tetris', SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 
    MAP_SIZE[0] * CELL_SIZE, MAP_SIZE[1] * CELL_SIZE, SDL_WINDOW_SHOWN
  )
  window_surface = SDL_GetWindowSurface(window)

  grid = Grid(window_surface, MAP_SIZE[0], MAP_SIZE[1], CELL_SIZE, window)
  grid.add_piece(random.choice(pieces), 4, 1)

  clock = Clock()
  game_clock = GameClock(clock, FALLING_PER_SECOND)
  game_clock.start()
  action_handler = ActionHandler(grid, clock, ACTIONS_PER_SECOND)
  action_handler.start()
  score = Score(window_surface, (MAP_SIZE[0] - 1) * CELL_SIZE - 8, CELL_SIZE)

  if '--ai' in sys.argv:
    ai = Bot(grid)
    ai.run()
  else:
    ai = False

  running = True
  event = SDL_Event()
  while running:
    clock.update_time()
    t0 = clock.time

    if ai:
      ai.adjust_position()

    while SDL_PollEvent(ctypes.byref(event)):
      if event.type == SDL_QUIT:
        running = False

      action_handler.handle_keypress_event(event)
    
    action_handler.execute_actions()
    print('wells depth:', grid.compute_wells_depth())
    
    for _ in range(game_clock.get_ticks()):
      try:
        grid.move_piece(0, 1)
      except Collision:
        try:
          grid.move_piece(0, -1)
          score.add(grid.integrate_piece())
          new_piece = random.choice(pieces)
          new_piece.reset_rotation()
          grid.add_piece(new_piece, 4, 1)
          if ai:
            ai.run()
        except Collision:
          print('-' * 40)
          print('Game over')
          print('You scored:', score.score)
          print('-' * 40)
          running = False
    
    grid.draw()
    score.draw()

    SDL_UpdateWindowSurface(window)
    
    clock.update_time()
    t1 = clock.time
    dt = t1 - t0
    if dt < DRAW_TIME:
      SDL_Delay((DRAW_TIME - dt) // 1000000)
  
  # avoid calling TTF_CloseFont() after TTF_Quit(), which causes a SEGFAULT
  del score
    
  SDL_DestroyWindow(window)
  TTF_Quit()
  SDL_Quit()
  return 0

if __name__ == '__main__':
  sys.exit(run())