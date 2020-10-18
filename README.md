# Timely: A COS333 Project

Timely is a homework and productivity manager.

Created by: Mariah Crawford, David Lipman, Lindsey Moore, and Jorge Zreik

## Usage

Set the `FLASK_APP`, `FLASK_ENV`, and `POSTGRES_URL` environment variables as follows.

To make these permanent, edit `.bashrc` or `.zshrc`.

### Mac/Linux

```shell
export FLASK_APP=timely
export FLASK_ENV=development
export POSTGRES_URL=<our secret url>
```

### Windows

```shell
setx FLASK_APP "timely"
setx FLASK_ENV "development"
setx POSTGRES_URL <our secret url>
```

Then run the app on `localhost:5000` as follows

```shell
pip install -e .
flask run
```
