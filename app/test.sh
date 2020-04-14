#!/bin/bash

docker-compose run --rm app python3 -u -m unittest $1
