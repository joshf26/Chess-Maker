FROM python:3.8.2

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD watchmedo auto-restart \
              --patterns="*.py" \
              --recursive -- \
              python -u chess_maker/main.py
