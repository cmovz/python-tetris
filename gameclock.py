import time

class GameClock:
  def __init__(self, ticks_per_second):
    self.ticks_per_second = ticks_per_second
    self.tick_time = 1000000000 // self.ticks_per_second

  def start(self):
    self.previous_tick = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
  
  def get_ticks(self):
    '''
    Return how many ticks have occurred since the last call and updates clock.
    '''
    t = time.clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    dt = t - self.previous_tick
    if dt < self.tick_time:
      return 0
    
    ticks = dt // self.tick_time
    self.previous_tick = t - (dt % self.tick_time)
    return ticks