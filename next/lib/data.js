import { sql } from "@vercel/postgres";

import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

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


export default async function getProducts() {
  try {
    console.log("Fetching products...");
    // Artificial slowdown for demoing
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const products = await prisma.products.findMany();
    // const products = data.rows;

    for (let i = 0; i < products.length; ++i) {

      const product_reviews = await prisma.reviews.findMany({
        where: { id: i },
      });

      products[i].reviews = product_reviews;
    }
    console.log("products: ", products);
    return products;
  } catch (error) {
    console.error("Database Error:", error)
    // do sentry stuff
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
}

export async function getProductsPrisma() {
  const products = await prisma.products.findMany();
  console.log("prisma", products);
}
