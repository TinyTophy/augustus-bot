## Setup

1. `pip install pipenv`

2. `cd augustus-bot`

3. `pipenv shell`

4. `pipenv install`

5. Add a file named `info.json` to the main dir. It's format should look like this:

```
{
  "mongo": "mongo connection string",
  "token": {
    "prod": "production bot token",
    "dev": "dev bot token"
  },
  "state": "Tells the bot whether in dev or prod. Don't edit this manually. (look in mode.py)"
}
```

## Run

While in pipenv shell run `python init.py`.

