import { z } from "zod";
import { PlantCareGuide } from "../types.js";
import { randomDelay, maybeThrow } from "../utils.js";

export const getPlantCareGuideTool = {
  title: "Get Plant Care Guide",
  annotations: {
    description: "Get detailed care instructions for a specific plant",
  },
  inputSchema: {
    plantName: z.string().describe("Name of the plant to get care guide for"),
  },
  handler: async ({ plantName }: { plantName: string }) => {
    const careGuide = await generatePlantCareGuide(plantName);
    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(careGuide, null, 2),
        },
      ],
    };
  },
};

async function generatePlantCareGuide(
  plantName: string
): Promise<PlantCareGuide> {
  // Generate care guide based on plant name patterns
  const lowerName = plantName.toLowerCase();

  await randomDelay(500, 1000);
  maybeThrow(0.1, new Error("Empower Plant API unreachable"));

  // Default care guide template
  let careGuide: PlantCareGuide = {
    plantName: plantName,
    difficulty: "Moderate",
    sunlight: "Bright, indirect light",
    watering: {
      frequency: "Weekly",
      amount: "Water until it drains from bottom",
      tips: "Allow soil to dry between waterings",
    },
    soil: {
      type: "Well-draining potting mix",
      drainage: "Good drainage essential",
      ph: "6.0-7.0",
    },
    temperature: {
      ideal: "65-75°F (18-24°C)",
      minimum: "60°F (15°C)",
      maximum: "80°F (27°C)",
    },
    humidity: "40-60%",
    fertilizer: {
      type: "Balanced liquid fertilizer",
      frequency: "Monthly",
      season: "Spring and summer",
    },
    commonIssues: [
      {
        problem: "Yellow leaves",
        cause: "Overwatering or poor drainage",
        solution: "Reduce watering frequency and check soil drainage",
      },
      {
        problem: "Brown leaf tips",
        cause: "Low humidity or fluoride in water",
        solution: "Increase humidity and use filtered water",
      },
    ],
    propagation: "Stem cuttings in water or soil",
    toxicity: "Mildly toxic to pets",
  };

  // Customize based on plant type
  if (lowerName.includes("succulent") || lowerName.includes("cactus")) {
    careGuide.difficulty = "Easy";
    careGuide.sunlight = "Full sun to bright light";
    careGuide.watering = {
      frequency: "Every 2-3 weeks",
      amount: "Deep watering, then let dry completely",
      tips: "Less water in winter",
    };
    careGuide.soil = {
      type: "Cactus/succulent potting mix",
      drainage: "Excellent drainage required",
      ph: "6.1-7.8",
    };
    careGuide.humidity = "Low, 30-40%";
    careGuide.propagation = "Leaf or stem cuttings, offsets";
    careGuide.toxicity = "Generally safe";
  }

  if (lowerName.includes("fern")) {
    careGuide.difficulty = "Challenging";
    careGuide.sunlight = "Indirect light, no direct sun";
    careGuide.watering = {
      frequency: "2-3 times per week",
      amount: "Keep soil consistently moist",
      tips: "Never let soil dry out completely",
    };
    careGuide.humidity = "High, 50-80%";
    careGuide.propagation = "Division or spores";
    careGuide.toxicity = "Generally safe";
  }

  if (lowerName.includes("snake") || lowerName.includes("sansevieria")) {
    careGuide.difficulty = "Very Easy";
    careGuide.sunlight = "Low to bright light";
    careGuide.watering = {
      frequency: "Every 2-4 weeks",
      amount: "Water deeply, then let dry",
      tips: "Very drought tolerant",
    };
    careGuide.propagation = "Leaf cuttings or division";
    careGuide.toxicity = "Toxic to pets";
  }

  if (lowerName.includes("pothos") || lowerName.includes("philodendron")) {
    careGuide.difficulty = "Easy";
    careGuide.sunlight = "Low to bright, indirect light";
    careGuide.propagation = "Stem cuttings in water";
    careGuide.toxicity = "Toxic to pets";
    careGuide.commonIssues.push({
      problem: "Leggy growth",
      cause: "Insufficient light",
      solution: "Move to brighter location or trim regularly",
    });
  }

  if (lowerName.includes("fiddle") || lowerName.includes("fig")) {
    careGuide.difficulty = "Challenging";
    careGuide.sunlight = "Bright, indirect light";
    careGuide.watering = {
      frequency: "Weekly when top inch is dry",
      amount: "Water thoroughly",
      tips: "Consistent watering schedule important",
    };
    careGuide.commonIssues.push({
      problem: "Dropping leaves",
      cause: "Stress from changes in light, water, or location",
      solution: "Maintain consistent care routine",
    });
  }

  return careGuide;
}
