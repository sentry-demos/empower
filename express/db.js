const getProducts = async function() {
    const knex = require('knex')({
        client: 'pg',
        connection: {
            user: process.env.USERNAME,
            password: process.env.PASSWORD,
            database: process.env.DATABASE,
            host: process.env.CLOUD_SQL_CONNECTION_IP
        }
    });
  
    let products = await knex('products').then(
        (listProducts) => {
            return listProducts;
        }
    ).catch((err) => {
        console.log("There was an error", err);
        throw err;
    })
    return products;
}

module.exports = { getProducts }