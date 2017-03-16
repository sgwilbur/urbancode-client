FROM python:2-alpine

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt && \
    python setup.py install

WORKDIR /app/examples

ENTRYPOINT ["python"]
