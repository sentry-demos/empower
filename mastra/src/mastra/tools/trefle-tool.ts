import { createTool } from '@mastra/core/tools';
import { z } from 'zod';
import { mastraLogger } from '../logger';

// Trefle API response interfaces
interface TrefleSpeciesSearchResponse {
  data: Array<{
    id: number;
    common_name: string | null;
    slug: string;
    scientific_name: string;
    image_url: string | null;
    family_common_name: string | null;
  }>;
  meta: {
    total: number;
  };
}

interface TrefleSpeciesDetailResponse {
  data: {
    id: number;
    common_name: string | null;
    slug: string;
    scientific_name: string;
    image_url: string | null;
    family_common_name: string | null;
    edible: boolean | null;
    growth: {
      habit: string | null;
      growth_form: string | null;
      growth_rate: string | null;
    } | null;
    specifications: {
      toxicity: string | null;
      growth_period: string | null;
    } | null;
    distributions: {
      native: string[];
      introduced: string[];
    } | null;
  };
}

interface TrefleDistributionsResponse {
  data: Array<{
    id: string;
    name: string;
    slug: string;
    tdwg_code: string;
    tdwg_level: number;
  }>;
}

interface TrefleDistributionPlantsResponse {
  data: Array<{
    id: number;
    common_name: string | null;
    slug: string;
    scientific_name: string;
    image_url: string | null;
  }>;
}

const TREFLE_BASE_URL = 'https://trefle.io/api/v1';

async function makeTrefleRequest(endpoint: string): Promise<any> {
  const token = process.env.TREFLE_TOKEN || 'Z5tH-dVywswd7M5NCJ0jnO7gnGhTuvTLjjt7OTi9bqU';
  if (!token) {
    throw new Error('TREFLE_TOKEN environment variable is required');
  }

  const url = `${TREFLE_BASE_URL}${endpoint}${endpoint.includes('?') ? '&' : '?'}token=${token}`;

  mastraLogger.info('Making Trefle API request', { endpoint });

  const response = await fetch(url);

  if (!response.ok) {
    mastraLogger.error('Trefle API request failed', {
      endpoint,
      status: response.status,
      statusText: response.statusText,
      rateLimit: response.headers.get('X-RateLimit-Remaining'),
      rateLimitReset: response.headers.get('X-RateLimit-Reset')
    });
    throw new Error(`Trefle API request failed: ${response.status} ${response.statusText}`);
  }

  // Log rate limit info
  const rateLimitRemaining = response.headers.get('X-RateLimit-Remaining');
  const rateLimitReset = response.headers.get('X-RateLimit-Reset');

  mastraLogger.info('Trefle API request successful', {
    endpoint,
    rateLimitRemaining: rateLimitRemaining ? parseInt(rateLimitRemaining) : null,
    rateLimitReset: rateLimitReset ? new Date(parseInt(rateLimitReset) * 1000).toISOString() : null
  });

  return await response.json();
}

// Tool to search for plant species
export const trefleSearchTool = createTool({
  id: 'trefle-search-plants',
  description: 'Search for plant species in the Trefle database',
  inputSchema: z.object({
    query: z.string().describe('Plant name to search for'),
    limit: z.number().optional().default(5).describe('Number of results to return (max 20)')
  }),
  outputSchema: z.object({
    plants: z.array(z.object({
      id: z.number(),
      commonName: z.string().nullable(),
      slug: z.string(),
      scientificName: z.string(),
      imageUrl: z.string().nullable(),
      familyCommonName: z.string().nullable()
    })),
    total: z.number()
  }),
  execute: async ({ context }) => {
    const { query, limit } = context;

    mastraLogger.info('Searching Trefle for plants', { query, limit });

    try {
      const response = await makeTrefleRequest(
        `/species/search?q=${encodeURIComponent(query)}&limit=${Math.min(limit, 20)}`
      ) as TrefleSpeciesSearchResponse;

      const plants = response.data.map(plant => ({
        id: plant.id,
        commonName: plant.common_name,
        slug: plant.slug,
        scientificName: plant.scientific_name,
        imageUrl: plant.image_url,
        familyCommonName: plant.family_common_name
      }));

      mastraLogger.info('Trefle search completed', {
        query,
        resultsFound: plants.length,
        totalAvailable: response.meta.total
      });

      return {
        plants,
        total: response.meta.total
      };
    } catch (error) {
      mastraLogger.error('Trefle search failed', {
        query,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }
});

// Tool to get detailed plant information
export const trefleDetailTool = createTool({
  id: 'trefle-plant-details',
  description: 'Get detailed information about a specific plant species',
  inputSchema: z.object({
    slug: z.string().describe('Plant slug from search results')
  }),
  outputSchema: z.object({
    id: z.number(),
    commonName: z.string().nullable(),
    slug: z.string(),
    scientificName: z.string(),
    imageUrl: z.string().nullable(),
    familyCommonName: z.string().nullable(),
    edible: z.boolean().nullable(),
    growth: z.object({
      habit: z.string().nullable(),
      growthForm: z.string().nullable(),
      growthRate: z.string().nullable()
    }).nullable(),
    specifications: z.object({
      toxicity: z.string().nullable(),
      growthPeriod: z.string().nullable()
    }).nullable(),
    distributions: z.object({
      native: z.array(z.string()),
      introduced: z.array(z.string())
    }).nullable()
  }),
  execute: async ({ context }) => {
    const { slug } = context;

    mastraLogger.info('Fetching Trefle plant details', { slug });

    try {
      const response = await makeTrefleRequest(`/species/${slug}`) as TrefleSpeciesDetailResponse;
      const plant = response.data;

      const result = {
        id: plant.id,
        commonName: plant.common_name,
        slug: plant.slug,
        scientificName: plant.scientific_name,
        imageUrl: plant.image_url,
        familyCommonName: plant.family_common_name,
        edible: plant.edible,
        growth: plant.growth ? {
          habit: plant.growth.habit,
          growthForm: plant.growth.growth_form,
          growthRate: plant.growth.growth_rate
        } : null,
        specifications: plant.specifications ? {
          toxicity: plant.specifications.toxicity,
          growthPeriod: plant.specifications.growth_period
        } : null,
        distributions: plant.distributions ? {
          native: plant.distributions.native || [],
          introduced: plant.distributions.introduced || []
        } : null
      };

      mastraLogger.info('Trefle plant details retrieved', {
        slug,
        hasImage: !!result.imageUrl,
        isEdible: result.edible,
        hasGrowthInfo: !!result.growth,
        nativeRegions: result.distributions?.native?.length || 0
      });

      return result;
    } catch (error) {
      mastraLogger.error('Trefle plant details fetch failed', {
        slug,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }
});

// Tool to get all distribution zones (for initialization)
export const trefleDistributionsTool = createTool({
  id: 'trefle-distributions',
  description: 'Get list of all distribution zones from Trefle',
  inputSchema: z.object({
    limit: z.number().optional().default(20).describe('Number of distributions to return')
  }),
  outputSchema: z.object({
    distributions: z.array(z.object({
      id: z.string(),
      name: z.string(),
      slug: z.string(),
      tdwgCode: z.string(),
      tdwgLevel: z.number()
    }))
  }),
  execute: async ({ context }) => {
    const { limit } = context;

    mastraLogger.info('Fetching Trefle distributions', { limit });

    try {
      const response = await makeTrefleRequest(
        `/distributions?limit=${limit}`
      ) as TrefleDistributionsResponse;

      const distributions = response.data.map(dist => ({
        id: dist.id,
        name: dist.name,
        slug: dist.slug,
        tdwgCode: dist.tdwg_code,
        tdwgLevel: dist.tdwg_level
      }));

      mastraLogger.info('Trefle distributions retrieved', {
        count: distributions.length
      });

      return { distributions };
    } catch (error) {
      mastraLogger.error('Trefle distributions fetch failed', {
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }
});

// Tool to get plants by distribution zone
// Valid zone slugs - only these are allowed
const VALID_ZONE_SLUGS = ['78', '76', '70', 'ala', 'ask', 'cal', 'tex', 'fla', '2', '34'];

export const trefleZonePlantsTool = createTool({
  id: 'trefle-zone-plants',
  description: 'Get plants native or introduced to a specific distribution zone. Valid zones: 78 (SE USA), 76 (SW USA), 70 (Subarctic America), ala (Alabama), ask (Alaska), cal (California), tex (Texas), fla (Florida), 2 (Africa), 34 (W Asia)',
  inputSchema: z.object({
    zoneSlug: z.enum(['78', '76', '70', 'ala', 'ask', 'cal', 'tex', 'fla', '2', '34']).describe('Distribution zone slug - must be one of: 78, 76, 70, ala, ask, cal, tex, fla, 2, 34'),
    establishment: z.enum(['native', 'introduced']).optional().describe('Filter by establishment type'),
    limit: z.number().optional().default(5).describe('Number of plants to return')
  }),
  outputSchema: z.object({
    plants: z.array(z.object({
      id: z.number(),
      commonName: z.string().nullable(),
      slug: z.string(),
      scientificName: z.string(),
      imageUrl: z.string().nullable()
    }))
  }),
    execute: async ({ context }) => {
    const { zoneSlug, establishment, limit } = context;

    // Validate zone slug
    if (!VALID_ZONE_SLUGS.includes(zoneSlug)) {
      const error = `Invalid zone slug "${zoneSlug}". Must be one of: ${VALID_ZONE_SLUGS.join(', ')}`;
      mastraLogger.error('Invalid zone slug provided', { zoneSlug, validSlugs: VALID_ZONE_SLUGS });
      throw new Error(error);
    }

    mastraLogger.info('Fetching plants for zone', { zoneSlug, establishment, limit });

    try {
      let endpoint = `/distributions/${zoneSlug}/plants?limit=${limit}`;
      if (establishment) {
        endpoint += `&filter[establishment]=${establishment}`;
      }

      const response = await makeTrefleRequest(endpoint) as TrefleDistributionPlantsResponse;

      const plants = response.data.map(plant => ({
        id: plant.id,
        commonName: plant.common_name,
        slug: plant.slug,
        scientificName: plant.scientific_name,
        imageUrl: plant.image_url
      }));

      mastraLogger.info('Zone plants retrieved', {
        zoneSlug,
        establishment,
        plantsFound: plants.length
      });

      return { plants };
    } catch (error) {
      mastraLogger.error('Zone plants fetch failed', {
        zoneSlug,
        establishment,
        error: error instanceof Error ? error.message : String(error)
      });
      throw error;
    }
  }
});
