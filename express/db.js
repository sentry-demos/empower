require('dotenv').config();
const Sentry = require('@sentry/node');
const knex = openDBConnection();
const sleepTime = 0.25

const getProducts = async function() {
  let results = [];
  try {
    // Retrieve Products
    let transaction = Sentry.startTransaction({ name: 'get_products db query' });
    let span = transaction.startChild({ op: 'get_products', description: 'db.query'})
    const products = await knex.raw(`SELECT *, pg_sleep(${sleepTime}) FROM products`)
      .catch((err) => {
        console.log("There was an error", err);
        throw err;
      })
    span.finish();
    transaction.finish();
    return products.rows;
  } catch(error) {
    Sentry.captureException(error);
    throw error;
  }
}

const getReviews = async function(products) {
  // Retrieve Reviews
  transaction = Sentry.startTransaction({ name: 'get_reviews db query'});
  span = transaction.startChild({ op: 'get_products.reviews', description: 'db.query'});
  let reviews = [];
  for(product of products) {
    const retrievedReviews = await knex.raw(
      `SELECT *, pg_sleep(0.25) FROM reviews WHERE productId = ${product.id}`
    )
    let productWithReviews = product;
    productWithReviews['reviews'] = retrievedReviews.rows;
    reviews.push(productWithReviews);
  }
  return reviews;
}

function openDBConnection() {
  const transaction = Sentry.startTransaction({ name: 'open db connection' });
  const span = transaction.startChild({ op: 'get_products', description: 'db.connect'})
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

module.exports = { getProducts, getReviews }