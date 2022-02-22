# Ruby (Rails) Backend

## Setup

Create a local `ruby/.env` file. Talk to a SE team member to get valid contents for this file?

Add REACT_APP_RUBY_BACKEND=<value> to react/.env. The value is the URL of the App Engine ruby instance.

There are other `.env` files in the other directories so ensure you get the contents for the ruby one?

You may need ruby 2.7. You may use rbenv to do this but it's not required.

```
// Run the ruby server locally in a test environment

$ cd ruby
$ bundle install
```

## Run
```
./run.sh
```

Visit http://localhost:3000/api/organization

Also...bin/rails server -p 3001
Also...don't care about the web html being served at localhost:3000/

## Hitting The ruby Backend

From the normal frontend demo url, add a query parameter `?backend=ruby` to any url. This will cause backend requests to be routed to the ruby backend.

To confirm that the correct backend was hit, you will see output in the developer console, i.e.

```
fetching products from backend =>>>>>>>>> https://application-monitoring-node-dot-sales-engineering-sf.appspot.com/
```

### In Production
You can hit any route in production and add the `?backend=ruby` query parameter. An example would be: https://application-monitoring-react-dot-sales-engineering-sf.appspot.com/?backend=ruby.

In production, the ruby backend is deployed to https://application-monitoring-node-dot-sales-engineering-sf.appspot.com/.

### Running Locally

You can hit any route locally and add the `?backend=ruby` query parameter. Let's say your React server is running on port 5000 locally. An example would be: http://localhost:5000/?backend=ruby.

Locally, the ruby backend is served on port 8088 when you run `ruby/run.sh`.

### Cloud GCP Deployment
To deploy only the ruby service.

```
gcloud app deploy
gcloud app deploy --quiet
```

If you get an error about invalid authentication credentials, try running this first:
```
gcloud auth login
```