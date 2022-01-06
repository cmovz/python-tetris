import os

def get_resource_path(*args):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)