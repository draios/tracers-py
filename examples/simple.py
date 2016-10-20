from sysdig_tracers import Tracer
import time

while True:
  with Tracer():
    print "Hello World"
  time.sleep(0.5)