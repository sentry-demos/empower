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
        // do i need to retrieve reviews in here...? is that stupidly clunky?
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
  // console.log(products);
  let reviews = [];
  products.forEach(
    (product) => {
      const review = knex.raw(
        `SELECT *, pg_sleep(0.25) FROM reviews WHERE productId = ${product.id}`
        ).then(
          (fetchedReview) => {
            console.log("fetched", fetchedReview.rows);
            // somehow make a dictionary -- checkout this
            // python struct in more detail - https://github.com/sentry-demos/application-monitoring/blob/master/flask/db.py#L57
            // what does that struct actually look like...?
            // const mapping = {
            //   product: {}
            // }
            reviews.push(fetchedReview.rows);
            return reviews;
          }
        )
    }
  );
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