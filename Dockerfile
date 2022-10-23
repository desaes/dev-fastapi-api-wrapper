FROM python:3.10

WORKDIR /

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app

WORKDIR /app

#CMD ["sh", "-c", "uvicorn main:app --proxy-headers --host 0.0.0.0 --port $API_PORT"]
CMD ["python3", "main.py"]
