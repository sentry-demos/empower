import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { PlantProduct, ProductResourceItem } from "../types.js";
import { EMPOWER_PLANT_API_URL } from "../consts.js";

export const productsResource = {
  template: new ResourceTemplate("empower://products", {
    // Provide list callback so resource appears in resources/list
    list: async () => ({
      resources: [
        {
          uri: "empower://products",
          name: "Products",
          description:
            "List of available products from Empower Plant store with names, prices, descriptions, and customer reviews",
          mimeType: "application/json",
        },
      ],
    }),
  }),
  metadata: {
    name: "Products",
    description:
      "List of available products from Empower Plant store with names, prices, descriptions, and customer reviews",
    mimeType: "application/json",
  },
  handler: async (_uri: URL) => {
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

    return {
      contents: [
        {
          uri: "empower://products",
          mimeType: "application/json",
          text: JSON.stringify(simplifiedProducts, null, 2),
        },
      ],
    };
  },
};
