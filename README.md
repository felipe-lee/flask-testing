# flask-testing
Place to test out flask

Going through the [Flask tutorial](https://flask.palletsprojects.com/en/2.0.x/tutorial/)

## Getting started

### Set Up Postgres

1. [Install postgres for your os](https://www.postgresql.org/download/).
   1. You might have to ensure the service is running on linux:

   ```shell
   sudo service postgresql status
   ```
   
   2. If it isn't you can start it by running:

   ```shell
   sudo service postgresql start
   ```

2. Open a `psql` shell.
   1. On linux, this is done by running:

   ```shell
   sudo -i -u postgres
   ```

   ```shell
   psql
   ```

3. Create the login role we'll use from the app:

```shell
CREATE ROLE flaskr_user WITH CREATEDB LOGIN PASSWORD 'flaskr_password';
```

   1. You can replace the user (`flaskr_user` above) and password (`flaskr_password`) with whatever values you want, just remember them for later.

4. Create the database we'll use for the app:

```shell
CREATE DATABASE flaskr WITH OWNER flaskr_user;
```

   1. You can use a different name for the DB (`flaskr` above) if you'd like, just remember it for later.
   2. If you didn't use `flaskr_user` for your username, set the value after `OWNER` to match yours.

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

1. First, copy the env example file.

    ```shell
    cp .env.example .env
    ```
   
2. Replace the `SECRET_KEY` value in your `.env` file. You can use this command to generate a new one:

    ```shell
    poetry run python -c 'import secrets; print(secrets.token_hex())'
    ```

3. Set the `POSTGRES_` variables in `.env` to match what you set up in the DB section above.
   1. If you used the values in the example commands above, you shouldn't have to do anything, for `POSTGRES_USER`, `POSTGRES_PASSWORD`, or `POSTGRES_DB_NAME`.
   2. `POSTGRES_HOST` and `POSTGRES_PORT` are probably fine as they are as well, unless you did something different from the default when installing.

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