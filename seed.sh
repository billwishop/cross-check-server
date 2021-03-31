#!/bin/bash

rm -rf crosscheckapi/migrations
rm db.sqlite3
python3 manage.py migrate
python3 manage.py makemigrations crosscheckapi
python3 manage.py migrate crosscheckapi
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata landlords
python3 manage.py loaddata tenants
python3 manage.py loaddata paymenttypes
python3 manage.py loaddata properties
python3 manage.py loaddata payments
python3 manage.py loaddata tenantpropertyrel

