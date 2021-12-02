// Copyright 2018 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

'use strict';

// Imported Functions
const DB = require('./db');

// [START app]
const express = require('express');
const app = express();
const cors = require('cors');
const sentryEventContext = function(req, res, next) {
  const se = req.headers.se;
  if(!['undefined'].includes(se)) {
    Sentry.setTag("se", se);
  }

  const customerType = req.headers.customertype;
  if(!['undefined'].includes(customerType)) {
    Sentry.setTag("customerType", customerType);
  }

  const email = req.headers.email;
  if(!['undefined'].includes(email)) {
    Sentry.setUser({ 'email': email })
  }

  // keep executing the router middleware
  next();
}

const dsn = process.env.EXPRESS_APP_DSN;
const release = process.env.RELEASE;
const environment = process.env.EXPRESS_ENV || "production";

console.log("> DSN", dsn);
console.log("> RELEASE", release);
console.log("> ENVIRONMENT", environment);

// Initialize Sentry
const Sentry = require('@sentry/node');
const Tracing = require('@sentry/tracing');
Sentry.init({
  dsn: dsn,
  environment: environment,
  release: release,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Tracing.Integrations.Express({ app })
  ],
  tracesSampleRate: 1.0,
  tracesSampler: samplingContext => {
    // sample out transactions for OPTIONS requests
    if (samplingContext.request.method == 'OPTIONS') {
      return 0.0
    }  else {

    }
  }
})

// The Sentry request handler must be the first middleware on the app
app.use(Sentry.Handlers.requestHandler());

// TracingHandler creates a trace for every incoming request
app.use(Sentry.Handlers.tracingHandler());

app.use(cors());
app.use(express.urlencoded({extended: true}));
app.use(express.json());
app.use(sentryEventContext);

// Configure ENV
require('dotenv').config();

app.get('/', (req, res) => {
  res.send('Sentry Node Service says Hello - turn me into a microservice that powers Payments, Shipping, or Customers');
});

app.get('/products', async (req, res) => {
  try {
    let transaction = Sentry.getCurrentHub()
      .getScope()
      .getTransaction();
    let span = transaction.startChild({ op: '/products.get_products', description: 'function' });
    const products = await DB.getProducts();
    span.finish();
    transaction.finish();
    res.status(200).send(products);
  } catch (error) {
    Sentry.captureException(error);
    throw(error);
  }
});

app.get('/products-join', async(req, res) => {
  try {
    let transaction = Sentry.getCurrentHub()
      .getScope()
      .getTransaction();
    let span = transaction.startChild({ op: '/products.get_products_join', description: 'function' });
    const products = await DB.getJoinedProducts();
    span.finish();
    transaction.finish();
    res.status(200).send(products);
  } catch (error) {
    Sentry.captureException(error);
    throw(error);
  }
});

app.post('/checkout', async(req, res) => {
  const order = req.body;
  const cart = order['cart'];
  const form = order['form'];
  let inventory = [];
  try {
    // Get Inventory
    let transaction = Sentry.startTransaction({ name: '/checkout.get_inventory' });
    let span = transaction.startChild({ op: '/checkout.get_inventory'});
    inventory = await DB.getInventory(cart);
    console.log("> /checkout inventory", inventory);
    span.finish();
    transaction.finish();

    // Process Order
    transaction = Sentry.startTransaction({ name: 'process order' });
    span = transaction.startChild({ op: 'process_order', description: 'function' });
    let quantities = cart['quantities'];
    console.log("quantities", quantities);
    for(const cartItem in quantities) {
      for(const inventoryItem of inventory) {
        console.log("> inventoryItem.count", inventoryItem['count']);
        if(inventoryItem.count < quantities[cartItem]) {
          throw("Not enough inventory for product");
        }
      }
    }
    span.finish();
    transaction.finish();
    res.status(200).send('success');
  } catch (error) {
    Sentry.captureException(error);
    res.status(500).send(error);
  }

});

app.use(Sentry.Handlers.errorHandler());

// Listen to the .env-specified, or default port otherwise
const PORT = process.env.PORT || 8088;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});
// [END app]

module.exports = { app, Sentry, Tracing };