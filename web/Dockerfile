FROM node:14.2.0

COPY . /web

WORKDIR /web/chess-maker

CMD npm install && \
    node_modules/@angular/cli/bin/ng serve --host 0.0.0.0
