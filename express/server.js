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

"use strict";
const axios = require("axios");

// Imported Functions
const DB = require("./db");

// Utils
const utils = require("./utils");

// [START app]
const express = require("express");
const app = express();
const cors = require("cors");
var headers = {};
const sentryEventContext = function (req, res, next) {
  const se = req.headers.se;

  if (se !== undefined) {
    Sentry.setTag("se", se);
    headers["se"] = se;
  }

  const customerType = req.headers.customertype;
  if (customerType !== undefined) {
    Sentry.setTag("customerType", customerType);
    headers["customerType"] = customerType;
  }

  const email = req.headers.email;
  if (email !== undefined) {
    Sentry.setUser({ email: email });
    headers["email"] = email;
  }

  // keep executing the router middleware
  next();
};

const dsn = process.env.EXPRESS_APP_DSN;
const release = process.env.RELEASE;
const environment = process.env.EXPRESS_ENV;
const RUBY_BACKEND = process.env.RUBY_BACKEND;

console.log("> DSN", dsn);
console.log("> RELEASE", release);
console.log("> ENVIRONMENT", environment);

// Initialize Sentry
const Sentry = require("@sentry/node");
const Tracing = require("@sentry/tracing");
const { ProfilingIntegration } = require("@sentry/profiling-node");
Sentry.init({
  dsn: dsn,
  environment: environment,
  release: release,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Tracing.Integrations.Express({ app }),
    new ProfilingIntegration(),
    new Sentry.Integrations.LocalVariables({
      captureAllExceptions: true,
    }),
  ],
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  tracesSampler: (samplingContext) => {
    // sample out transactions from http OPTIONS requests hitting endpoints
    const request = samplingContext.request;
    if (request && request.method == "OPTIONS") {
      return 0.0;
    } else {
      return 1.0;
    }
  },
  includeLocalVariables: true,
});

async function fetchProducts(req, res) {
  try {
    // This /api call must happen before the DB.products() call or else it's a broken subtrace (if you do it after DB.Products())
    await axios
      .get(RUBY_BACKEND + "/api", { headers: headers })
      .then((response) => {
        console.log("> response", response.data);
        return;
      })
      .catch((error) => {
        console.log(error);
        Sentry.captureException(error);
      });

    let transaction = Sentry.getCurrentHub().getScope().getTransaction();

    const products = await DB.getProducts();

    let profilingSpan = transaction.startChild({
      op: "/products.get_iterator",
      description: "function",
    });

    await utils.getIteratorProcessor(products);

    profilingSpan.finish();
    transaction.finish();

    res.status(200).send(products);
  } catch (error) {
    Sentry.captureException(error);
    throw error;
  }
}

// The Sentry request handler must be the first middleware on the app
app.use(Sentry.Handlers.requestHandler());

// TracingHandler creates a trace for every incoming request
app.use(Sentry.Handlers.tracingHandler());

app.use(cors());
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(sentryEventContext);

// Configure ENV
require("dotenv").config();

app.get("/", (req, res) => {
  res.send(
    "Sentry Express Service says Hello - turn me into a microservice that powers Payments, Shipping, or Customers"
  );
});

app.get("/success", (req, res) => {
  console.log("> success");
  res.send(`success from express`);
});

app.get("/products", fetchProducts);

app.get("/products-join", async (req, res) => {
  try {
    // This /api call must happen before the DB.products() call or else it's a broken subtrace (if you do it after DB.Products())
    await axios
      .get(RUBY_BACKEND + "/api", { headers: headers })
      .then((response) => {
        console.log("> response", response.data);
        return;
      })
      .catch((error) => {
        console.log(error);
        Sentry.captureException(error);
      });

    let transaction = Sentry.getCurrentHub().getScope().getTransaction();
    let span = transaction.startChild({
      op: "/products.get_products_join",
      description: "function",
    });
    const products = await DB.getJoinedProducts();
    span.finish();

    res.status(200).send(products);
  } catch (error) {
    Sentry.captureException(error);
    throw error;
  }
});

app.post("/checkout", async (req, res) => {
  const order = req.body;
  const cart = order["cart"];
  const form = order["form"];
  let inventory = [];
  try {
    const transaction = Sentry.getCurrentHub().getScope().getTransaction();

    // Get Inventory
    let spanGetInventory = transaction.startChild({
      op: "function",
      description: "getInventory",
    });
    inventory = await DB.getInventory(cart);
    console.log("> /checkout inventory", inventory);

    spanGetInventory.finish();

    // Process Order
    let spanProcessOrder = transaction.startChild({
      op: "function",
      description: "processOrder",
    });
    let quantities = cart["quantities"];
    console.log("quantities", quantities);
    for (const cartItem in quantities) {
      for (const inventoryItem of inventory) {
        console.log("> inventoryItem.count", inventoryItem["count"]);
        if (inventoryItem.count < quantities[cartItem]) {
          throw new Error("Not enough inventory for product");
        }
      }
    }
    spanProcessOrder.finish();

    res.status(200).send("success");
  } catch (error) {
    Sentry.captureException(error);
    res.status(500).send(error);
  }
});

app.get("/api", (req, res) => {
  res.send(`express /api`);
});

app.get("/connect", (req, res) => {
  res.send(`express /connect`);
});

app.get("/organization", (req, res) => {
  res.send(`express /organization`);
});

app.use(Sentry.Handlers.errorHandler());

const PORT = process.env.PORT;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});
// [END app]

module.exports = { app, Sentry, Tracing };
