#!/bin/bash

echo Running prestart script...
FLASK_APP=main flask db migrate
FLASK_APP=main flask db upgrade

