require('dotenv').config();
const Sentry = require('@sentry/node');
const knex = openDBConnection();
const sleepTime = 0.2

const getProducts = async function() {
  let results = [];
  try {
    // Retrieve Products
    let transaction = Sentry.startTransaction({ name: 'get products - db query' });
    let span = transaction.startChild({ op: 'getproducts', description: 'db.query'})
    const products = await knex.raw(`SELECT *, pg_sleep(${sleepTime}) FROM products`)
      .catch((err) => {
        console.log("There was an error", err);
        throw err;
      })
    span.finish();
    transaction.finish();

    // Retrieve Reviews
    transaction = Sentry.startTransaction({ name: 'get reviews - db query'});
    span = transaction.startChild({ op: 'getproducts.reviews', description: 'db.query'});
    let formattedProducts = [];
    for(product of products.rows) {
      const retrievedReviews = await knex.raw(
        `SELECT *, pg_sleep(0.25) FROM reviews WHERE productId = ${product.id}`
      );
      let productWithReviews = product;
      productWithReviews['reviews'] = retrievedReviews.rows;
      formattedProducts.push(productWithReviews);
    }
    span.finish();
    transaction.finish();
    return formattedProducts;
  } catch(error) {
    Sentry.captureException(error);
    throw error;
  }
}

const getJoinedProducts = async function() {
  let transaction = Sentry.startTransaction({ name: 'get joined products' });
  let span = transaction.startChild({ op: 'getjoinedproducts', description: 'db.query' });

  // Retrieve Products
  const products = await knex.raw(`SELECT * FROM products`)
      .catch((err) => {
        console.log("There was an error", err);
        throw err;
      })
  span.finish();
  transaction.finish();

  // Retrieve Reviews
  transaction = Sentry.startTransaction({ name: 'get joined product reviews'});
  span = transaction.startChild({ op: 'getjoinedproducts.reviews', description: 'db.query' });
  let formattedProducts = [];
  for(product of products.rows) {
    const retrievedReviews = await knex.raw(
      "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id"
    );
    let productWithReviews = product;
    productWithReviews['reviews'] = retrievedReviews.rows;
    formattedProducts.push(productWithReviews);
  }
  //TODO: do I need span.setData? i.e. https://github.com/sentry-demos/application-monitoring/blob/master/flask/db.py#L101
  // appears in multiple places in the function
  span.finish();
  transaction.finish();
  return formattedProducts;
}

function openDBConnection() {
  const transaction = Sentry.startTransaction({ name: 'open db connection' });
  const span = transaction.startChild({ op: 'getproducts', description: 'db.connect'})
  const db = require('knex')({
    client: 'pg',
    connection: {
      user: process.env.USERNAME,
      password: process.env.PASSWORD,
      database: process.env.DATABASE,
      host: process.env.CLOUD_SQL_CONNECTION_IP
    }
  });
  span.finish();
  transaction.finish();
  return db;
}

module.exports = { getProducts, getJoinedProducts }