#!/bin/bash
set -e

echo "BUILD START"
python3.9 -m ensurepip --upgrade  # Pip'in kurulu olduğunu kontrol edin ve güncelleyin
python3.9 -m pip install --upgrade pip  # Pip'i güncelleyin
python3.9 -m pip install -r requirements.txt
python3.9 manage.py collectstatic --noinput --clear
echo "BUILD END"
