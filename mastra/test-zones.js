// Quick test script to verify zone mapping works
import { initializeWgsrpdZones, getWgsrpdZone } from './src/mastra/utils/wgsrpd-zones.ts';

async function testZones() {
  console.log('🧪 Testing WGSRPD zone mapping...');

  try {
    // Initialize zones
    await initializeWgsrpdZones();
    console.log('✅ Zones initialized');

    // Test some coordinates
    const testPoints = [
      { name: 'Birmingham, Alabama', lat: 33.5186, lon: -86.8104 },
      { name: 'Anchorage, Alaska', lat: 61.2181, lon: -149.9003 },
      { name: 'Miami, Florida', lat: 25.7617, lon: -80.1918 },
      { name: 'London, UK', lat: 51.5074, lon: -0.1278 },
    ];

    for (const point of testPoints) {
      const zone = getWgsrpdZone(point.lat, point.lon);
      console.log(`📍 ${point.name}:`, zone ?
        `${zone.name} (${zone.tdwgCode}) -> Trefle: ${zone.trefleSlug || 'N/A'}` :
        'No zone found'
      );
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testZones();
