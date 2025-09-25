# Empower Plant

<img width="633" alt="Empower Plant website screenshot" src="https://github.com/sentry-demos/empower/assets/490201/6bce9ad6-d256-4a6d-a49b-e0fe8cdd193c">


This is a multi-language/framework project that implements Empower Plant web app. It has multiple actively maintained frontends:
- **`react`** - Primary React frontend (default)
- **`angular`** - Modern Angular 20 frontend with TDA test compatibility
- **`vue`** - Vue.js frontend

All frontends can connect to any one of the backend implementations using a query string parameter (e.g. `?backend=flask`) and use `flask` by default.

# Usage

Go to: empower dash plant dot com

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
- **DEPRECATED (broke at some point)** `?frontendSlowdown=true` - used in the [frontend-only demo flow](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L200-L207), which showcases a frontend slowdown via profiling.
- `?rageclick=true` - causes the checkout button to stop working, so you can rageclick it. This will prevent the checkout error from happening. If you want to still demo the checkout error AND a rageclick, you can rageclick manually on the 'Contact Us' button that shows on the page after the Checkout Error occurs.
- `?error_boundary=true` - enables the error boundary functionality in subscribe instead of putting a message on the queue (NextJS / React)
```
# example
https://localhost:5000/?se=chris&backend=flask&frontendSlowdown=true
```

## Query Parameter Options in Sentry.io

While not an Empower React app query param, we also have demo-specific query params to customize Sentry UI experience. Those have to be set in the Sentry app itself.

- `&issueTracking=jira` - only shows 1 issue integration instead of all ~10 (for examples, see [internal documentation](https://www.notion.so/sentry/issueTracking-hack-c8bbae41bcb84c80aed9f3fc0ab29df6))

## User Feedback
The [user feedback widget](https://docs.sentry.io/platforms/javascript/user-feedback/#user-feedback-widget) is enabled on all pages, in the bottom-right corner. Submit user feedback from any page to have it [show up in Sentry](https://demo.sentry.io/feedback/?project=5808623&statsPeriod=7d).

## Frontend Applications

### React (Primary)
- **Status**: Actively maintained, production ready
- **Documentation**: [react/README.md](./react/README.md)
- **Features**: Full Sentry integration, multiple backend support

### Angular 20
- **Status**: Actively maintained, TDA test compatible
- **Documentation**: [angular/README.md](./angular/README.md)
- **Deployment Guide**: [angular/DEPLOYMENT.md](./angular/DEPLOYMENT.md)
- **Features**: Modern Angular framework, Sentry integration, React-matching UI

### Vue.js
- **Status**: Available but may need updates
- **Documentation**: [vue/README.md](./vue/README.md)

## Additional documentation

Note: some of these may be out of date

- project README's in subdirectories (e.g. [react/README.md](./react/README.md)
- **"empower/deploy"** (internal doc)
- See [troubleshooting](./troubleshooting.md)
- **"Checklist for adding new language/framework demo to Empower"** (internal documentation)
- [comment at the top of `deploy.sh` file](https://github.com/sentry-demos/empower/blob/master/deploy.sh#L3-L47).

# Local Setup / Development

> [!WARNING]
> `npm run` won't work, please use the build system (`deploy.sh`). It sets all required env variables and is documented in detail below:

## Setup

> [!NOTE]
> `*.env` files now live in repository root, instead of `./env-config`, and are checked-in to source control. (`empower-config` repo is deprecated)

1. In `local.env` fill in your personal `SENTRY_ORG` and DSNs (also sentry project names if different from standard subdirectory names).
2. Confirm [Homebrew](https://brew.sh/) is installed with `brew -v`. If not, install using `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`.
3. Confirm PostgreSQL is installed with `Postgres -V`. If not, install using `brew install postgresql`.
4. As the application is compatible with specific versions of `node` and `npm`, install the following to be able to set the specific versions required (below describes how to achieve it using `n` package, but  you can use `nvm`):
   1. Install compatible `npm` version with `npm install -g npm@XX.XX.XX`. NOTE: may need to use `sudo` with command.
   2. Install `n` to update `node` version with `npm install -g n`.
   3. Set the specific `node` version with `n XX.XX.XX`. NOTE: may need to use `sudo` with command.
5. Configure Sentry CLI using [this](https://docs.sentry.io/product/cli/configuration/) document.
6. Install [gcloud](https://cloud.google.com/sdk/docs/install) in the root of your project to be able to deploy to staging. Initialize the gcloud CLI by running `gcloud init`. When prompted, choose the project `sales-engineering-sf`.

Following sub-projects might not work with `deploy.sh` at this moment. Consult their README's for how to run and deploy them (and feel free to submit a PR that fixes it):

- vue
- ruby
- nextjs

NOTE: `build.sh` and `run.sh` files in each project are not meant to be run directly, use top-level `deploy.sh` instead because it sets all required environment variables.

If you run locally and only deploy `react` it will point to `staging` backends, however if you include a backend
projects in the command `react` will magically point to it instead of staging (still requires `&backend=<backend>` url param).

`deploy.sh` takes another argument `--env=<env>`, which can be either `local`, `staging` or `production`. Each value corresponds to one of the *.env files in the root directory. `local` is a special value, it will run all webservers locally instead of deploying to Google App Engine.

`deploy.sh` does everything including validating that all required values are set in the `*.env`

It is highly recommended that you read the long comment at the top of `deploy`](https://github.com/sentry-demos/empower/blob/master/deploy) to get an idea how it works.

## Run

Pick one of two ways to run the React app:

### Option 1: Run React app the normal way

Recommended to use this command rather than `npm start`, as`deploy` uploads source maps and handles crashes more realistically.

```
# talks to staging backends
./deploy react --env=local
```

```
# talks to flask backend running locally, all others - staging
./deploy react flask --env=local
```

You many need to touch YubiKey or follow OAuth flow in the browser if you're prompted to re-authenticate.


### Option 2: Run React app w/ hot reload

NOTE: this will cause crashing errors to be tagged in sentry as handled (`handled: true`)

```
cd react
../deploy --env=local react --  npm start
```

## Deploy to Staging

Note: multiple people may be deploying to staging around the same time, you may overrwrite someone's code and vice-versa. If you really want to you can create `my-branch.env` and deploy to it like an environment. But we don't have any automation to cleanup these or monitor costs, so not recommended as a standard process, rather a one-off when needed.

```
./deploy react flask vue --env=staging
```

## Deploy to Prod

Normally you shouldn't need to do that since all merged changed are deployed automatically in Github CI.

Before proceeding, make sure you don't have any local changes to `production.env`.

```
./deploy react --env=production
```


## Updating The Apps (basic git commands)

```
# first time
git clone git@github.com:sentry-demos/empower.git
cd empower
# -- end
# returning
git checkout master
git pull -r
# -- end

git checkout -b my-feature-branch-name

# make changes, then stage one-by-one to only include what you want
git add -p
git commit -m "[react/flask/etc] description of change here"

# merge latest upstream changes
git fetch
git merge origin/master
# OR to avoid creating a merge commit
git pull -r
# -- end OR

# push branch create a PR
git push origin HEAD
```

## Troubleshooting

See [troubleshooting](./troubleshooting.md)

```
# get service name from <PROJECT>_APP_ENGINE_SERVICE in your *.env file OR
gcloud app services list
gcloud app logs tail -s <SERVICE>
```

`gcloud app deploy` does not support `--update-env-vars RELEASE=$RELEASE` like `gcloud run deploy` does with Cloud Run

## AI Suggestions (nextjs -> flask)

1. Run next and flask (./deploy --env=local next flask)
2. Get suggestion button should show automatically

## Caches & Queues (flask)

### Redis Configuration

Our Flask application uses Redis for two primary purposes:
1. **Caching**: Improves performance by storing frequently accessed data
2. **Message Queues**: Enables asynchronous task processing via Celery

Running `./deploy --env=local flask` will call `flask/local_run.sh` which manages all necessary processes so you don't need to do anything special:
1. SSH tunnel to Redis
2. Celery worker
3. Flask development server

#### Production/Staging Environment

In production/staging, we use a Google Cloud Redis instance that doesn't expose a public IP address for security reasons. The application connects directly to this Redis instance within the GCP network.
