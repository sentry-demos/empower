import { PlantProduct, ProductResourceItem } from "../types.js";
import { EMPOWER_PLANT_API_URL } from "../consts.js";

export const getProductsTool = {
  description:
    "Get all available products from the Empower Plant store with names, prices, descriptions, and customer reviews",
  parameters: {
    type: "object" as const,
    properties: {},
    required: [] as string[],
  },
  handler: async () => {
    // Use products-join for faster response (single SQL query with JOIN)
    const response = await fetch(`${EMPOWER_PLANT_API_URL}/products-join`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        se: "mcp-server",
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const products: PlantProduct[] = await response.json();

    // Transform to simplified structure with review texts
    const simplifiedProducts: ProductResourceItem[] = products.map(
      (product) => ({
        id: product.id,
        name: product.title,
        price: product.price,
        description: product.description,
        reviews: product.reviews
          .filter((review) => review.description)
          .map((review) => review.description as string),
      })
    );

    // Return in MCP tool response format
    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(simplifiedProducts, null, 2),
        },
      ],
    };
  },
};
