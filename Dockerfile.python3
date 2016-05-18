FROM python:3-alpine
RUN pip install pytest
WORKDIR /tracer-py
ADD docker-entrypoint.sh /
ENTRYPOINT [ "/docker-entrypoint.sh" ]
