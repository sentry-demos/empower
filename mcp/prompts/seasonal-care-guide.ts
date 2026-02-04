import { randomDelay } from "../utils.js";
export const seasonalCareGuidePrompt = {
  metadata: {
    title: "Seasonal Plant Care Guide",
    description:
      "Get customized plant care advice based on current season and location",
    arguments: [
      {
        name: "season",
        description: "Current season (spring, summer, fall, winter)",
        required: true,
      },
      {
        name: "region",
        description: "Your climate region (temperate, tropical)",
        required: true,
      },
      {
        name: "plant_types",
        description: "Types of plants you're caring for (optional)",
        required: false,
      },
    ],
  },
  handler: async (args: any) => {
    await randomDelay(5, 30);
    const { season, region, plant_types } = args;
    const messages = [
      {
        role: "user" as const,
        content: {
          type: "text" as const,
          text: `I need seasonal plant care guidance for:
- **Season:** ${season}
- **Region:** ${region}
${plant_types ? `- **Plant Types:** ${plant_types}` : ""}

Using the seasonal calendar resources, please provide:
1. Key care activities for this time of year
2. Specific watering and fertilizing guidance
3. Environmental considerations (humidity, temperature, light)
4. Common problems to watch for this season
5. Preparation tasks for the upcoming season

Make the advice practical and actionable for my specific situation.`,
        },
      },
    ];

    return {
      description:
        "Seasonal plant care guidance tailored to your location and time of year",
      messages,
    };
  },
};
