import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { randomDelay } from "../utils.js";

function getAllSymptoms() {
  return {
    availableSymptoms: [
      {
        key: "yellow-leaves",
        name: "Yellow Leaves",
        description: "Leaves turning yellow, common issue with multiple causes",
      },
      {
        key: "brown-spots",
        name: "Brown Spots",
        description: "Dark spots appearing on leaf surfaces",
      },
      {
        key: "wilting",
        name: "Wilting/Drooping",
        description: "Leaves becoming limp and drooping down",
      },
      {
        key: "brown-tips",
        name: "Brown Leaf Tips",
        description: "Tips of leaves turning brown and crispy",
      },
    ],
    usage:
      "Use empower://problems/{symptom} to get detailed diagnostic information",
    examples: [
      "empower://problems/yellow-leaves",
      "empower://problems/brown-spots",
      "empower://problems/wilting",
      "empower://problems/brown-tips",
    ],
  };
}

export const plantSymptomsResource = {
  template: new ResourceTemplate("empower://plant-symptoms", {
    list: async () => ({
      resources: [
        { uri: "empower://plant-symptoms", name: "Plant Problems Directory" },
      ],
    }),
  }),
  metadata: {
    title: "Plant Problem Directory",
    description:
      "Directory of all available plant problem diagnostics and symptoms",
    annotations: {
      audience: ["user", "assistant"],
      priority: 0.6,
    },
  },
  handler: async (uri: { href: string }) => {
    await randomDelay(30, 100);

    const symptomsData = getAllSymptoms();
    return {
      contents: [
        {
          uri: uri.href,
          text: JSON.stringify(symptomsData, null, 2),
        },
      ],
    };
  },
};
