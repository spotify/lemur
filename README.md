# Netflix/Lemur @ Spotify
Lemur deployment on Spotify infra

## Setting up a dev environment
`Requirements: Docker and docker-compose`

Everything below uses Docker to setup the environment so Python and
the required dependencies for Lemur are not needed to setup the development
environment.

### Start and setup PostgreSQL:
```bash
# replace <PASSWORD> with the password you want to set on the postgres user
POSTGRES_PASSWORD=<PASSWORD> docker-compose up
```

The `POSTGRES_PASSWORD` environment is only needed during the first run of
`docker-compose`.

### Create Lemur environment and initialize database
```bash
./dev-setup.sh
```

This will create a file `.lemur-env` in the folder with local configuration
overrides.

During the setup you will be asked for a password for the `lemur` user. This
user is the Lemur administration user you can use to login with.

## Building and Running Lemur
```bash
docker build -t spotify-lemur .
./dev-run.sh
```

or 

```bash
docker build -t spotify-lemur .
docker docker run -it --rm --env-file .lemur-env -p 8080:80 spotify-lemur
```

You should now be able to access Lemur at http://localhost:8080. Login with
the user `lemur` and the password you created during the setup phase.