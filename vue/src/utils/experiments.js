/**
 * Utility functions for accessing experiment flags and tags
 * These are set in main.js and made available globally
 */

export const getSeTag = () => {
  return sessionStorage.getItem('se');
};

export const isRageClick = () => {
  return window.RAGECLICK === true;
};

export const getProductsApi = () => {
  return window.PRODUCTS_API || 'products';
};

export const isCheckoutSuccess = () => {
  return window.CHECKOUT_SUCCESS === true;
};

export const getBackendType = () => {
  return window.BACKEND_TYPE;
};

export const getBackendUrl = () => {
  return window.BACKEND_URL;
};

export const getUserFeedback = () => {
  return sessionStorage.getItem('userFeedback') || 'false';
};

export const isUserFeedbackEnabled = () => {
  return getUserFeedback() === 'true';
};
