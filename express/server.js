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

require("./instrument")

const express = require("express");
const Sentry = require("@sentry/node");
const axios = require("axios");
const cors = require("cors");

// Imported Functions
const DB = require("./db");
const utils = require("./utils");

// Environment variables
const BACKEND_URL_RUBYONRAILS = process.env.BACKEND_URL_RUBYONRAILS;
const PORT = process.env.PORT;

// [START app]
const app = express();
const headers = {};

// Middleware function to set Sentry context
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

// Helper function to check inventory
function hasInventory(item) {
  return false;
}

// Route handlers
async function fetchProducts(req, res) {
  try {
    // This /api call must happen before the DB.products() call or else it's a broken subtrace
    // (if you do it after DB.Products())
    await axios
      .get(BACKEND_URL_RUBYONRAILS + "/api", { headers: headers })
      .then((response) => {
        console.log("> response", response.data);
        return;
      })
      .catch((error) => {
        console.log(error);
        Sentry.captureException(error);
      });

    const products = await DB.getProducts();
    
    const span = await Sentry.startSpan(
      { op: "function", description: "products.get_iterator" },
      async () => {
        await utils.getIteratorProcessor(products);
      }
    );

    res.status(200).send(products);
  } catch (error) {
    Sentry.captureException(error);
    throw error;
  }
}

// Middleware setup
app.use(cors());
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(sentryEventContext);

// Configure ENV
require("dotenv").config();

// Routes
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
    // This /api call must happen before the DB.products() call or else it's a broken subtrace
    // (if you do it after DB.Products())
    await axios
      .get(BACKEND_URL_RUBYONRAILS + "/api", { headers: headers })
      .then((response) => {
        console.log("> response", response.data);
        return;
      })
      .catch((error) => {
        console.log(error);
        Sentry.captureException(error);
      });

    const products = await Sentry.startSpan(
      { op: "function", description: "products.get_products_join" },
      async () => {
        return await DB.getJoinedProducts();
      }
    );

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

  try {
    const inventory = await Sentry.startSpan(
      { name: "function", op: "checkout.get_inventory" },
      async () => {
        return await DB.getInventory(cart);
      }
    );

    console.log("> /checkout inventory", inventory);

    const quantities = await Sentry.startSpan(
      { name: "function", op: "processorder" },
      () => {
        return cart["quantities"];
      }
    );

    console.log("quantities", quantities);

    for (const cartItem in quantities) {
      if (!hasInventory(cartItem)) {
        throw new Error("Not enough inventory for product");
      }
    }

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

Sentry.setupExpressErrorHandler(app);

// Start server
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});
// [END app]

module.exports = { app, Sentry };
