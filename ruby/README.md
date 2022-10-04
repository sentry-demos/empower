# Ruby (Rails) Backend

## Setup

In react/.env add REACT_APP_RUBY_BACKEND=<value> with a URL for the hosted Ruby backend, the App Engine instance.

Flask, Express, SpringBoot and Mobile may have .env files too where you can specify this same backend URL, so update those as needed.

```
cd ruby
bundle install
```

```
rbenv versions
ruby --version
ruby 3.1.1p18 (2022-02-18 revision 53f5fc4236) [x86_64-darwin19]
```

### Run
```
./run.sh
```
The local ruby backend is served on localhost:4567 when you run `ruby/run.sh`.

### Cloud GCP Deployment
To deploy the ruby service.

```
gcloud app deploy
gcloud app deploy --quiet
```

If you get an error about invalid authentication credentials, try running this first:
```
gcloud auth login
```


## Upgrade Pathway
update version in Gemfile.lock  
bundle update sentry-ruby  
bundle update sentry-ruby-core  
