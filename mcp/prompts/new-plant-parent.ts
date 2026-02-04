import { randomDelay } from "../utils.js";
export const newPlantParentPrompt = {
  metadata: {
    title: "New Plant Parent Guide",
    description:
      "Comprehensive guidance for beginners starting their plant journey",
    arguments: [
      {
        name: "experience_level",
        description:
          "Your experience level (complete beginner, some experience, etc.)",
        required: false,
      },
      {
        name: "living_situation",
        description:
          "Your living situation (apartment, house, available light, etc.)",
        required: false,
      },
      {
        name: "goals",
        description:
          "What you hope to achieve with plants (decoration, air purification, hobby, etc.)",
        required: false,
      },
    ],
  },
  handler: async (args: any) => {
    await randomDelay(20, 70);

    const { experience_level, living_situation, goals } = args;
    const messages = [
      {
        role: "user" as const,
        content: {
          type: "text" as const,
          text: `I'm new to plant parenting and need guidance:

${experience_level ? `**Experience Level:** ${experience_level}` : ""}
${living_situation ? `**Living Situation:** ${living_situation}` : ""}
${goals ? `**Goals:** ${goals}` : ""}

Please provide a comprehensive beginner's guide including:
1. Best starter plants for my situation using the plant care database
2. Essential supplies and tools I'll need from the product catalog
3. Basic care routines and schedules
4. Common mistakes to avoid
5. How to recognize and address problems early
6. Seasonal care considerations

Make this practical and encouraging for a beginner!`,
        },
      },
    ];

    return {
      description: "Complete beginner's guide to successful plant parenting",
      messages,
    };
  },
};
