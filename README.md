# python-tetris
Simple, unfinished, Tetris clone with simple AI, written in Python using SDL2. 
This is not optimized. For an optimized version check out 
[c-tetris](https://github.com/cmovz/c-tetris).
# Running
Clone the repo then run `python3 main.py` or `python3 main.py --ai`.

If you don't have `PySDL2` installed run `pip3 install -U pysdl2`.
It needs Python >= 3.7 and right now only works on Unix because of 
`time.clock_gettime_ns()`.
# Screenshot
![Screenshot](images/screenshot.png)