import os
import traceback
from inspect import isfunction
import sys
import functools

# ensure file descriptor will be closed on execve
O_CLOEXEC = 524288 # cannot use octal because they have different syntax on python2 and 3
NULL_FD = os.open("/dev/null", os.O_WRONLY | os.O_NONBLOCK | O_CLOEXEC)

class Args(object):
  def __init__(self, i):
    self.i = i

  def __call__(self, args):
    return args[self.i]

class Kwds(object):
  def __init__(self, key):
    self.key = key

  def __call__(self, kwds):
    return kwds[self.key]

class ReturnValue(object):
  pass

class Tracer(object):

  def __init__(self, tag=None, enter_args={}, exit_args={}):
    self.__detect_tag(tag)
    self.enter_args = enter_args
    self.exit_args = exit_args

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
    tracer = "%s:t:%s:%s:" % (direction, self.tag, args_s)
    if sys.version_info[0] == 3:
      tracer = bytes(tracer, 'ascii')
    try:
      os.write(NULL_FD, tracer)
    except OSError:
      pass

  def __enter__(self):
    self.__emit_trace(">", self.enter_args)
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.__emit_trace("<")

  def __call__(self, *args, **kwds):
    if len(args) == 1 and callable(args[0]):
      # This happens when Tracer is used as:
      #
      # @Tracer(enter_args= ..)
      # def myf():  ....
      self.__detect_tag(args[0])
      return self
    else:
      # This happens when Tracer is used as:
      #
      # @Tracer
      # def myf():  ....
      enter_args = {}
      for key, value in self.enter_args.items():
        if isinstance(value, Args):
          enter_args[key] = value(args)
        elif isinstance(value, Kwds):
          enter_args[key] = value(kwds)
        elif isinstance(value, str):
          enter_args[key] = value

      self.__emit_trace(">", enter_args)
      res = self.wrapped_func(*args, **kwds)
        
      exit_args = {}
      for key, value in self.exit_args.items():
        if value == ReturnValue:
          exit_args[key] = res
        elif isinstance(value, str):
          exit_args[key] = value

      self.__emit_trace("<", exit_args)
      return res

  def start(self, tag=None, args={}):
    self.__detect_tag(tag)
    self.__emit_trace(">", args)

  def stop(self, args={}):
    self.__emit_trace("<", args)

  def span(self, tag=None, enter_args={}, exit_args={}):
    t = Tracer("", enter_args, exit_args)
    t.__detect_tag(tag)
    t.tag = "%s.%s" % (self.tag, t.tag)
    return t

  def __get__(self, obj, objtype):
    # This is needed to support decorating methods instead of spare functions
    return functools.partial(self.__call__, obj)