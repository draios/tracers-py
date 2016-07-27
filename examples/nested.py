from sysdig_tracer import Tracer
import time
import random

def noiseSleep(base):
  return time.sleep(base + random.random() / 10)

while True:
  with Tracer("worker") as t:
    print("Hello World")
    noiseSleep(0.1)
    with t.span("read"):
      noiseSleep(0.2)
    with t.span("parse"):
      noiseSleep(0.3)
    with t.span("write"):
      noiseSleep(0.4)
