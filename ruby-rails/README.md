# Ruby (Rails) Backend

## Setup

Create a local `ruby/.env` file. Talk to a SE team member to get valid contents for this file?

Add REACT_APP_RUBY_BACKEND=<value> to react/.env. The value is the URL of the App Engine ruby instance.

You may need ruby 2.7. You may use rbenv to do this but it's not required.

```
// Run the ruby server locally in a test environment

$ cd ruby-rails
$ bundle install
```

Troubleshooting ruby versions? Install rbenv.
```
rbenv versions --list # shows versions for download
rbenv versions # shows if 2.7.5 is already downloaded
rbenv init
eval "$(rbenv init - zsh)"
rbenv --version # should say 2.7.5
rbenv global 3.1.1
```

## Run
```
./run.sh
```

Visit http://localhost:3000/api/organization

Also...bin/rails server -p 3001
Also...don't care about the web html being served at localhost:3000/

Locally, the ruby backend is served on port 8088 or 4567 when you run `ruby/run.sh`.

### Production - Cloud GCP Deployment
In production, the ruby backend is deployed to https://application-monitoring-ruby-dot-sales-engineering-sf.appspot.com/.

To deploy only the ruby service.

```
gcloud app deploy
gcloud app deploy --quiet
```

If you get an error about invalid authentication credentials, try running this first:
```
gcloud auth login
```

https://github.com/GoogleCloudPlatform/ruby-docs-samples/tree/master/appengine
