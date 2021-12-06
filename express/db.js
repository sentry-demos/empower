require('dotenv').config();
const Sentry = require('@sentry/node');

// Knex is the database query builder used in the GCP docs, which
// is why we are using it here. See docs:
// https://cloud.google.com/sql/docs/postgres/connect-app-engine-standard#node.js
const knex = openDBConnection();
const sleepTime = 0.2;

const getProducts = async function() {
  let results = [];
  try {
    // Retrieve Products
    let transaction = Sentry.getCurrentHub()
      .getScope()
      .getTransaction();
    let span = transaction.startChild({ op: 'getproducts', description: 'db.query'});
    const productsQuery = `SELECT *, pg_sleep(${sleepTime}) FROM products`;
    const subspan = span.startChild({op: 'fetch products', description: productsQuery});
    console.log("> productsQuery", productsQuery)
    const products = await knex.raw(productsQuery)
      .catch((err) => {
        console.log("There was an error", err);
        throw err;
      })
    Sentry.setTag("totalProducts", products.rows.length);
    span.setData("Products", products.rows);
    subspan.finish();
    span.finish();

    // Retrieve Reviews
    span = transaction.startChild({ op: 'getproducts.reviews', description: 'db.query'});
    let formattedProducts = [];
    for(product of products.rows) {
      const reviewsQuery = `SELECT *, pg_sleep(0.25) FROM reviews WHERE productId = ${product.id}`;
      const subspan = span.startChild({op: 'fetch review', description: reviewsQuery});
      const retrievedReviews = await knex.raw(reviewsQuery);
      let productWithReviews = product;
      productWithReviews['reviews'] = retrievedReviews.rows;
      formattedProducts.push(productWithReviews);
      subspan.setData("Reviews", retrievedReviews.rows);
      subspan.finish();
    }
    span.setData("Products With Reviews", formattedProducts);
    span.finish();
    transaction.finish();
    return formattedProducts;
  } catch(error) {
    Sentry.captureException(error);
    throw error;
  }
}

const getJoinedProducts = async function() {
  let transaction = Sentry.getCurrentHub()
      .getScope()
      .getTransaction();

  // Retrieve Products
  const productsQuery = `SELECT * FROM products`
  let span = transaction.startChild({ op: 'getjoinedproducts', description: productsQuery });
  const products = await knex.raw(productsQuery)
      .catch((err) => {
        console.log("There was an error", err);
        throw err;
      })
  Sentry.setTag("totalProducts", products.rows.length);
  span.setData("Products", products.rows)
  span.finish();

  // Retrieve Reviews
  const reviewsQuery = "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id";
  span = transaction.startChild({ op: 'getjoinedproducts.reviews', description: reviewsQuery });
  const retrievedReviews = await knex.raw(
    reviewsQuery
  );
  span.setData("reviews", retrievedReviews.rows);
  span.finish();

  // Format Products/Reviews
  span = transaction.startChild({ op: 'getjoinedproducts.formatresults', description: 'function' })
  let formattedProducts = [];
  for(product of products.rows) {
    let productWithReviews = product;
    productWithReviews['reviews'] = retrievedReviews.rows;
    formattedProducts.push(productWithReviews);
  }
  span.setData("results", formattedProducts);
  span.finish();

  transaction.finish();
  return formattedProducts;
}

const getInventory = async function(cart) {
  console.log("> getting inventory");
  const quantities = cart['quantities'];
  console.log("> quantities", quantities);
  let productIds = [];
  for(productId in quantities) {
    productIds.push(productId)
  }
  productIds = formatArray(productIds);
  console.log("> productIds", productIds);
  try {
    let transaction = Sentry.startTransaction({ name: 'get inventory' });
    let span = transaction.startChild({ op: 'get_inventory', description: 'db.query' });
    const inventory = await knex.raw(
      `SELECT * FROM inventory WHERE productId in ${productIds}`
    )
    span.setData("inventory", inventory.rows);
    return inventory.rows
  } catch(error) {
    Sentry.captureException(error);
    throw err;
  }
}

function formatArray(ids) {
  let numbers = "";
  for(id of ids) {
    numbers += (id + ",");
  }
  const output = "(" + numbers.substring(0, numbers.length - 1) + ")";
  return output;
}

function openDBConnection() {
  const transaction = Sentry.startTransaction({ name: 'open db connection' });
  const span = transaction.startChild({ op: 'getproducts', description: 'db.connect'})

  let host
  if (process.env.EXPRESS_ENV === 'test') {
    // The cloud sql instance connection
    // name doesn't work locally, but the
    // public IP of the instance does.
    host = process.env.CLOUD_SQL_PUBLIC_IP
  } else {
    host = '/cloudsql/' + process.env.CLOUD_SQL_CONNECTION_NAME
  }
  console.log("> host ", host)
  console.log("> DB \n", {
    client: 'pg',
    connection: {
      user: process.env.USERNAME,
      password: process.env.PASSWORD,
      database: process.env.DATABASE,
      host: host
    }
  })
  const db = require('knex')({
    client: 'pg',
    connection: {
      user: process.env.USERNAME,
      password: process.env.PASSWORD,
      database: process.env.DATABASE,
      host: host
    }
  });
  span.finish();
  transaction.finish();
  return db;
}

module.exports = { getProducts, getJoinedProducts, getInventory }