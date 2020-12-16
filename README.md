Momedict
=========

Momedict is a webapp written in Python 3 using Flask and SQLAlchemy meant to be used for homework.  

**Warning for users who want to adopt this project**:

This project has been used as playground for me.  

Features
--------

- Search word definitions
- Create private vocabulary and start practice
- Correct word is +1 point, wrong is -1 point
- Create profile and login
- Update your profile

Installation
------------

- Requires pipenv to be installed


```bash
git clone http://git.ragipunal.com/ragip/momedict.git
cd momedict
python3 -m venv venv
source venv/bin/activate
pip install wheel
pip install pipenv
pipenv install # Install requirements

# for init migrations
# python ./main.py db init

# for change db scheme
# python ./main.py db migrate
# python ./main.py db upgrade # Create/upgrade database tables
# for initial data load but this db loaded
python ./main.py import words/wordsapi_sample.json # Import all questions (Warning: super slow if using SQLite)
# first run is too slow for windows os please waiting
python ./main.py runserver # Run webserver
```


### Local config

To overwrite configuration in momedict/config.py.

Example: 

```python
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(PROJECT_PATH, 'momedict.db')
# or
SQLALCHEMY_DATABASE_URI = 'postgresql://username@localhost/momedict'
RAPIDAPI_KEY = 'your api key'
RAPIDAPI_HOST = 'wordsapiv1.p.rapidapi.com'
```

