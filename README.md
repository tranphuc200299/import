# Import System

## Setup code
```bash
$ git clone https://git.ntq.solutions/BJM/import.git
$ cd import
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cd import
$ touch .dev
$ python manage.py runserver
```

## Create env file
Create .env file this includes all keys
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=import_cfs
DB_USER=admin
DB_PASSWORD=password@12345
DB_HOST=10.0.64.93
DB_PORT=5432
```

Access in url: **http://127.0.0.1:8000**