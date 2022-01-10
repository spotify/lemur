# Lemur Dev Handbook

## Setting up a dev environment
`Requirements: docker, docker-compose, python37`
`System packages required: postgresql redis openldap cyrus_sasl openssl`


### MacOS packages installation
Install the required system packages, ie with `brew install`.

If you experience errors installing packages while initializing submodules, you might have to link openssl like: 

```bash
brew link openssl
export LDFLAGS="-L/opt/homebrew/opt/openssl@1.1/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@1.1/include"
```
TODO: cyrus_sasl not found (ignore if not a problem?)

### Linux package installation
Install the required system packages, ie with `apt-get install`.

If you didn't have python 3.7, you might need the `libffi(-dev)` package before installing it (otherwise you might get `_ctype module not found` errors later).

### Clone repo and initialize submodule
Clone the repository and initialize the submodule `public-lemur` which points
to the [public fork of Netflix/lemur in our Github spotify org](https://github.com/spotify/lemur):
```bash
git clone git@ghe.spotify.net:atc/spotify-lemur.git
cd spotify-lemur
git submodule update --init --recursive
```

The submodule is set to using the https URL so that tingle can pull from
the fork. For development this might be inconvenient as you have to use
username/password auth for the http URL, so you can set the push-URL to the ssh 
URL instead:

```bash
cd public-lemur
git config remote.origin.pushurl git@github.com:spotify/lemur.git
cd ..
```

### Installing Lemur
Create a virtualenv and activate
```bash
python -m venv venv
. venv/bin/activate
```

or if using pyenv
```bash
pyenv install 3.7.10
pyenv virtualenv 3.7.10 spotify-lemur
pyenv local spotify-lemur
```

Install Lemur and plugins in development mode:
```bash
pip install -e public-lemur/
pip install -e lemur-plugin-ffwd/
pip install -e lemur-plugin-gcp/
pip install -e lemur-plugin-slack/
```

### Create Lemur env file and initialize database
To clean up after previous development, stop all docker containers and execute `./dev-cleanup.sh`.

```bash
python generate-env.py > .lemur-env
source .lemur-env
```

This will create a file `.lemur-env` in the folder with local configuration
overrides.

Start postgres:
```bash
docker-compose up -d postgres
```

Initialize the database:
```bash
source .lemur-env
cd public-lemur/lemur/
lemur init
```

During the setup you will be asked for a password for the `lemur` user. This
user is the Lemur administration user you can use to login with.

## Running Lemur
Lemur consists of multiple components.

1. Lemur backend (Flask application)
1. Frontend (Written in Javascript)
1. Celery Beat (Periodic task scheduler)
1. Celery Worker (Celery worker to run tasks)
1. PostgreSQL (Database)
1. Redis (Backend for Celery task orchestration) - [repo here](https://ghe.spotify.net/atc/spotify-lemur-redis) to have separate deployment cycles from the components defined in this repo

You don't have to run everything if you're only on certain parts. However, the
backend code will create tasks for certain operations, e.g. destination upload
that happens when you attach a destination to a certificate.

For development mode we use an nginx docker container to serve the frontend
and act as a reverse proxy to the backend development server running on port
5000.

### Backend
Backend development server that will auto-reload on code changes:

```bash
lemur runserver
```

### Nginx for Frontend and Backend proxy
If you're on mac:
```bash
source .lemur-env
docker-compose up -d nginx-mac
```

If you're on linux:
```bash
source .lemur-env
docker-compose up -d nginx-linux
```

Add `--build` to rebuild the container if you've made any changes to `Dockerfile.nginx`.

### Redis
```bash
docker-compose up -d redis
```

### Celery worker
```bash
celery -A lemur.common.celery worker --loglevel=debug --concurrency 1 -E
```

### Celery beat (period task scheduler)
```bash
celery -A lemur.common.celery beat --loglevel=debug
```

### Celery flower (graphical task overview)
Before running flower the first time, you need to install it in you python 
virtual env with `pip install flower`. Then you can run
```bash
flower --broker=redis://:lemur@localhost:6379/0
```


You should now be able to access Lemur at http://localhost:8080. Login with
the user `lemur` and the password you created during the setup phase.

On http://localhost:5555 you can view your local Celery flower instance.

## Making changes in upstream code: working with the submodule  

For local development you can simply change any file, including those in 
`public-lemur` and rerun Lemur - it will pick up source changes as it was 
installed in development mode.

When you're done and you have made code changes in the original Netflix/lemur 
code (files in `public-lemur`), you can use the submodule to commit changes to 
our [public lemur fork on Github](https://github.com/spotify/lemur):

1. `cd public-lemur` so git is working in the submodule context.
1. Create a new branch `git checkout -b my-new-feature-or-fix`.
1. Review the changes of your files in `public-lemur/*` eg with with `git diff`. 
1. When happy with your changes, make a commit (`git commit -m "..."`) and
   push the branch to the fork 
   (`git push --set-upstream origin my-new-feature-or-fix`)
1. Create a PR on the public fork, get it reviewed and merged. NOTE: By default
   Github suggests to make the PR against the Netflix repository as ours was
   forked from there. **You have to manually change the base to `spotify/lemur`** 
   otherwise you create the PR in the Netflix repo!
1. `git checkout master` and `git pull` in `public-lemur`.
1. `cd ..` to the spotify-lemur directory and up the submodule to the latest 
   commit on a new branch: 
   - `git checkout -b up-submodule`
   - `git add public-lemur`
   - `git commit -m "Up submodule"`

   This will trigger the build pipeline on your branch and you can create a PR 
   if the tests succeed. 


## Testing Digicert API Integration
If you want to test the lemur's Digicert Plugin, please add the 
`DIGICERT_API_KEY` variable to the `.lemur-env` file. You find API key in the 
LastPass's Lemur shared folder. For testing please use the **(testing)** key.

Remember to never commit secrets to GHE. `.lemur-env` is listed in `.gitignore` 
but still be careful not to check it in.
