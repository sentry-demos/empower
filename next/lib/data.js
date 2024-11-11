'use server'
import { PrismaClient } from '@prisma/client';
import { determineBackendUrl } from '@/src/utils/backendrouter';
import { isOddReleaseWeek, busy_sleep } from '@/src/utils/time';
import { ServerActionError, createServerAction } from '@/src/utils/serverActionError';
import * as Sentry from '@sentry/nextjs';

const prisma = new PrismaClient();


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
}

export async function getProduct(index) {
  const i = Number(index);
  try {
    console.log("Fetching product...");
    console.log(i);
    const product = await prisma.products.findUnique({
      where: { id: i }
    });

    const product_reviews = await prisma.reviews.findMany({
      where: { id: i },
    });

    product.reviews = product_reviews;
    return product;
  } catch (error) {
    console.error("Database Error:", error);
  }
}

export async function checkoutAction(cart) {
  console.log("cart ", cart);
  const inventory = await getInventory(cart);

  console.log("> /checkout inventory", inventory)


  if (inventory.length === 0 || cart.quantities.length === 0) {
    const error = new Error("Not enough inventory for product")
    Sentry.captureException(error);
    throw error;
  }

  for (let inventoryItem of inventory) {
    let id = inventoryItem.id;
    console.log(inventoryItem.count, cart.quantities[id]);
    if (inventoryItem.count < cart.quantities[id] || cart.quantities[id] >= inventoryItem.count) {
      throw new ServerActionError("Not enough inventory for product");
    //   const error = new Error("Not enough inventory for product")

    //   Sentry.captureException(error);
    //   throw error;
    }
  }

  return {status : 200, message: "success"}
}


export async function getInventory(cart) {
  console.log("> getInventory");

  const quantities = cart['quantities'];
  console.log("> quantities", quantities);

  let productIds = []

  Object.entries(quantities).forEach(([key, value]) => productIds.push(Number(key)));
  console.log("> product ids", productIds);
  let inventory;
  try {
    inventory = await prisma.inventory.findMany({
      where: { id : { in : productIds } }
    });
  } catch (error) {
    console.log("Database Error:", error);
  }
  console.log("inventory: ", inventory);
  return inventory;
}



export async function getAbout(backend) {
  if (!isOddReleaseWeek()) {
    // can't have async sleep in a constructor
    busy_sleep(Math.random(25) + 100);
  }

  const url = determineBackendUrl(backend);
  // Http requests to make in parallel, so the Transaction has more Spans
  let request1 = fetch(url + '/api', {
    method: 'GET',
  });
  let request2 = fetch(url + '/organization', {
    method: 'GET',
  });
  let request3 = fetch(url + '/connect', {
    method: 'GET',
  });

  // Need Safari13 in tests/config.py in order for this modern javascript to work in Safari Browser
  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled#browser_compatibility
  // let response = await Promise.allSettled([request1, request2, request3])

  const [response1, response2, response3] = await Promise.all([request1, request2, request3]);

  console.log([response1, response2, response3]);
  const responses = [response1, response2, response3];
  // Error Handling
  responses.forEach((r) => {
    if (!r.ok) {
      Sentry.withScope((scope) => {
        scope.setContext('response', r);
        Sentry.captureException(
          new Error(
            r.status + ' - ' + (r.statusText || 'Server Error for API')
          )
        );
      });
    }
  });
}
