from sysdig_tracer import Tracer 
import sysdig_tracer
import os
import fcntl
import sys
import pytest

# hack to send tracers to a pipe and allow unit testing
read_end, write_end = os.pipe()
sysdig_tracer.NULL_FD = write_end
fcntl.fcntl(read_end, fcntl.F_SETFL, os.O_NONBLOCK)

def check_pipe_content(s):
  content = ""
  try:
    content = os.read(read_end, 1024)
    if sys.version_info[0] == 3:
      content = str(content, 'ascii')
  except:
    pass
  assert content == s

def test_with():
  with Tracer("myname"):
    x = 5
    y = 6
  check_pipe_content(">:t:myname::<:t:myname::")

def test_with_and_args():
  with Tracer("myname", {"x": "8"}):
    x = 5
    y = 6
  check_pipe_content(">:t:myname:x=8:<:t:myname::")

def test_auto_naming():
  with Tracer():
    x = 5
    y = 6
  check_pipe_content(">:t:tracer-py/test\\.py\\:36(test_auto_naming)::<:t:tracer-py/test\\.py\\:36(test_auto_naming)::")

def test_decorator():
  @Tracer
  def myfunction():
    x = 5
    y = 6
  myfunction()
  check_pipe_content(">:t:myfunction::<:t:myfunction::")

def test_start_stop():
  t = Tracer()
  t.start()
  x = 8
  y = 5
  t.stop(args={"x": x})
  check_pipe_content(">:t:tracer-py/test\\.py\\:51(test_start_stop)::<:t:tracer-py/test\\.py\\:51(test_start_stop):x=8:")

  t.start("mytest")
  y = 6
  x = 7
  t.stop(args={"x": x})
  check_pipe_content(">:t:mytest::<:t:mytest:x=7:")

def test_auto_naming_in_nested_scope():
  def f():
    with Tracer():
      x = 5
      y = 6
  def g():
    f()
  g()
  check_pipe_content(">:t:tracer-py/test\\.py\\:65(f)::<:t:tracer-py/test\\.py\\:65(f)::")

@pytest.mark.skip(reason="not implemented yet")
def test_auto_correlate_nested_functions():
  @Tracer
  def f():
      x = 5
      y = 6
  @Tracer
  def g():
    f()
  g()
  check_pipe_content(">:t:g::<:t:g.f::>:t:g.f::<:t:g::")

