# Lemur Dev Handbook

## Setting up a dev environment
`Requirements: Docker and docker-compose`

Everything below uses Docker to setup the environment so Python and
the required dependencies for Lemur shouldn't be needed. So no need to create
a python virtual env either.

### Clone repo and initialize submodule

Clone the repository and initialize the submodule `public-lemur` which points
to the [public fork of Netflix/lemur in our Github spotify org](https://github.com/spotify/lemur):
```bash
git clone git@ghe.spotify.net:wasabi/spotify-lemur.git
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

### Create Lemur env file and initialize database

```bash
./dev-setup.sh
```

This will create a file `.lemur-env` in the folder with local configuration
overrides.

During the setup you will be asked for a password for the `lemur` user. This
user is the Lemur administration user you can use to login with.

## Building and Running Lemur

Build the spotify-lemur container locally

```bash
docker build -t spotify-lemur .
```

Start the local database and celery services

```bash
docker-compose up
```

Run the spotify-lemur container

```bash
./dev-run.sh
```

or

```bash
docker run -it --rm --env-file .lemur-env -p 8080:80 spotify-lemur
```

You should now be able to access Lemur at http://localhost:8080. Login with
the user `lemur` and the password you created during the setup phase.

## Making changes in upstream code: working with the submodule  

If you need to make code changes in the original Netflix/lemur code, you can
use the submodule to commit changes to our 
[public lemur fork on Github](https://github.com/spotify/lemur):

1. `cd public-lemur` so git is working in the submodule context.
2. Create a new branch `git checkout -b my-new-feature-or-fix`.
3. Change any file in `public-lemur/` and `git commit -m "..."` as usual.
4. Push the branch to the fork (`git push --set-upstream origin my-new-feature-or-fix`)
5. Create a PR on the public fork, get it reviewed and merged. NOTE: By default
   Github suggests to make the PR against the Netflix repository as ours was
   forked from there. **You have to manually change the base to `spotify/lemur`** 
   otherwise you create the PR in the Netflix repo!
6. `git checkout master` and `git pull` in `public-lemur`.
7. `cd ..` to the spotify-lemur directory and up the submodule to the latest 
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
