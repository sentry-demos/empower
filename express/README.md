# Express (Node.js) Backend

## Setup

Create a local `express/.env` file. Talk to a SE team member to get valid contents for this file. 

Add REACT_APP_EXPRESS_BACKEND=<value> to react/.env. The value is the URL of the App Engine express instance.

There are other `.env` files in the other directories so ensure you get the contents for the Express one.

```
// Run the Express server locally in a test environment

$ cd express
$ npm install
$ ./run.sh
```

## Hitting The Express Backend

From the normal frontend demo url, add a query parameter `?backend=express` to any url. This will cause backend requests to be routed to the Express backend.

To confirm that the correct backend was hit, you will see output in the developer console, i.e.

```
fetching products from backend =>>>>>>>>> https://application-monitoring-node-dot-sales-engineering-sf.appspot.com/
```

### In Production
You can hit any route in production and add the `?backend=express` query parameter. An example would be: https://application-monitoring-react-dot-sales-engineering-sf.appspot.com/?backend=express.

In production, the Express backend is deployed to https://application-monitoring-node-dot-sales-engineering-sf.appspot.com/.

### Running Locally

You can hit any route locally and add the `?backend=express` query parameter. Let's say your React server is running on port 5000 locally. An example would be: http://localhost:5000/?backend=express.

Locally, the Express backend is served on port 8088 when you run `express/run.sh`.

### Cloud GCP Deployment
To deploy only the express service.

gcloud app deploy
gcloud app deploy --quiet