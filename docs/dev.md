# Lemur Dev Handbook

## Setting up a dev environment
`Requirements: docker, docker-compose, python37`
`System packages required: postgresql redis openldap cyrus_sasl openssl`

### Clone repo and initialize submodule

Clone the repository and initialize the submodule `public-lemur` which points
to the [public fork of Netflix/lemur in our Github spotify org](https://github.com/spotify/lemur):
```bash
git clone git@ghe.spotify.net:wasabi/spotify-lemur.git
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
```

### Installing Lemur
Create a virtualenv and activate

```bash
$ python -m venv venv
$ . venv/bin/activate
```

Install Lemur and plugins in development mode:
```bash
$ pip install -e public-lemur/
$ pip install -e lemur-plugin-ffwd/
$ pip install -e lemur-plugin-gcp/
$ pip install -e lemur-plugin-slack/
```

### Create Lemur env file and initialize database

```bash
$ ./generate-env.py > .lemur-env
$ source .lemur-env
```

This will create a file `.lemur-env` in the folder with local configuration
overrides.

Start postgres:
```bash
$ docker-compose up -d postgres

To initialize the database:

```bash
$ cd public-lemur/lemur/
$ lemur init
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
1. Redis (Backend for Celery task orchestration)

You don't have to run everything if you're only on certain parts. However, the
backend code will create tasks for certain operations, e.g. destination upload
that happens when you attach a destination to a certificate.

For development mode we use an nginx docker container to serve the frontend
and act as a reverse proxy to the backend development server running on port
5000.


### Backend
Backend development server that will auto-reload on code changes:

```bash
$ lemur runserver
```

### Nginx for Frontend and Backend proxy
```bash
$ docker-compose up -d nginx
```

Add `--build` to rebuild the container if you've made any changes to `Dockerfile.nginx`.

### Redis
```bash
$ docker-compose up -d redis
```

### Celery worker
```bash
$ celery -A lemur.common.celery worker --loglevel=debug --concurrency 1 -E
```

### Celery beat (period task scheduler)
```bash
celery -A lemur.common.celery beat --loglevel=debug
```


You should now be able to access Lemur at http://localhost:8080. Login with
the user `lemur` and the password you created during the setup phase.

## Making changes in upstream code: working with the submodule  

If you need to make code changes in the original Netflix/lemur code, you can
use the submodule to commit changes to our 
[public lemur fork on Github](https://github.com/spotify/lemur):

1. `cd public-lemur` so git is working in the submodule context.
1. Create a new branch `git checkout -b my-new-feature-or-fix`.
1. Change any file in `public-lemur/*` 
1. To test your changes locally, simply build and run the docker container. Docker 
   will pick up the current version of any files in `public-lemur/*` as build context:
   `cd ..`, `docker build -t spotify-lemur .`, `./dev-run.sh`.
1. When happy with your changes, make sure you're back in the submodule context
   (`cd public-lemur`), make a commit (`git commit -m "..."`) and
   push the branch to the fork (`git push --set-upstream origin my-new-feature-or-fix`)
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

For local development you can simply change any file in `public-lemur` and run
`docker build -t spotify-lemur` and then `./dev-run.sh` to test it. 


## Testing Digicert API Integration

If you want to test the lemur's Digicert Plugin, please add the 
`DIGICERT_API_KEY` variable to the `.lemur-env` file. You find API key in the 
LastPass's Lemur shared folder. For testing please use the **(testing)** key.

Remember to never commit secrets to GHE. `.lemur-env` is listed in `.gitignore` 
but still be careful not to check it in.
