## Setup

1. `pip3 install pipenv`

2. `pipenv shell`

3. `pipenv install`

4. Add a file named `info.json` to the main dir. It's format should look like this:

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

