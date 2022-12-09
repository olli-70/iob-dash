FROM python:3.10

ENV DASH_DEBUG_MODE True
COPY ./app /app
WORKDIR /app
RUN set -ex && \
    pip install -r requirements.txt
EXPOSE 8050
CMD ["gunicorn", "-w", "4","-b", "0.0.0.0:443", "--reload", "--certfile", "/certs/fullchain.pem", "--keyfile", "/certs/privkey.pem", "iob_dash:server"]
