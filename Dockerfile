FROM python:3

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./ /app/

ENTRYPOINT ["python", "-u", "main.py"]
