# flask-testing
Place to test out flask

Going through the [Flask tutorial](https://flask.palletsprojects.com/en/2.0.x/tutorial/)

## Getting started

You can optionally install `direnv`, which means you can leave out the `FLASK_APP=flaskr` out from 
commands below. You can also run 

```shell
export FLASK_APP=flaskr
```

if you'd rather not add it to each command that needs it.

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
   
4. Copy the env file.

    ```shell
    cp .env.example .env
    ```
   
5. Replace the `SECRET_KEY` value in your `.env` file. You can use this command to generate a new one:

    ```shell
    poetry run python -c 'import secrets; print(secrets.token_hex())'
    ```
   
6. Initialize the DB:

    ```shell
    FLASK_APP=flaskr poetry run flask init-db
    ```

7. Start the application:

    ```shell
    FLASK_APP=flaskr poetry run flask run
    ```