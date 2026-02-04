import * as Sentry from "@sentry/node";
export const delay = (ms: number) =>
  new Promise((resolve) => setTimeout(resolve, ms));

export const randomDelay = (min: number, max: number) => {
  return delay(Math.floor(Math.random() * (max - min + 1)) + min);
};

export const maybeThrow = (probability: number, error: Error) => {
  if (Math.random() < probability) {
    // Sentry does not capture exceptions automatically here
    Sentry.captureException(error);
    throw error;
  }
};
