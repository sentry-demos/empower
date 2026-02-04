import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { randomDelay } from "../utils.js";

function getPlantDiagnosticData(symptom: string) {
  const diagnostics: Record<string, any> = {
    "yellow-leaves": {
      symptom: "Yellow Leaves",
      commonCauses: [
        {
          cause: "Overwatering",
          probability: "High",
          description: "Most common cause of yellowing leaves",
          signs: [
            "Soft, mushy stems",
            "Soil that stays wet for days",
            "Fungal smell from soil",
            "Multiple leaves yellowing at once",
          ],
          treatment: [
            "Stop watering immediately",
            "Check for root rot",
            "Improve drainage",
            "Remove affected leaves",
            "Repot if roots are black/mushy",
          ],
        },
        {
          cause: "Natural aging",
          probability: "Medium",
          description: "Older leaves naturally yellow and drop",
          signs: [
            "Only bottom/older leaves affected",
            "Gradual, slow process",
            "Plant otherwise healthy",
            "New growth looks normal",
          ],
          treatment: [
            "Simply remove yellow leaves",
            "Continue normal care routine",
            "This is completely normal",
          ],
        },
        {
          cause: "Nutrient deficiency",
          probability: "Medium",
          description: "Lack of nitrogen or other nutrients",
          signs: [
            "Yellowing starts with older leaves",
            "Slow growth",
            "Small new leaves",
            "Overall pale appearance",
          ],
          treatment: [
            "Apply balanced fertilizer",
            "Check soil pH",
            "Consider repotting with fresh soil",
            "Increase fertilizing frequency during growing season",
          ],
        },
        {
          cause: "Underwatering",
          probability: "Low",
          description: "Severe water stress",
          signs: [
            "Dry, crispy leaf edges",
            "Soil pulls away from pot edges",
            "Leaves feel dry and brittle",
            "Wilting before yellowing",
          ],
          treatment: [
            "Water thoroughly",
            "Check watering schedule",
            "Ensure proper drainage",
            "Monitor soil moisture regularly",
          ],
        },
      ],
      preventionTips: [
        "Check soil moisture before watering",
        "Ensure pots have drainage holes",
        "Use well-draining soil mix",
        "Maintain consistent watering schedule",
        "Remove old leaves regularly",
      ],
    },
    "brown-spots": {
      symptom: "Brown Spots on Leaves",
      commonCauses: [
        {
          cause: "Fungal infection",
          probability: "High",
          description: "Bacterial or fungal leaf spot disease",
          signs: [
            "Dark brown or black spots",
            "Spots have yellow halos",
            "Spots spread over time",
            "High humidity conditions",
          ],
          treatment: [
            "Remove affected leaves immediately",
            "Improve air circulation",
            "Reduce humidity",
            "Apply fungicide if severe",
            "Avoid getting leaves wet when watering",
          ],
        },
        {
          cause: "Sunburn",
          probability: "Medium",
          description: "Direct sunlight damage",
          signs: [
            "Brown, crispy patches",
            "Spots on sun-facing side",
            "Recent move to brighter location",
            "Dry, papery texture",
          ],
          treatment: [
            "Move to less direct light",
            "Gradually acclimate to bright light",
            "Remove severely damaged leaves",
            "Provide filtered light instead",
          ],
        },
        {
          cause: "Water on leaves",
          probability: "Medium",
          description: "Water droplets acting as magnifying glasses",
          signs: [
            "Round brown spots",
            "Spots where water droplets sat",
            "Occurs after misting or watering",
            "Pattern matches water drops",
          ],
          treatment: [
            "Water soil directly, not leaves",
            "Improve ventilation",
            "Water in morning so leaves dry quickly",
            "Remove damaged leaves",
          ],
        },
      ],
      preventionTips: [
        "Water at soil level, not on leaves",
        "Ensure good air circulation",
        "Gradually introduce plants to bright light",
        "Maintain proper humidity levels",
        "Quarantine new plants",
      ],
    },
    wilting: {
      symptom: "Wilting/Drooping Leaves",
      commonCauses: [
        {
          cause: "Underwatering",
          probability: "High",
          description: "Plant needs more water",
          signs: [
            "Dry soil",
            "Leaves feel limp but not mushy",
            "Soil pulls away from pot",
            "Quick recovery after watering",
          ],
          treatment: [
            "Water thoroughly until water drains out",
            "Check watering schedule",
            "Consider larger pot if rootbound",
            "Monitor soil moisture more closely",
          ],
        },
        {
          cause: "Root rot from overwatering",
          probability: "Medium",
          description: "Roots damaged and can't take up water",
          signs: [
            "Wet soil but wilting plant",
            "Black, mushy roots",
            "Foul smell from soil",
            "No improvement after watering",
          ],
          treatment: [
            "Stop watering immediately",
            "Remove from pot and inspect roots",
            "Cut away black/mushy roots",
            "Repot in fresh, well-draining soil",
            "Reduce watering frequency",
          ],
        },
        {
          cause: "Heat stress",
          probability: "Medium",
          description: "Temperature too high",
          signs: [
            "Wilting during hottest part of day",
            "Recovery in evening/morning",
            "Recent temperature increase",
            "Leaves may curl inward",
          ],
          treatment: [
            "Move to cooler location",
            "Increase humidity around plant",
            "Provide shade during peak sun",
            "Ensure adequate water",
          ],
        },
      ],
      preventionTips: [
        "Maintain consistent watering schedule",
        "Use well-draining soil",
        "Monitor temperature changes",
        "Check root health during repotting",
        "Avoid sudden environmental changes",
      ],
    },
    "brown-tips": {
      symptom: "Brown Leaf Tips",
      commonCauses: [
        {
          cause: "Low humidity",
          probability: "High",
          description: "Air too dry for plant's needs",
          signs: [
            "Just tips turn brown",
            "Crispy, dry texture",
            "More common in winter",
            "Affects many leaves",
          ],
          treatment: [
            "Increase humidity with humidifier",
            "Group plants together",
            "Use pebble trays with water",
            "Mist air around plant (not leaves)",
          ],
        },
        {
          cause: "Overfertilization",
          probability: "Medium",
          description: "Salt buildup from too much fertilizer",
          signs: [
            "Brown, burned-looking tips",
            "White crust on soil surface",
            "Recent fertilizing",
            "Affects new growth first",
          ],
          treatment: [
            "Flush soil with plain water",
            "Reduce fertilizer concentration",
            "Skip next few fertilizing sessions",
            "Repot if salt buildup is severe",
          ],
        },
        {
          cause: "Fluoride/chlorine in water",
          probability: "Medium",
          description: "Sensitive plants react to tap water chemicals",
          signs: [
            "Gradual browning of tips",
            "Affects sensitive plants most",
            "Using tap water",
            "Pattern consistent across plant",
          ],
          treatment: [
            "Use filtered or distilled water",
            "Let tap water sit 24 hours before using",
            "Collect rainwater when possible",
            "Trim affected tips",
          ],
        },
      ],
      preventionTips: [
        "Maintain 40-60% humidity",
        "Use filtered water when possible",
        "Fertilize at half strength",
        "Monitor humidity with hygrometer",
        "Avoid over-fertilizing",
      ],
    },
  };

  return (
    diagnostics[symptom] || {
      error: "Symptom not found",
      availableSymptoms: Object.keys(diagnostics),
      suggestion:
        "Try searching for: yellow-leaves, brown-spots, wilting, or brown-tips",
    }
  );
}

export const plantDiagnosticsResource = {
  template: new ResourceTemplate("empower://plant-diagnostics", {
    list: async () => ({
      resources: [
        {
          uri: "empower://plant-diagnostics",
          name: "Plant Problem Diagnostics",
        },
      ],
    }),
  }),
  metadata: {
    title: "Plant Problem Diagnostics",
    description:
      "Detailed diagnostic information for common plant problems including causes, treatments, and prevention tips",
  },
  handler: async (uri: { href: string }) => {
    await randomDelay(100, 300);

    // Default to yellowing leaves diagnosis
    const diagnosticData = getPlantDiagnosticData("yellowing");
    return {
      contents: [
        {
          uri: uri.href,
          text: JSON.stringify(diagnosticData, null, 2),
        },
      ],
    };
  },
};
