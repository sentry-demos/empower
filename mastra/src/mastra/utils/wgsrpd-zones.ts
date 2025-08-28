import { booleanPointInPolygon, point } from '@turf/turf';
import type { FeatureCollection, Polygon, MultiPolygon } from 'geojson';
import { mastraLogger } from '../logger';

// WGSRPD Zone interface
interface WgsrpdZone {
  tdwgCode: string;
  name: string;
  level: number;
  trefleSlug?: string;
}

interface TrefleDistribution {
  id: string;
  name: string;
  slug: string;
  tdwgCode: string;
  tdwgLevel: number;
}

// In-memory cache for zones and distributions
let tdwgZones: FeatureCollection<Polygon | MultiPolygon> | null = null;
let trefleIndexByCode: Map<string, TrefleDistribution> = new Map();
let isInitialized = false;

// Simplified WGSRPD zones for MVP (using real TDWG codes)
// In production, load from TDWG GitHub or local file
const SIMPLIFIED_WGSRPD_ZONES: FeatureCollection<Polygon | MultiPolygon> = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        tdwg_code: "78",
        name: "Southeastern U.S.A.",
        level: 2
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [-105, 25], [-105, 40], [-75, 40], [-75, 25], [-105, 25]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        tdwg_code: "ALA",
        name: "Alabama",
        level: 3
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [-88, 30], [-88, 35], [-84, 35], [-84, 30], [-88, 30]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        tdwg_code: "ASK",
        name: "Alaska",
        level: 3
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [-180, 54], [-180, 72], [-130, 72], [-130, 54], [-180, 54]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        tdwg_code: "76",
        name: "Southwestern U.S.A.",
        level: 2
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [-125, 30], [-125, 42], [-100, 42], [-100, 30], [-125, 30]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        tdwg_code: "2",
        name: "Africa",
        level: 1
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [-25, -40], [-25, 40], [55, 40], [55, -40], [-25, -40]
        ]]
      }
    },
    {
      type: "Feature",
      properties: {
        tdwg_code: "34",
        name: "Western Asia",
        level: 2
      },
      geometry: {
        type: "Polygon",
        coordinates: [[
          [25, 25], [25, 50], [70, 50], [70, 25], [25, 25]
        ]]
      }
    }
  ]
};

/**
 * Initialize the WGSRPD zone system
 * In production: fetch TDWG GeoJSON and Trefle distributions
 */
export async function initializeWgsrpdZones(): Promise<void> {
  if (isInitialized) {
    return;
  }

  mastraLogger.info('Initializing WGSRPD zones');

  try {
    // For MVP: use simplified zones
    tdwgZones = SIMPLIFIED_WGSRPD_ZONES;

    // In production, you would:
    // 1. Fetch TDWG GeoJSON from GitHub or load from local file
    // 2. Fetch Trefle distributions and build index

    // Real Trefle distributions mapping from API
    const realTrefleDistributions: TrefleDistribution[] = [
      { id: "606", name: "Southeastern U.S.A.", slug: "78", tdwgCode: "78", tdwgLevel: 2 },
      { id: "144", name: "Alabama", slug: "ala", tdwgCode: "ALA", tdwgLevel: 3 },
      { id: "325", name: "Alaska", slug: "ask", tdwgCode: "ASK", tdwgLevel: 3 },
      { id: "76", name: "Southwestern U.S.A.", slug: "76", tdwgCode: "76", tdwgLevel: 2 },
      { id: "407", name: "Africa", slug: "2", tdwgCode: "2", tdwgLevel: 1 },
      { id: "453", name: "Western Asia", slug: "34", tdwgCode: "34", tdwgLevel: 2 }
    ];

    // Build index by TDWG code
    trefleIndexByCode.clear();
    for (const dist of realTrefleDistributions) {
      trefleIndexByCode.set(dist.tdwgCode, dist);
    }

        isInitialized = true;
    mastraLogger.info('WGSRPD zones initialized', {
      zoneCount: tdwgZones.features.length,
      trefleDistributions: realTrefleDistributions.length
    });

  } catch (error) {
    mastraLogger.error('Failed to initialize WGSRPD zones', {
      error: error instanceof Error ? error.message : String(error)
    });
    throw error;
  }
}

/**
 * Find the WGSRPD zone containing a given point
 */
export function getWgsrpdZone(latitude: number, longitude: number): WgsrpdZone | null {
  if (!isInitialized || !tdwgZones) {
    mastraLogger.warn('WGSRPD zones not initialized, call initializeWgsrpdZones() first');
    return null;
  }

  mastraLogger.info('Looking up WGSRPD zone', { latitude, longitude });

  const queryPoint = point([longitude, latitude]);

  // Find the most specific zone (highest level) that contains the point
  let bestMatch: WgsrpdZone | null = null;
  let bestLevel = 0;

  for (const feature of tdwgZones.features) {
    try {
      if (booleanPointInPolygon(queryPoint, feature)) {
        const props = feature.properties as any;
        const level = props.level || 0;

        if (level >= bestLevel) {
          const trefleDistribution = trefleIndexByCode.get(props.tdwg_code);

          bestMatch = {
            tdwgCode: props.tdwg_code,
            name: props.name,
            level: level,
            trefleSlug: trefleDistribution?.slug
          };
          bestLevel = level;
        }
      }
    } catch (error) {
      mastraLogger.warn('Error checking zone polygon', {
        tdwgCode: feature.properties?.tdwg_code,
        error: error instanceof Error ? error.message : String(error)
      });
    }
  }

  if (bestMatch) {
    mastraLogger.info('WGSRPD zone found', {
      latitude,
      longitude,
      zone: bestMatch
    });
  } else {
    mastraLogger.info('No WGSRPD zone found for coordinates', { latitude, longitude });
  }

  return bestMatch;
}

/**
 * Get Trefle distribution info for a TDWG code
 */
export function getTrefleDistribution(tdwgCode: string): TrefleDistribution | null {
  return trefleIndexByCode.get(tdwgCode) || null;
}

/**
 * Get all available Trefle distributions
 */
export function getAllTrefleDistributions(): TrefleDistribution[] {
  return Array.from(trefleIndexByCode.values());
}

/**
 * Update the Trefle distributions index (for refreshing from API)
 */
export function updateTrefleDistributions(distributions: TrefleDistribution[]): void {
  mastraLogger.info('Updating Trefle distributions index', { count: distributions.length });

  trefleIndexByCode.clear();
  for (const dist of distributions) {
    trefleIndexByCode.set(dist.tdwgCode, dist);
  }

  mastraLogger.info('Trefle distributions index updated');
}
