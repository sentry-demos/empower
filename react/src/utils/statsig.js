import { StatsigClient } from '@statsig/js-client';

const STATSIG_CLIENT_KEY = process.env.REACT_APP_STATSIG_CLIENT_KEY;

const featureFlags = ["react_ui_update_feature", "beta_feature", "alpha_feature"];

const initialUser = { userID: Math.random().toString(36).substring(7) };
const statsigClient = new StatsigClient(STATSIG_CLIENT_KEY, initialUser);


/**
 * Updates the Statsig user context, fetches latest values, and evaluates flags.
 * @param {string} userId - The new user ID to use for evaluations.
 * @returns {Promise<void>} A promise that resolves when the update and evaluation are complete.
 */
async function updateStatsigUserAndEvaluate(userId) {
  if (!userId || typeof userId !== 'string') {
    console.error('Invalid userId provided for Statsig update:', userId);
    return;
  }
  const newUser = { userID: userId };
  console.log(`[Statsig] Attempting to update user to: ${JSON.stringify(newUser)}`);
  try {
    console.log(`[Statsig] Calling statsigClient.updateUserSync for user: ${userId}`);
    console.log('StatsigClient', statsigClient);
    await statsigClient.updateUserAsync(newUser);

    featureFlags.forEach(flag => {
      const result = statsigClient.checkGate(flag);
      console.log(` -> statsig ${flag}:`, result);
      const gate = statsigClient.getFeatureGate(flag);
      // Log the full gate object for more details
      console.log(` -> Gate details for ${flag}:`, JSON.stringify(gate));
    });
  } catch (error) {
    console.error(`[Statsig] updateUser or flag evaluation failed for user ${userId}:`, error);
    // Optionally re-throw or report to Sentry
    // Sentry.captureException(new Error(`Statsig update failed for ${userId}: ${error}`));
  }
}
export { statsigClient, updateStatsigUserAndEvaluate };
