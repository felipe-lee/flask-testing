# flask-testing
Place to test out flask

Going through the [Flask tutorial](https://flask.palletsprojects.com/en/2.0.x/tutorial/)

## Getting started

1. First, copy the env example file. This will keep secrets and other config needed for later parts.

    ```shell
    cp .env.example .env
    ```

### Set Up Postgres

1. [Install docker compose](https://docs.docker.com/compose/install/).
2. Check the `POSTGRES*` variables to make sure they'll be ok for you. They probably are, but change any if you want/need to.
   1. You can also just try running the next step and adjust only if needed (e.g. if the host port is already being used).
3. Start the postgres container:

   ```shell
   docker compose up
   ```

### Python Dependencies

1. You'll need python installed, up to you how. The version that you need is listed in the `pyproject.toml` file and will
    look something like this:

    ```toml
    [tool.poetry.dependencies]
    python = "^3.10"
    ```

2. Install [poetry](https://python-poetry.org/docs/)
3. Install dependencies.

    ```shell
    poetry install
    ```
   
### Settings
   
1. Replace the `SECRET_KEY` value in your `.env` file. You can use this command to generate a new one:

    ```shell
    poetry run python -c 'import secrets; print(secrets.token_hex())'
    ```

### Creating Tables

Now we can create the tables in the database by running:

```shell
poetry run flask init-db
```

### Running The Application

To start the application, run:

```shell
poetry run flask run
```