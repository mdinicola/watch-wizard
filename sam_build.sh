#!/bin/bash
set -e
python3 -m flake8
sam build --use-container --skip-pull-image