import { sql } from "@vercel/postgres";
import * as Sentry from '@sentry/nextjs';

// export type Product = {
//   id: number;
//   description: string;
//   descriptionfull: string;
//   price: number;
//   img: string;
//   imgcropped: string;
//   reviews: Review[] | [];
// }

// export type Review = {
//   id: number;
//   productid: number;
//   rating: number;
//   customerid: string;
//   description: string;
//   created: string;
// }


export default async function getProducts(a) {
  console.log("random number: ", a);
  const result = await Sentry.startSpan(
    { name: "query db" },
    async () => {
      try {
        console.log("Fetching products...");
        // Artificial slowdown for demoing
        await new Promise((resolve) => setTimeout(resolve, 2000));

        const data = await sql`SELECT * from products WHERE id != ${a + 1000}`;
        const products = data.rows;

        for (let i = 0; i < products.length; ++i) {
          const product_reviews = await getReview(i);
          products[i].reviews = product_reviews;
        }
        console.log(products);
        return products;
      } catch (error) {
        console.error("Database Error:", error)
        // do sentry stuff
      }
    });

  return result;
}



async function getReview(i) {
  try {
    const data = await sql`SELECT * from reviews WHERE productId=${i}`;
    console.log(data.rows);
    return data.rows;
  } catch (error) {
    console.error("Db error", error);
  }
}
