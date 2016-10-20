# Copyright (C) 2016 Sysdig inc.
# All rights reserved

# Author: Luca Marturana (luca@sysdig.com)

import os
import traceback
from inspect import isfunction
import sys
import functools

# ensure file descriptor will be closed on execve
O_CLOEXEC = 524288 # cannot use octal because they have different syntax on python2 and 3
NULL_FD = os.open("/dev/null", os.O_WRONLY | os.O_NONBLOCK | O_CLOEXEC)

class Args(object):
  """
  Use this class to tell Tracer to extract positional function arguments
  and emit them to the trace:

  @Tracer(enter_args={"n": Args(0)})
  def myfunction(n):
    pass

  myfunction(9)
  """
  def __init__(self, i):
    self.i = i

  def __call__(self, args):
    return args[self.i]

class Kwds(object):
  """
  Use this class to tell Tracer to extract keyword function arguments
  and emit them to the trace:

  @Tracer(enter_args={"n": Kwds("n")})
  def myfunction(n):
    pass

  myfunction(n=9)
  """
  def __init__(self, key):
    self.key = key

  def __call__(self, kwds):
    return kwds[self.key]

class ReturnValue(object):
  """
  Use this class to tell Tracer to extract return value of a function
  and emit them to the trace:

  @Tracer(exit_args={"n": ReturnValue})
  def myfunction():
    return 8

  myfunction()
  """
  pass

class Tracer(object):
  """
  This class allows you to add a tracer to a function, a method or
  to instrument specific part of code. Use it as decorator:

  @Tracer
  def myfuction():
    pass

  or using `with` syntax:

  with Tracer():
    pass

  """

  def __init__(self, tag=None, enter_args={}, exit_args={}):
    """
    Create a new Tracer, all arguments are optional:

    tag -- tag name, by default is auto-detected by the code line or function name
    enter_args -- dictionary of enter arguments for the trace, use Args, Kwds to extract function arguments
    exit_args -- dictionary of exit arguments for the trace, use ReturnValue to extract function return value
    """
    self.__detect_tag(tag)
    self.enter_args = enter_args
    self.exit_args = exit_args

  def __detect_tag(self, tag):
    if isinstance(tag, str):
      self.tag = tag
    elif isfunction(tag):
      self.tag = tag.__name__
      self.wrapped_func = tag
      self.function_calls = 0
    else:
      tb = traceback.extract_stack(None, 3)[0]
      filepath = tb[0]
      filepath = filepath[filepath.rfind("/",0, filepath.rfind("/"))+1:]
      filepath = filepath.replace(".", "\.")
      self.tag = "%s\:%d(%s)" % (filepath, tb[1], tb[2].replace("<","\<").replace(">","\>"))

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

      if self.function_calls == 0:
        enter_args = {}
        for key, value in self.enter_args.items():
          if isinstance(value, Args):
            enter_args[key] = value(args)
          elif isinstance(value, Kwds):
            enter_args[key] = value(kwds)
          elif isinstance(value, str):
            enter_args[key] = value
        self.__emit_trace(">", enter_args)
      
      # function_calls counter helps to detect recursive calls
      # and print them only once
      self.function_calls += 1
      res = self.wrapped_func(*args, **kwds)
      self.function_calls -= 1

      if self.function_calls == 0:
        exit_args = {}
        for key, value in self.exit_args.items():
          if value == ReturnValue:
            exit_args[key] = res
          elif isinstance(value, str):
            exit_args[key] = value
        self.__emit_trace("<", exit_args)
      return res

  def start(self, tag=None, args={}):
    """
    Emit a tracer enter event.
    
    This method allows to fine control trace emission

    t = Tracer()
    t.start()
    [code]
    t.stop()

    is equal to:

    with Tracer():
      [code]

    tag -- same as __init__
    args -- dictionary of enter args
    """
    self.__detect_tag(tag)
    self.__emit_trace(">", args)

  def stop(self, args={}):
    """
    Emit an exit trace event

    See start() for further details
    """
    self.__emit_trace("<", args)

  def span(self, tag=None, enter_args={}, exit_args={}):
    """
    Create a nested span inside a tracer,
    the usage is the same of Tracer() itself:

    with Tracer() as t:
      [code]
      with t.span() as child:
        [othercode]

    """
    t = Tracer("", enter_args, exit_args)
    t.__detect_tag(tag)
    t.tag = "%s.%s" % (self.tag, t.tag)
    return t

  def __get__(self, obj, objtype):
    # This is needed to support decorating methods
    # instead of spare functions
    return functools.partial(self.__call__, obj)
