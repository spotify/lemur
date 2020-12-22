# Netflix/Lemur @ Spotify
Lemur deployment on Spotify infra

## Setting up a dev environment
`Requirements: Docker and docker-compose`

Everything below uses Docker to setup the environment so Python and
the required dependencies for Lemur shouldn't be needed.

### Start and setup PostgreSQL:
```bash
# replace <PASSWORD> with the password you want to set on the postgres user
POSTGRES_PASSWORD=<PASSWORD> docker-compose up
```

The `POSTGRES_PASSWORD` environment is only needed during the first run of
`docker-compose`.

### Create Lemur environment and initialize database

If you're on linux, you need to edit the `dev-setup.sh` and uncomment the lines
where it says so.

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
docker run -it --rm --env-file .lemur-env -p 8080:80 spotify-lemur
```

You should now be able to access Lemur at http://localhost:8080. Login with
the user `lemur` and the password you created during the setup phase.


## Working with patches

If you want to change code in the upstream lemur repository, you can use patches
instead:

* Clone https://ghe.spotify.net/wasabi/lemur
* Edit the files in the `lemur` subfolder you want to edit.
* run `git diff --no-prefix > patches/<000-your-patch-name>.patch` to create a
  new patch file in the `patches` folder.

These patches are [applied by the build-pipeline](https://ghe.spotify.net/wasabi/lemur/blob/master/build-info.yaml#L10-L15) 
before building the docker image.

### Local development with patches

In the [wasabi/lemur repo](https://ghe.spotify.net/wasabi/lemur), you can run
```bash
./dev-build-local.sh
```
which will apply all patches, build a local docker image called 
`lemur-local-dev` and undo the patches again (to leave the files in clean 
state).

Then in this repository, you can run
```bash
./dev-build-from-local-lemur.sh
```
which will build the `spotify-lemur` image as usual from the Dockerfile, but 
use the `lemur-local-dev` image as base-image (instead of the one from the GCR).