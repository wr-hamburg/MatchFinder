#!/bin/bash

. .venv/bin/activate

export FLASK_APP=matchFinder

export FLASK_ENV=development

flask run

#flask run --host=0.0.0.0 # allow all devices in network to access app