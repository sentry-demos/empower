// Minimal Server-Sent Events reader over fetch + ReadableStream.
//
// Not EventSource: that can only issue GETs and cannot set request headers, and
// a turn needs to POST the message and send x-conversation-id.

const FRAME_SEPARATOR = /\n\n/;

// Parse one SSE frame ("event: x\ndata: {...}") into {event, data}.
function parseFrame(frame) {
  let event = 'message';
  const dataLines = [];

  for (const line of frame.split('\n')) {
    if (line.startsWith(':')) continue; // comment / keep-alive
    if (line.startsWith('event:')) {
      event = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim());
    }
  }

  if (dataLines.length === 0) return null;

  try {
    return { event, data: JSON.parse(dataLines.join('\n')) };
  } catch (err) {
    // A frame we can't parse shouldn't kill the turn.
    return { event, data: { raw: dataLines.join('\n') } };
  }
}

/**
 * POST to `url` and invoke `onEvent({event, data})` for each SSE frame.
 *
 * Always pass an options object through to fetch: window.fetch is monkeypatched
 * in index.js to do `args[1].headers = {...}` with no guard, so a single-argument
 * call throws.
 */
export default async function postEventStream(url, { headers, body, signal, onEvent }) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed: HTTP ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  // eslint-disable-next-line no-constant-condition
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // A read can land mid-frame, so only consume complete frames and keep the
    // remainder buffered for the next chunk.
    let split = buffer.split(FRAME_SEPARATOR);
    buffer = split.pop();
    for (const frame of split) {
      const parsed = parseFrame(frame);
      if (parsed) onEvent(parsed);
    }
  }

  const trailing = parseFrame(buffer);
  if (trailing) onEvent(trailing);
}
