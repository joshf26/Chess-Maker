FROM python:3.8.2

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD python -u -m chessmaker.main
#CMD watchmedo auto-restart \
#              --patterns="*.py;*.svg;*.yml" \
#              --recursive -- \
#              python -u -m chessmaker.main
