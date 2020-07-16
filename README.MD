## Setup

It is important that you perform these steps in order.

1. `pip3 install pipenv`

1. `pip install pipenv`

2. `cd augustus-bot`

3. Add a file named `.env` to the main dir. It's format should look like this:

```
PROD=production bot token
DEV=dev bot token
MONGO=mongodb connection string
```
4. `pipenv shell`

5. `pipenv install`

## Run

While in the pipenv venv run `python init.py`.

