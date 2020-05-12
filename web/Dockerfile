FROM node:14.2.0

COPY . /web

WORKDIR /web/chess-maker

RUN touch mytouchedfile

CMD npm install && \
    npm install -g @angular/cli && \
    ng serve --host 0.0.0.0
