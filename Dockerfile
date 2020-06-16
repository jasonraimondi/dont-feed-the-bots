FROM python:3-alpine

WORKDIR /app

RUN addgroup -g 1000 pyuser \
    && adduser -u 1000 -G pyuser -s /bin/sh -D pyuser \
    && chown -R pyuser:pyuser /app

USER pyuser

COPY --chown=pyuser:pyuser ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY --chown=pyuser:pyuser  ./ /app/

CMD ["python", "-u", "dontfeedthebots/main.py"]
