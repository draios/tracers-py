# tracers-py
Python library to easy emit Sysdig tracers

# Install

This library supports python 2.7 and 3, it also works on pypy 3 as well. To install it, just type:

```
pip install sysdig-tracers
```

Install also [sysdig](https://github.com/draios/sysdig/wiki/How-to-Install-Sysdig-for-Linux) to read trace data and correlate them.

# Usage

Using this library is pretty easy, just wrap your code in a `with` statement:

```python
from sysdig_tracers import Tracer
import time

while True:
  with Tracer():
    print "Hello World"
  time.sleep(0.5)
```

then while your code is running, launch sysdig:

```sh
$ sysdig evt.type=tracer
11132 12:58:56.203177473 0 python (11163) > tracer id=11163 tags=example/simple.py:5(<module>) args=
11136 12:58:56.203257412 0 python (11163) < tracer id=11163 tags=example/simple.py:5(<module>) args=
12570 12:58:56.705334633 2 python (11163) > tracer id=11163 tags=example/simple.py:5(<module>) args=
12615 12:58:56.705540522 2 python (11163) < tracer id=11163 tags=example/simple.py:5(<module>) args=
14202 12:58:57.207921927 2 python (11163) > tracer id=11163 tags=example/simple.py:5(<module>) args=
14245 12:58:57.208221298 2 python (11163) < tracer id=11163 tags=example/simple.py:5(<module>) args=
15672 12:58:57.710556623 3 python (11163) > tracer id=11163 tags=example/simple.py:5(<module>) args=
15680 12:58:57.710613724 3 python (11163) < tracer id=11163 tags=example/simple.py:5(<module>) args=
17325 12:58:58.213161095 3 python (11163) > tracer id=11163 tags=example/simple.py:5(<module>) args=
17333 12:58:58.213259041 3 python (11163) < tracer id=11163 tags=example/simple.py:5(<module>) args=
```

You can also use it as a decorator to automatically trace each function call:

```python
from sysdig_tracers import Tracer
import time

@Tracer
def myprinter():
  print "Hello World"

while True:
  myprinter()
  time.sleep(0.5)
```

And in sysdig you will see:

```sh
$ sysdig evt.type=tracer
2542 13:01:25.798147410 1 python (11171) > tracer id=11171 tags=myprinter args=
2546 13:01:25.798198636 1 python (11171) < tracer id=11171 tags=myprinter args=
4176 13:01:26.298901248 1 python (11171) > tracer id=11171 tags=myprinter args=
4180 13:01:26.298988231 1 python (11171) < tracer id=11171 tags=myprinter args=
5550 13:01:26.799701837 1 python (11171) > tracer id=11171 tags=myprinter args=
5554 13:01:26.799757884 1 python (11171) < tracer id=11171 tags=myprinter args=
7150 13:01:27.300566452 1 python (11171) > tracer id=11171 tags=myprinter args=
7154 13:01:27.300669953 1 python (11171) < tracer id=11171 tags=myprinter args=
8502 13:01:27.801823005 1 python (11171) > tracer id=11171 tags=myprinter args=
```

For more advanced usages see the [examples](https://github.com/draios/tracers-py/tree/master/examples) directory or our [tests](https://github.com/draios/tracers-py/blob/master/test.py)
