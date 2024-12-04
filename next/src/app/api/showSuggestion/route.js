
import { NextResponse } from "next/server";
import { getProductsOnly } from '@/lib/data.js';
import {
  determineBackendUrl,
} from '@/src/utils/backendrouter';


export async function GET(request) {
  const backendUrl = determineBackendUrl('flask');

  const resp = await fetch(backendUrl + `/showSuggestion`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })
    .then((result) => {
      if (!result.ok) {
        // Sentry.setContext('err', {
        //   status: result.status,
        //   statusText: result.statusText,
        // });
        return Promise.reject();
      } else {
        return result.json();
      }
    });

  return NextResponse.json({ response: resp.response }, { status: 200 })
}

function extractRelevantDataAsString(items) {
  return items.map(item =>
    `Title: ${item.title}, Description: ${item.description}, Price: ${item.price}`
  ).join('; ');
}
