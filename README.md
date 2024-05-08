# Empower Plant

<img width="633" alt="Empower Plant website screenshot" src="https://github.com/sentry-demos/empower/assets/490201/6bce9ad6-d256-4a6d-a49b-e0fe8cdd193c">


This is a multi-language/framework project that implements Empower Plant web app. It has one actively maintained frontend, `react`, that can connect to any one of the backend implementations using a query string parameter (e.g. `?backend=express`) and uses `flask` by default.

# Usage

Curently deployed to: https://application-monitoring-react-dot-sales-engineering-sf.appspot.com/

## Features

https://www.notion.so/sentry/Demo-Data-Requirements-4b918453be6f4e4fbdcfd4b2e3e608e0

## Trigger an error

Add at least 1 item to Cart and purchase in order to trigger an Error. Visit the routes defined in src/index.js to produce transactions.

## Query Parameter Options in Demo App

Query params to be added to the demo app. These query parameters can be stacked on top of one another

- `?backend=flask` - [sets the backend url](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L175-L177) (we have multiple backends with similar functionality). [Here](https://github.com/sentry-demos/empower/blob/master/react/src/utils/backendrouter.js#L4-L10) are all the options for backends). Additionally recorded in `backendType` tag. **Defaults to**: flask
- `?userFeedback=true` - displays [(old) user feedback modal](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L208-L212) 5 seconds after checkout crash.
- `?se=<yourname` - put your name here, for example `?se=chris`, `?se=kosty`, etc. This results in an `se` tag [added to events triggered during the demo](https://github.com/sentry-demos/empower/blob/ea51c3dbce9d50ac32519546e1c772ea5a91722f/react/src/index.js#L191-L198), and [adjust the fingerprint](https://github.com/sentry-demos/empower/blob/ea51c3dbce9d50ac32519546e1c772ea5a91722f/react/src/index.js#L130-L138) to segment issues depending on the SE.
- `?crash=true` - forces [a crash](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/utils/errors.js#L41) of one of predefined types, selected randomly.
- `?crash=true&errnum=3` - forces crash of specific type depending on `errnum` value
- `?userEmail=someemail@example.com` - lets you [pass in a specific user email](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L218-L219)
- `?frontendSlowdown=true` - used in the [frontend-only demo flow](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L200-L207), which showcases a frontend slowdown via profiling.
- `?rageclick=true` - causes the checkout button to stop working, so you can rageclick it. This will prevent the checkout error from happening. If you want to still demo the checkout error AND a rageclick, you can rageclick manually on the 'Contact Us' button that shows on the page after the Checkout Error occurs.

```
# example
https://localhost:5000/?se=chris&backend=flask&frontendSlowdown=true
```

## Query Parameter Options in Sentry.io

While not an Empower React app query param, we also have demo-specific query params to customize Sentry UI experience. Those have to be set in the Sentry app itself.

- `&issueTracking=jira` - only shows 1 issue integration instead of all ~10 (for examples, see [internal documentation](https://www.notion.so/sentry/issueTracking-hack-c8bbae41bcb84c80aed9f3fc0ab29df6))

## User Feedback
The [user feedback widget](https://docs.sentry.io/platforms/javascript/user-feedback/#user-feedback-widget) is enabled on all pages, in the bottom-right corner. Submit user feedback from any page to have it [show up in Sentry](https://demo.sentry.io/feedback/?project=5808623&statsPeriod=7d).

## Additional documentation

- project README's in subdirectories (e.g. [react/README.md](./react/README.md)
- **"New deploy.sh and env-config for empower"** (internal doc)
- See [troubleshooting](./troubleshooting.md)
- **"Checklist for adding new language/framework demo to Empower"** (internal doc)
- [comment at the top of `deploy.sh` file](https://github.com/sentry-demos/empower/blob/master/deploy.sh#L3-L47).

# Local Setup / Development

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
