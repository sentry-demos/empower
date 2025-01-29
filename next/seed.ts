import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // Seed products
  const products = await prisma.products.createMany({
    data: [
      {
        title: 'Mood Planter',
        description: 'A stylish planter that adds character to any room',
        descriptionfull:
          'This unique planter brings both style and functionality to your space. Perfect for small to medium-sized plants, its modern design complements any interior décor.',
        price: 2999, // $29.99
        img: '/assets/mood-planter.jpg',
        imgcropped: '/assets/mood-planter-cropped.jpg',
      },
      {
        title: 'Spider Plant',
        description: 'Easy-care spider plant that purifies your air',
        descriptionfull:
          'The Spider Plant is one of the most adaptable houseplants and is perfect for beginners. These plants are excellent air purifiers and look great in hanging baskets.',
        price: 1999, // $19.99
        img: '/assets/plant-spider.jpg',
        imgcropped: '/assets/plant-spider-cropped.jpg',
      },
      {
        title: 'Text Plant',
        description: 'A decorative plant with unique text-like patterns',
        descriptionfull:
          'This fascinating plant features distinctive leaf patterns that resemble text, making it a perfect conversation starter. Low maintenance and suitable for indoor environments.',
        price: 2499, // $24.99
        img: '/assets/plant-to-text.jpg',
        imgcropped: '/assets/plant-to-text-cropped.jpg',
      },
    ],
  });

  // Seed inventory
  const inventory = await prisma.inventory.createMany({
    data: [
      {
        sku: 'MOOD-001',
        count: 25,
        productid: 1,
      },
      {
        sku: 'SPDR-001',
        count: 30,
        productid: 2,
      },
      {
        sku: 'TEXT-001',
        count: 20,
        productid: 3,
      },
    ],
  });

  // Seed reviews
  const reviews = await prisma.reviews.createMany({
    data: [
      {
        productid: 1,
        rating: 5,
        customerid: 1,
        description: 'Beautiful planter, perfect size for my snake plant!',
      },
      {
        productid: 2,
        rating: 5,
        customerid: 2,
        description: 'My spider plant is thriving and so easy to care for.',
      },
      {
        productid: 3,
        rating: 4,
        customerid: 3,
        description: 'Unique plant, gets lots of comments from visitors.',
      },
    ],
  });

  console.log('Database has been seeded! 🌱');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
