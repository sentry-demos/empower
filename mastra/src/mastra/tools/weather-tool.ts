import { createTool } from '@mastra/core/tools';
import { z } from 'zod';
import { mastraLogger } from '../logger';
import { initializeWgsrpdZones, getWgsrpdZone } from '../utils/wgsrpd-zones';

interface GeocodingResponse {
  results: {
    latitude: number;
    longitude: number;
    name: string;
  }[];
}
interface WeatherResponse {
  current: {
    time: string;
    temperature_2m: number;
    apparent_temperature: number;
    relative_humidity_2m: number;
    wind_speed_10m: number;
    wind_gusts_10m: number;
    weather_code: number;
  };
}

export const weatherTool = createTool({
  id: 'get-weather',
  description: 'Get current weather for a location',
  inputSchema: z.object({
    location: z.string().describe('City name'),
  }),
  outputSchema: z.object({
    temperature: z.number(),
    feelsLike: z.number(),
    humidity: z.number(),
    windSpeed: z.number(),
    windGust: z.number(),
    conditions: z.string(),
    location: z.string(),
    coordinates: z.object({
      latitude: z.number(),
      longitude: z.number()
    }),
    wgsrpdZone: z.object({
      tdwgCode: z.string(),
      name: z.string(),
      level: z.number(),
      trefleSlug: z.string().optional()
    }).optional()
  }),
  execute: async ({ context }) => {
    mastraLogger.info('Weather tool starting execution', { location: context.location });
    try {
      const result = await getWeather(context.location);
      mastraLogger.info('Weather tool completed successfully', {
        location: result.location,
        temperature: result.temperature,
        conditions: result.conditions
      });
      return result;
    } catch (error) {
      mastraLogger.error('Weather tool execution failed', {
        location: context.location,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  },
});

const getWeather = async (location: string) => {
  mastraLogger.info('Starting geocoding lookup', { location });

  // Initialize WGSRPD zones if not already done
  await initializeWgsrpdZones();

  const geocodingUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(location)}&count=1`;
  const geocodingResponse = await fetch(geocodingUrl);
  const geocodingData = (await geocodingResponse.json()) as GeocodingResponse;

  if (!geocodingData.results?.[0]) {
    mastraLogger.warn('Location not found in geocoding', { location });
    throw new Error(`Location '${location}' not found`);
  }

  const { latitude, longitude, name } = geocodingData.results[0];
  mastraLogger.info('Geocoding successful', {
    originalLocation: location,
    resolvedName: name,
    coordinates: { latitude, longitude }
  });

  // Look up WGSRPD zone
  const wgsrpdZone = getWgsrpdZone(latitude, longitude);
  if (wgsrpdZone) {
    mastraLogger.info('WGSRPD zone identified', wgsrpdZone);
  }

  const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_gusts_10m,weather_code`;

  mastraLogger.info('Fetching weather data', { coordinates: { latitude, longitude } });
  const response = await fetch(weatherUrl);

  if (!response.ok) {
    mastraLogger.error('Weather API request failed', {
      status: response.status,
      statusText: response.statusText,
      coordinates: { latitude, longitude }
    });
    throw new Error(`Weather API request failed: ${response.status} ${response.statusText}`);
  }

  const data = (await response.json()) as WeatherResponse;
  mastraLogger.info('Weather data retrieved successfully', {
    location: name,
    temperature: data.current.temperature_2m,
    weatherCode: data.current.weather_code
  });

  return {
    temperature: data.current.temperature_2m,
    feelsLike: data.current.apparent_temperature,
    humidity: data.current.relative_humidity_2m,
    windSpeed: data.current.wind_speed_10m,
    windGust: data.current.wind_gusts_10m,
    conditions: getWeatherCondition(data.current.weather_code),
    location: name,
    coordinates: { latitude, longitude },
    wgsrpdZone: wgsrpdZone || undefined
  };
};

function getWeatherCondition(code: number): string {
  const conditions: Record<number, string> = {
    0: 'Clear sky',
    1: 'Mainly clear',
    2: 'Partly cloudy',
    3: 'Overcast',
    45: 'Foggy',
    48: 'Depositing rime fog',
    51: 'Light drizzle',
    53: 'Moderate drizzle',
    55: 'Dense drizzle',
    56: 'Light freezing drizzle',
    57: 'Dense freezing drizzle',
    61: 'Slight rain',
    63: 'Moderate rain',
    65: 'Heavy rain',
    66: 'Light freezing rain',
    67: 'Heavy freezing rain',
    71: 'Slight snow fall',
    73: 'Moderate snow fall',
    75: 'Heavy snow fall',
    77: 'Snow grains',
    80: 'Slight rain showers',
    81: 'Moderate rain showers',
    82: 'Violent rain showers',
    85: 'Slight snow showers',
    86: 'Heavy snow showers',
    95: 'Thunderstorm',
    96: 'Thunderstorm with slight hail',
    99: 'Thunderstorm with heavy hail',
  };
  return conditions[code] || 'Unknown';
}
