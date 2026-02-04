import { ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { randomDelay } from "../utils.js";

function getSeasonalCalendar(season: string, region: string) {
  const calendars: Record<string, Record<string, any>> = {
    spring: {
      temperate: {
        season: "Spring",
        region: "Temperate",
        months: ["March", "April", "May"],
        activities: {
          march: [
            "Begin increasing watering frequency as plants wake up",
            "Start fertilizing houseplants monthly",
            "Repot plants that have outgrown containers",
            "Increase humidity as heating systems are used less",
          ],
          april: [
            "Move plants closer to windows for increased light",
            "Begin propagation projects",
            "Check for pests emerging with warmer weather",
            "Gradually acclimate plants to outdoor conditions",
          ],
          may: [
            "Transition plants outdoors gradually",
            "Increase watering frequency",
            "Prune and shape plants for growing season",
            "Start regular pest monitoring",
          ],
        },
        generalTips: [
          "Spring is the best time for repotting and propagation",
          "Gradually increase watering and fertilizing",
          "Watch for new growth and adjust care accordingly",
        ],
      },
      tropical: {
        season: "Spring",
        region: "Tropical",
        months: ["March", "April", "May"],
        activities: {
          march: [
            "Maintain consistent watering schedule",
            "Monitor for increased pest activity",
            "Continue regular fertilizing",
            "Ensure good air circulation",
          ],
          april: [
            "Peak growing season - increase fertilizer frequency",
            "Propagate rapidly growing plants",
            "Prune overgrown plants",
            "Monitor soil moisture more frequently",
          ],
          may: [
            "Continue intensive care routine",
            "Watch for heat stress in sensitive plants",
            "Maintain high humidity levels",
            "Consider shade protection for outdoor plants",
          ],
        },
        generalTips: [
          "Growing season is year-round in tropical climates",
          "Focus on consistent moisture and humidity",
          "Heat stress can be an issue even in spring",
        ],
      },
    },
    summer: {
      temperate: {
        season: "Summer",
        region: "Temperate",
        months: ["June", "July", "August"],
        activities: {
          june: [
            "Increase watering frequency significantly",
            "Provide shade for plants in direct sun",
            "Continue monthly fertilizing",
            "Monitor for spider mites in dry conditions",
          ],
          july: [
            "Peak watering season - daily for some plants",
            "Provide maximum humidity",
            "Deadhead flowers to encourage growth",
            "Move sensitive plants to shadier locations",
          ],
          august: [
            "Continue intensive watering",
            "Watch for heat stress",
            "Begin preparing for fall transition",
            "Last chance for major propagation projects",
          ],
        },
        generalTips: [
          "Heat and drought stress are primary concerns",
          "Consistent watering is crucial",
          "Provide shade during hottest parts of day",
        ],
      },
    },
    fall: {
      temperate: {
        season: "Fall",
        region: "Temperate",
        months: ["September", "October", "November"],
        activities: {
          september: [
            "Begin reducing watering frequency",
            "Stop fertilizing most plants",
            "Bring outdoor plants inside gradually",
            "Check for pests before bringing plants indoors",
          ],
          october: [
            "Reduce watering as growth slows",
            "Clean leaves to maximize light absorption",
            "Prepare grow lights for shorter days",
            "Final pest treatments before winter",
          ],
          november: [
            "Minimal watering for most plants",
            "Increase humidity as heating starts",
            "Remove dead or dying foliage",
            "Group plants together for better humidity",
          ],
        },
        generalTips: [
          "Transition period requires careful observation",
          "Reduce care intensity as plants enter dormancy",
          "Prepare for lower light and humidity conditions",
        ],
      },
    },
    winter: {
      temperate: {
        season: "Winter",
        region: "Temperate",
        months: ["December", "January", "February"],
        activities: {
          december: [
            "Water sparingly - only when soil is dry",
            "Maximize available light",
            "Maintain humidity with humidifiers",
            "Avoid fertilizing dormant plants",
          ],
          january: [
            "Minimal watering and care",
            "Monitor for dry air damage",
            "Keep plants away from heating vents",
            "Plan for spring repotting and propagation",
          ],
          february: [
            "Begin watching for signs of new growth",
            "Slightly increase watering if growth appears",
            "Prepare for spring care routine",
            "Order supplies for growing season",
          ],
        },
        generalTips: [
          "Dormancy period requires minimal intervention",
          "Focus on preventing stress rather than promoting growth",
          "Prepare for spring growing season",
        ],
      },
    },
  };

  const seasonData = calendars[season.toLowerCase()];
  if (!seasonData) {
    return {
      error: "Season not found",
      availableSeasons: Object.keys(calendars),
    };
  }

  const regionData = seasonData[region.toLowerCase()];
  if (!regionData) {
    return {
      error: "Region not found for this season",
      availableRegions: Object.keys(seasonData),
    };
  }

  return regionData;
}

export const seasonalCalendarResource = {
  template: new ResourceTemplate("empower://seasonal-calendar", {
    list: async () => ({
      resources: [
        { uri: "empower://seasonal-calendar", name: "Seasonal Plant Calendar" },
      ],
    }),
  }),
  metadata: {
    title: "Seasonal Plant Calendar",
    description:
      "Seasonal care calendar showing what plant care activities should be done each month",
    annotations: {
      audience: ["user"],
      priority: 0.8,
    },
  },
  handler: async (uri: { href: string }) => {
    await randomDelay(50, 200);

    // Default to spring temperate calendar
    const calendarData = getSeasonalCalendar("spring", "temperate");
    return {
      contents: [
        {
          uri: uri.href,
          text: JSON.stringify(calendarData, null, 2),
        },
      ],
    };
  },
};
