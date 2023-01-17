FROM python:3.10

WORKDIR /

# disable the pyc generation
ENV PYTHONDONTWRITEBYTECODE 1
# unbuffered output that speeds up the log generation to stdout
ENV PYTHONUNBUFFERED 1

COPY ./requirements_prd.txt /app/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app

WORKDIR /

CMD ["sh", "-c", "uvicorn app.main:app --proxy-headers --host 0.0.0.0 --port $API_PORT"]
