import os
from IPython import embed
import traceback
from inspect import isfunction
import sys

NULL_FD = os.open("/dev/null", os.O_WRONLY)

class Tracer(object):
  def __init__(self, tag=None, enter_args={}, exit_args={}):
    self.__detect_tag(tag)
    self.enter_args = enter_args

  def __detect_tag(self, tag):
    if isinstance(tag, str):
      self.tag = tag
    elif isfunction(tag):
      self.tag = tag.__name__
      self.wrapped_func = tag
    else:
      tb = traceback.extract_stack(None, 3)[0]
      filepath = tb[0]
      filepath = filepath[filepath.rfind("/",0, filepath.rfind("/"))+1:]
      filepath = filepath.replace(".", "\.")
      self.tag = "%s\:%d(%s)" % (filepath, tb[1], tb[2])

  def __emit_trace(self, direction, args={}):
    args_s = ",".join(["%s=%s" % item for item in args.items()])
    try:
      os.write(NULL_FD, "%s:t:%s:%s:" % (direction, self.tag, args_s))
    except:
      pass

  def __enter__(self):
    self.__emit_trace(">", self.enter_args)

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.__emit_trace("<")

  def __call__(self, *args, **kwds):
    self.__emit_trace(">")
    res = self.wrapped_func(*args, **kwds)
    self.__emit_trace("<")
    return res

  def start(self, tag=None, args={}):
    self.__detect_tag(tag)
    self.__emit_trace(">", args)

  def stop(self, args={}):
    self.__emit_trace("<", args)