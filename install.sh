#!/bin/bash

ampy ${@:1} put venv/lib/python3.*/site-packages/picozero/picozero.py
ampy ${@:1} put secrets.py
ampy ${@:1} put main.py
