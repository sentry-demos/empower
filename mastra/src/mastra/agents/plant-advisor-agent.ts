import { openai } from '@ai-sdk/openai';
import { Agent } from '@mastra/core/agent';
import { Memory } from '@mastra/memory';
import { LibSQLStore } from '@mastra/libsql';
import { weatherTool } from '../tools/weather-tool';
import { trefleSearchTool, trefleDetailTool, trefleZonePlantsTool } from '../tools/trefle-tool';
import { z } from 'zod';
import { mastraLogger } from '../logger';
import { initializeWgsrpdZones, getWgsrpdZone } from '../utils/wgsrpd-zones';

// Schemas for structured input/output
export const UserConstraintsSchema = z.object({
  location: z.string().describe('City name or location'),
  environment: z.enum(['indoor', 'outdoor']).describe('Where the plants will be placed'),
  sunlight: z.enum(['low', 'medium', 'high']).describe('Available sunlight level'),
  pets: z.boolean().describe('Whether pets are present (affects plant toxicity recommendations)'),
  maintenancePreference: z.enum(['low', 'medium', 'high']).describe('Desired maintenance level'),
  preferences: z.string().optional().describe('Additional preferences like fragrance, flowering, edible, budget')
});

export const PlantRecommendationSchema = z.object({
  name: z.string().describe('Plant name'),
  why: z.string().describe('Why this plant fits the user\'s needs'),
  care: z.object({
    light: z.string().describe('Light requirements'),
    water: z.string().describe('Watering schedule and tips'),
    humidity: z.string().describe('Humidity requirements'),
    fertilizing: z.string().describe('Fertilizing schedule'),
    repotting: z.string().describe('Repotting frequency')
  }),
  toxicity: z.string().describe('Pet safety information'),
  difficulty: z.enum(['beginner', 'intermediate', 'advanced']).describe('Care difficulty level'),
  estPriceRange: z.string().describe('Estimated price range')
});

export const WeatherSummarySchema = z.object({
  temperature: z.number(),
  humidity: z.number(),
  conditions: z.string(),
  location: z.string(),
  tempBand: z.enum(['cool', 'temperate', 'warm']).describe('Temperature category'),
  humidityBand: z.enum(['low', 'medium', 'high']).describe('Humidity category'),
  wgsrpdZone: z.object({
    tdwgCode: z.string(),
    name: z.string(),
    level: z.number(),
    trefleSlug: z.string().optional()
  }).optional().describe('WGSRPD biogeographic zone')
});

export const PlantAdvisorResultSchema = z.object({
  weatherSummary: WeatherSummarySchema,
  topPlants: z.array(PlantRecommendationSchema).min(3).max(8),
  shoppingList: z.object({
    potSize: z.string(),
    soilType: z.string(),
    additionalItems: z.array(z.string())
  }).optional(),
  notes: z.string().optional().describe('Additional guidance or disclaimers')
});

// Helper function to derive climate profile from weather data
export const deriveClimateProfile = (weather: any) => {
  mastraLogger.info('Deriving climate profile from weather data', {
    temperature: weather.temperature,
    humidity: weather.humidity
  });

  const tempBand = weather.temperature < 18 ? 'cool' :
                   weather.temperature <= 24 ? 'temperate' : 'warm';

  const humidityBand = weather.humidity < 40 ? 'low' :
                       weather.humidity <= 60 ? 'medium' : 'high';

  const profile = {
    ...weather,
    tempBand,
    humidityBand
  };

  mastraLogger.info('Climate profile derived', profile);
  return profile;
};

export const plantAdvisorAgent = new Agent({
  name: 'Plant Advisor Agent',
  instructions: `
You are an expert horticulturist and plant care specialist with access to the Trefle plant database.

**SIMPLE APPROACH:**
When user provides location + indoor/outdoor:
1. IMMEDIATELY call weatherTool
2. IMMEDIATELY call trefle tools
3. Provide recommendations
4. Be conversational but ACTION FIRST, talk second

**SCOPE CLARIFICATION:**
You ONLY provide plant recommendations. If users ask for:
- General care tips: "I specialize in plant recommendations! Just tell me your location and whether you want indoor or outdoor plants, and I'll find great options for you."
- Plant identification: "I focus on recommending plants for your specific needs. Share your location and indoor/outdoor preference, and I'll suggest perfect plants for your space!"
- Other plant services: "My specialty is finding the perfect plants for your situation. Just need your location and indoor/outdoor - then I can recommend ideal plants for you!"

Always redirect to gathering the minimum requirements: location and environment (indoor/outdoor). Use smart defaults for everything else.

**INITIAL GREETING:**
When first contacted, use this exact greeting:
"🌿 Hello! I'm your plant recommendation specialist. I help you find the perfect plants for your specific space and lifestyle.

Just tell me your location and whether you want indoor or outdoor plants, and I'll get started finding great options for you!"

**FLEXIBLE INFORMATION GATHERING:**
Work with whatever information the user provides initially. If they give you location + indoor/outdoor, START THE RECOMMENDATION PROCESS immediately.

Required minimum:
• 📍 Location (city/region)
• 🏠 Environment (indoor or outdoor)

Use smart defaults for missing information:
• ☀️ Sunlight: Assume "medium" for indoor, "high" for outdoor
• 🐕 Pets: Assume "no pets" unless mentioned
• 🛠️ Maintenance: Assume "low" unless specified
• 💭 Preferences: Use general popular plants unless specified

**WORKFLOW:**
User says "New York, indoors" → You IMMEDIATELY:
1. Call weatherTool({ location: "New York" })
2. Call trefleZonePlantsTool with zone from weather result
3. Call trefleSearchTool({ query: "indoor plants" })
4. Call trefleDetailTool for 3-5 promising plants
5. Return complete PlantAdvisorResultSchema

Keep conversation minimal until you have the data.

**TOOLS:**
- weatherTool: Get climate data
- trefleZonePlantsTool: Get zone plants
- trefleSearchTool: Search plants
- trefleDetailTool: Get plant details

Valid zone slugs: "78", "76", "ala", "ask", "2", "34"

**CRITICAL: CALL TOOLS IMMEDIATELY. NO PRELIMINARY CHAT.**

Return PlantAdvisorResultSchema with actual tool data.

**Tools available:**
- weatherTool: Get weather and location data
- trefleSearchTool: Search plant species by name
- trefleDetailTool: Get detailed plant information by slug
- trefleZonePlantsTool: Get plants native/introduced to a biogeographic zone

Prioritize data-driven recommendations using Trefle while maintaining practical, safe advice.
`,
  model: openai('gpt-4o-mini'),
  tools: {
    weatherTool,
    trefleSearchTool,
    trefleDetailTool,
    trefleZonePlantsTool
  },
  memory: new Memory({
    storage: new LibSQLStore({
      url: 'file:../mastra.db', // path is relative to the .mastra/output directory
    }),
  }),
});

// Note: For now, logging is handled in the agent instructions and tool implementations
// Future enhancement: Add execution interceptors when Mastra supports them
