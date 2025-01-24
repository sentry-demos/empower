import { NextResponse } from "next/server";
import {
  determineBackendUrl,
} from '@/src/utils/backendrouter';

export async function POST(request) {
  try {
    console.log("Here in POST");


    const { email } = await request.json();
    if (!email) {
      return NextResponse.json({ error: 'Email is required' }, { status: 400 });
    }

    const backendUrl = determineBackendUrl('flask');
    const resp = await fetch(`${backendUrl}/enqueue`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email }),
    });

    if (!resp.ok) {
      const errorText = await resp.text();
      console.error('Backend error:', errorText);
      return NextResponse.json({ error: 'Failed to enqueue email' }, { status: resp.status });
    }

    const data = await resp.json();

    return NextResponse.json({ response: data }, { status: 200 });
  } catch (err) {
    console.error('Error handling POST request:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
