# ~~Application Monitoring~~ Empower
This is a multi-language/framework project that implements Empower Plant web app. It has one actively maintained frontend, `react`, that can connect to any one of the backend implementations using a query string parameter (e.g. `?backend=express`) and uses `flask` by default.

## Features
https://www.notion.so/sentry/Demo-Data-Requirements-4b918453be6f4e4fbdcfd4b2e3e608e0

## Additional documentation
- project README's in subdirectories (e.g. [react/README.md](./react/README.md)
- **"New deploy.sh and env-config for empower"** (internal doc)
- See [troubleshooting](./troubleshooting.md)
- **"Checklist for adding new language/framework demo to Empower"** (internal doc)
- [comment at the top of `deploy.sh` file](https://github.com/sentry-demos/empower/blob/master/deploy.sh#L3-L47).

## Setup
1. Permit your IP address in CloudSQL:
    1. Go to https://console.cloud.google.com/sql/instances
    2. You will see 1 instance, under Actions column click "..." -> Edit
    3. Expand "Connections", under Authorized Networks click "ADD NETWORK"
    4. Google "my IP address", add it.
2. Copy `local.env` from [empower-config](https://github.com/sentry-demos/empower-config) into `env-config` directory of your local repo, or, if you don't have access to it, follow `env-config/example.env`.
3. The `REACT_APP_FLASK_BACKEND` in `env-config/local.env` points to the backend instance deployed to AppEngine, the same one used by the cloud-hosted React web app. Flask is the default backend. If you expect to run other backend types, add values for those in `env-config` in your `local.env` file as well (i.e. `REACT_APP_EXPRESS_BACKEND`).
4. Confirm [Homebrew](https://brew.sh/) is installed with `brew -v`. If not, install using `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
5. Confirm PostgreSQL is installed with `Postgres -V`. If not, install using `brew install postgresql`.
6. As the application is compatible with specific versions of `node` and `npm`, install the following to be able to set the specific versions required (below describes how to achieve it using `n` package, but alternatively you can use `nvm`):
    1. Install compatible `npm` version with `npm install -g npm@XX.XX.XX`. NOTE: may need to use `sudo` with command.
    2. Install `n` to update `node` version with `npm install -g n`.
    3. Set the specific `node` version with `n XX.XX.XX`. NOTE: may need to use `sudo` with command.
7. Configure the `CLI` using [this](https://docs.sentry.io/product/cli/configuration/) document.
8. Install [gcloud](https://cloud.google.com/sdk/docs/install) in the root of your project to be able to deploy to staging. Initialize the gcloud CLI by running `gcloud init`. When prompted, choose the project `sales-engineering-sf`.

Following sub-projects might not work with `deploy.sh` at this moment. Consult their README's for how to run and deploy them (and feel free to submit a PR that fixes it):
- vue
- ruby

NOTE: `build.sh` and `run.sh` files in each project are not meant to be run directly, use top-level `deploy.sh` instead because it sets all required environment variables.

If you run locally and only deploy `react` it will point to `staging` backends, however if you include a backend
projects in the command `react` will magically point to it instead of staging (still requires `&backend=<backend>` url param).

`deploy.sh` takes another argument `--env=<env>`, which can be either `local`, `staging` or `production`. Each value corresponds to a file in `env-config` directory. `local` is a special value, most significantly it will run all webservers locally instead of deploying to Google App Engine.

`deploy.sh` does everything including validating that all required values are set in the `env-config/*.env`, that each project's DSN and project name point to the same project, and that you are not accidentally deploying to production, etc.

## Run

Pick one of two ways to run the React app:

### Option 1: Run React app w/ sourcemaps, suspect commits
Recommended to use this command rather than `npm start`, as deploy.sh uploads source maps and handles crashes more realistically.
```
./deploy.sh --env=local react flask
```
or
```
./deploy.sh react --env=local
```

### Option 2: Run React app w/ hot reload
NOTE: this will cause crashing errors to be tagged in sentry as handled (`handled: true`)
```
cd react
../env.sh local npm start
```

### Port Notes
The React app will default to Flask as its backend
```
// points to Flask
localhost:5000

// points to Express
localhost:5000?backend=express
localhost:5000/products?se=yourname&backend=express

// throw an exception on any route via 'crash'
localhost:5000?crash=true
```

## Trigger an error

Add +2 quantity of a single item to Cart and purchase in order to trigger an Error. Visit the routes defined in src/index.js to produce transactions.

## Deploy to Prod
This script deploys the flagship apps React + Flask. For deploying a single app to App Engine, check each platform's README for specific instructions. Make sure you don't have any local changes to `env-config/production.env`.
```
./deploy.sh react --env=production
```
You can put all 4 apps in deploy.sh for deployment, but that's 4 apps you could be taking down at once, which other people are relying on. With great power, comes great responsibility.  

Run `gcloud auth login` if it asks you to authenticate, or insert YubiKey.  

## Deploy to Staging
```
./deploy.sh react flask vue --env=staging
```

## Updating The Apps
```
## Check if you're on your fork. If so, you should see:
git remote -v
origin	git@github.com:<your_handle>/empower.git (fetch)
origin	git@github.com:<your_handle>/empower.git (push)
upstream	git@github.com:sentry-demos/empower.git (fetch)
upstream	git@github.com:sentry-demos/empower.git (push)

# If you don't have an upstream
git remote add upstream git@github.com:sentry-demos/empower.git

# Make sure you're on master
git checkout master

# get updates from the upstream
git fetch upstream master
git merge upstream/master

# merge those updates into your current branch, if it's behind
git checkout yourbranch
git merge master
```

## Troubleshooting
See [troubleshooting](./troubleshooting.md)

## Gcloud
```
gcloud app versions list
gcloud app deploy
gcloud app browse
gcloud app services list
gcloud app logs tail -s application-monitoring-react
gcloud app logs tail -s application-monitoring-flask
gcloud --help
gcloud topic configurations
gcloud auth
gcloud auth application-default
gcloud auth login
gcloud auth list
gcloud config set account `ACCOUNT`
gcloud config list, to display current account
```
`gcloud app deploy` does not support `--update-env-vars RELEASE=$RELEASE` like `gcloud run deploy` does with Cloud Run

