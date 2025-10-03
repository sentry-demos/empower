import { Injectable } from '@angular/core';
import * as Sentry from '@sentry/angular';

@Injectable({
  providedIn: 'root'
})
export class FeatureFlagsService {
  private flagsIntegration: Sentry.FeatureFlagsIntegration | null = null;

  // Same feature flags as React but with angular prefix
  private featureFlags = ["angular_ui_update_feature", "beta_feature", "alpha_feature"];

  constructor() {
    // Get the feature flags integration from Sentry
    this.flagsIntegration = Sentry.getClient()?.getIntegrationByName<Sentry.FeatureFlagsIntegration>('FeatureFlags') || null;
    
    if (!this.flagsIntegration) {
      console.warn('FeatureFlags integration not found. Check your Sentry configuration.');
    }
  }

  /**
   * Add a feature flag evaluation to Sentry context
   * @param flagName - The name of the feature flag
   * @param flagValue - The boolean value of the flag
   */
  addFeatureFlag(flagName: string, flagValue: boolean): void {
    if (this.flagsIntegration) {
      this.flagsIntegration.addFeatureFlag(flagName, flagValue);
    } else {
      console.warn(`Cannot add feature flag ${flagName}: FeatureFlags integration not available`);
    }
  }

  /**
   * Evaluate feature flags exactly like React does
   * Uses the same flag names as React: react_ui_update_feature, beta_feature, alpha_feature
   */
  evaluateFeatureFlags(): void {
    this.featureFlags.forEach(flag => {
      // Generate random boolean values like React would
      const result = Math.random() > 0.5;
      this.addFeatureFlag(flag, result);
      console.log(` -> feature flag ${flag}:`, result);
    });
  }

  /**
   * Generate random user ID exactly like React does
   */
  generateRandomUserId(): string {
    return Math.random().toString(36).substring(7);
  }
}