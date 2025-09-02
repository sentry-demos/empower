require("dotenv").config();
const Sentry = require("@sentry/node");

// Knex is the database query builder used in the GCP docs, which
// is why we are using it here. See docs:
// https://cloud.google.com/sql/docs/postgres/connect-app-engine-standard#node.js
const knex = openDBConnection();

const getProducts = async function () {
  let results = [];
  try {
    // Retrieve Products

    // backorder_inventory is a "sleepy view", run the following query to get current sleep duration:
    // SELECT pg_get_viewdef('backorder_inventory', true)
    const productsQuery = `SELECT * FROM products CROSS JOIN backorder_inventory`;

    const products = await Sentry.startSpan(
      { op: "db.query.getproducts", description: productsQuery },
      async () => {
        return await knex.raw(productsQuery).catch((err) => {
          console.log("There was an error", err);
          throw err;
        });
      }
    );

    Sentry.setTag("totalProducts", products.rows.length);
    const span = Sentry.getActiveSpan();
    if (span) span.setAttribute("products", products.rows);

    // Retrieve Reviews
    Sentry.startSpan({ op: "db.query.getallreviews"}, () => true);

    let formattedProducts = [];
    for (const product of products.rows) {
      // weekly_promotions is a "sleepy view", run the following query to get current sleep duration:
      // SELECT pg_get_viewdef('weekly_promotions', true)
      const reviewsQuery = `SELECT * FROM reviews, weekly_promotions WHERE productId = ${product.id}`;

      await Sentry.startSpan({ op: "db.query.getreview", description: reviewsQuery }, () => true);

      const retrievedReviews = await knex.raw(reviewsQuery);
      let productWithReviews = product;
      productWithReviews["reviews"] = retrievedReviews.rows;
      formattedProducts.push(productWithReviews);
    }

    return formattedProducts;
  } catch (error) {
    Sentry.captureException(error);
    throw error;
  }
};

const getJoinedProducts = async function () {
  // Retrieve Products
  const productsQuery = `SELECT * FROM products`;

  let products;

  let span = Sentry.startSpan(
    { op: "db.query.getjoinedproducts", description: productsQuery },
    async () => {
      products = await knex.raw(productsQuery).catch((err) => {
        console.log("There was an error", err);
        throw err;
      });
    }
  );

  Sentry.setTag("totalProducts", products.rows.length);
  span.setAttribute("Products", products.rows);

  // Retrieve Reviews
  const reviewsQuery =
    "SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id";
  
  span = Sentry.startSpan(
    { op: "db.query.getjoinedproducts.reviews", description: reviewsQuery },
    async () => {}
  );
  
  const retrievedReviews = await knex.raw(reviewsQuery);
  span.setAttribute("reviews", retrievedReviews.rows);

  // Format Products/Reviews
  span = Sentry.startSpan(
    { op: "getjoinedproducts.formatresults", description: "function" },
    async () => {}
  );
  
  let formattedProducts = [];
  for (const product of products.rows) {
    let productWithReviews = product;
    productWithReviews["reviews"] = retrievedReviews.rows;
    formattedProducts.push(productWithReviews);
  }
  
  span.setAttribute("results", formattedProducts);

  return formattedProducts;
};

const getInventory = async function (cart) {
  console.log("> getting inventory");
  const quantities = cart["quantities"];
  console.log("> quantities", quantities);
  let productIds = [];
  
  for (const productId in quantities) {
    productIds.push(productId);
  }
  
  productIds = formatArray(productIds);
  console.log("> productIds", productIds);

  try {
    const inventoryQuery = `SELECT * FROM inventory WHERE productId in ${productIds}`;
    const inventory = await Sentry.startSpan(
      { name: "db.query.getInventory", description: inventoryQuery },
      async () => {
        return await knex.raw(inventoryQuery);
      }
    );

    const span = Sentry.getActiveSpan();
    span.setAttribute("inventory", inventory.rows);

    return inventory.rows;
  } catch (error) {
    Sentry.captureException(error);
    throw error;
  }
};

function formatArray(ids) {
  let numbers = "";
  for (const id of ids) {
    numbers += id + ",";
  }
  const output = "(" + numbers.substring(0, numbers.length - 1) + ")";
  return output;
}

function openDBConnection() {
  let host;
  if (process.env.EXPRESS_ENV === "test") {
    // The cloud sql instance connection
    // name doesn't work locally, but the
    // public IP of the instance does.
    host = process.env.DB_HOST;
  } else {
    host = "/cloudsql/" + process.env.DB_CLOUD_SQL_CONNECTION_NAME;
  }

  const db = require("knex")({
    client: "pg",
    connection: {
      user: process.env.DB_USERNAME,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_DATABASE,
      host: host,
    },
  });
  return db;
}

module.exports = { getProducts, getJoinedProducts, getInventory };
