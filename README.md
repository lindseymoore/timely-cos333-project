# Timely: A COS333 Project

Timely is a homework and productivity manager. It can be accessed by Princeton students at https://timely-hw.herokuapp.com/.

Created by: Mariah Crawford, David Lipman, Lindsey Moore, and Jorge Zreik

## Usage

Set the `FLASK_APP`, `FLASK_ENV`, and `DATABASE_URL` environment variables as follows.

To make these permanent, edit `.bashrc` or `.zshrc`.

### Mac/Linux

```shell
export FLASK_APP=timely
export FLASK_ENV=development
export DATABASE_URL=<our secret url>
```

### Windows

```shell
setx FLASK_APP "timely"
setx FLASK_ENV "development"
setx DATABASE_URL <our secret url>
```

Then run the app on `localhost:5000` as follows

```shell
pip install -e .
flask run
```
