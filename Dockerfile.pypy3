FROM pypy:3-slim
RUN pip install pytest
WORKDIR /tracer-py
ADD docker-entrypoint.sh /
ENTRYPOINT [ "/docker-entrypoint.sh" ]
