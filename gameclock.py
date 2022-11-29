import time

class Clock:
  def __init__(self):
    self.update_time()
  
  def update_time(self):
    self.time = time.monotonic_ns()

class GameClock:
  def __init__(self, clock, ticks_per_second):
    self.clock = clock
    self.ticks_per_second = ticks_per_second
    self.tick_time = 1000000000 // self.ticks_per_second

  def start(self):
    self.previous_tick = self.clock.time
  
  def get_ticks(self):
    '''
    Returns how many ticks have occurred since the last call.
    Updates previous_tick.
    '''
    t = self.clock.time
    dt = t - self.previous_tick
    if dt < self.tick_time:
      return 0
    
    ticks = dt // self.tick_time
    self.previous_tick = t - (dt % self.tick_time)
    return ticks