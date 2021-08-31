# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster
WORKDIR /app

COPY main.py process_utils.py ydl_utils.py entrypoint.sh userscript.js requirements.txt ./
COPY hooks.py params.py userscript.js ./setup/

RUN pip3 install -r requirements.txt
RUN apt update && apt install ffmpeg -y && apt-get autoremove && apt-get -y clean && rm -rf /var/lib/apt/lists/*

EXPOSE 80
VOLUME ["/app/downloads", "/app/params"]

CMD ["sh", "/app/entrypoint.sh"]
