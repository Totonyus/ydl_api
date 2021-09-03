#!/bin/bash

pip3 install youtube-dl --upgrade

if [ ! -f /app/params/params.py ]; then
  cp /app/setup/params.py /app/params/params.py
fi

if [ ! -f /app/params/hooks.py ]; then
  cp /app/setup/hooks.py /app/params/hooks.py
fi

if [ ! -f /app/params/userscript.js ]; then
  cp /app/setup/userscript.js /app/params/userscript.js
fi

ln -s /app/params/params.py /app/params.py
ln -s /app/params/hooks.py /app/hooks.py

uvicorn main:app --port 80 --host 0.0.0.0
