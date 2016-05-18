#!/bin/bash
set -ex
for dockerfile in Dockerfile.*; do
  python_version=`echo $dockerfile|cut -d "." -f2`
  docker build -t tracer-py-${python_version} -f ${dockerfile} .
  docker run -it --rm -v $PWD:/tracer-py tracer-py-${python_version} $*
done
