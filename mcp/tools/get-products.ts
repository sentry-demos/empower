import { PlantProduct, PlantProductSummary } from "../types.js";
import { EMPOWER_PLANT_API_URL } from "../consts.js";
import { z } from "zod";
import { maybeThrow } from "../utils.js";

export const getProductsTool = {
  title: "Get Plant Products",
  annotations: {
    description: "Get a list of plant products from Empower Plant store",
  },
  inputSchema: {
    title: z
      .string()
      .optional()
      .describe(
        "Partial title of the product, matches any part of the title, case insensitive"
      ),
  },
  handler: async ({ title }: { title?: string }) => {
    const plants = await fetchPlantProducts(title);
    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(plants, null, 2),
        },
      ],
    };
  },
};

async function fetchPlantProducts(
  search?: string
): Promise<PlantProductSummary[]> {
  const response = await fetch(`${EMPOWER_PLANT_API_URL}/products`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  maybeThrow(0.1, new Error("Empower Plant API unreachable"));

  const products: PlantProduct[] = await response.json();

  const summaries: PlantProductSummary[] = products
    .filter((product) =>
      search ? product.title.toLowerCase().includes(search.toLowerCase()) : true
    )
    .map((product) => ({
      id: product.id,
      title: product.title,
      description: product.description,
      price: product.price,
    }));

  return summaries;
}
