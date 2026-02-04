import { randomDelay } from "../utils.js";
export const plantShoppingAssistantPrompt = {
  metadata: {
    title: "Plant Shopping Assistant",
    description:
      "Get personalized product recommendations for your plant care needs",
    arguments: [
      {
        name: "needs",
        description:
          "What you're looking for (e.g., monitoring tools, watering solutions, plant food)",
        required: true,
      },
      {
        name: "budget",
        description: "Your budget range (optional)",
        required: false,
      },
      {
        name: "plant_types",
        description: "Types of plants you're shopping for (optional)",
        required: false,
      },
    ],
  },
  handler: async (args: any) => {
    await randomDelay(10, 50);

    const { needs, budget, plant_types } = args;
    const messages = [
      {
        role: "user" as const,
        content: {
          type: "text" as const,
          text: `I'm looking for plant care products:

**What I need:** ${needs}
${budget ? `**Budget:** ${budget}` : ""}
${plant_types ? `**Plant Types:** ${plant_types}` : ""}

Please help me by:
1. Searching the product catalog for relevant items
2. Comparing features and prices
3. Reading customer reviews and ratings
4. Making personalized recommendations based on my needs
5. Explaining how each product would help with my specific situation

Focus on products that offer the best value and effectiveness for my needs.`,
        },
      },
    ];

    return {
      description:
        "Personalized plant product recommendations with detailed comparisons",
      messages,
    };
  },
};
