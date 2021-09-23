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
app.use(cors());

// Configure ENV
require('dotenv').config();

// Initialize Sentry
const Sentry = require('@sentry/node');
const Tracing = require('@sentry/tracing');
Sentry.init({
  dsn: 'https://6de3af6bd0de437694e2b908b1223014@o87286.ingest.sentry.io/5963130',
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Tracing.Integrations.Express({ app })
  ],
  tracesSampleRate: 1.0
})


app.get('/', (req, res) => {
  res.send('Sentry Node Service says Hello - turn me into a microservice that powers Payments, Shipping, or Customers');
});

app.get('/products', async (req, res) => {
  try {
    let transaction = Sentry.startTransaction( { name: '/products.get_products' });
    let span = transaction.startChild({ op: '/products.get_products', description: 'function' });
    const products = await DB.getProducts();
    span.finish();
    transaction.finish();
    res.send(products);
  } catch (error) {
    Sentry.captureException(error);
    throw(error);
  }
});

app.get('/products-join', async(req, res) => {
  try {
    let transaction = Sentry.startTransaction( { name: '/products.get_products' });
    let span = transaction.startChild({ op: '/products.get_products', description: 'function' });
    const products = await DB.getJoinedProducts();
    span.finish();
    transaction.finish();
    res.send(products);
  } catch (error) {
    Sentry.captureException(error);
    throw(error);
  }
});

// Listen to the App Engine-specified port, or 8080 otherwise
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});
// [END app]

module.exports = { app, Sentry, Tracing };