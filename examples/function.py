from sysdig_tracer import Tracer
import time

@Tracer
def myprinter():
  print "Hello World"

while True:
  myprinter()
  time.sleep(0.5)