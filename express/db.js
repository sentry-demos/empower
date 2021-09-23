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
    const products = await knex.raw(`SELECT *, pg_sleep(${sleepTime}) FROM products`).then(
      (listProducts) => {
        return listProducts;
        // currently retrieving reviews in a separate func,
        // but it could also probably go here. Wonder if that's
        // part of my issues?
      }
    ).catch((err) => {
      console.log("There was an error", err);
      throw err;
    })
    span.finish();
    transaction.finish();
    return products;
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
  products.forEach(
    (product) => {
      const review = knex.raw(
        `SELECT *, pg_sleep(0.25) FROM reviews WHERE productId = ${product.id}`
        ).then(
          (fetchedReview) => {
            console.log("fetched", fetchedReview.rows);
            reviews.push(fetchedReview.rows);
            return reviews;
          }
        )
    }
  );
  // Not understanding async stuff here...
  // Why is this returning an empty array instead
  // of waiting for the loop above to fill the reviews
  // array with DB data?
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