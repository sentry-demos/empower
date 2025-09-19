/**
 * Utility functions for accessing experiment flags and tags
 * These are set in main.js and made available globally
 */

/**
 * Get the SE tag value for pre-filling forms
 * @returns {string|null} The SE tag value or null if not set
 */
export const getSeTag = () => {
  return sessionStorage.getItem('se');
};

/**
 * Check if frontend slowdown experiment is enabled
 * @returns {boolean} True if frontend slowdown is enabled
 */
export const isFrontendSlowdown = () => {
  return window.FRONTEND_SLOWDOWN === true;
};

/**
 * Check if rage click experiment is enabled
 * @returns {boolean} True if rage click is enabled
 */
export const isRageClick = () => {
  return window.RAGECLICK === true;
};

/**
 * Get the current products API type
 * @returns {string} Either 'products' or 'products-join'
 */
export const getProductsApi = () => {
  return window.PRODUCTS_API || 'products';
};

/**
 * Check if products are extremely slow experiment is enabled
 * @returns {boolean} True if products are extremely slow
 */
export const isProductsExtremelySlow = () => {
  return window.PRODUCTS_EXTREMELY_SLOW === true;
};

/**
 * Check if products backend error experiment is enabled
 * @returns {boolean} True if products backend error is enabled
 */
export const isProductsBeError = () => {
  return window.PRODUCTS_BE_ERROR === true;
};

/**
 * Check if add to cart JS error experiment is enabled
 * @returns {boolean} True if add to cart JS error is enabled
 */
export const isAddToCartJsError = () => {
  return window.ADD_TO_CART_JS_ERROR === true;
};

/**
 * Check if checkout success experiment is enabled
 * @returns {boolean} True if checkout success is enabled
 */
export const isCheckoutSuccess = () => {
  return window.CHECKOUT_SUCCESS === true;
};

/**
 * Get the current backend type
 * @returns {string} The current backend type (e.g., 'flask', 'express')
 */
export const getBackendType = () => {
  return window.BACKEND_TYPE;
};

/**
 * Get the current backend URL
 * @returns {string} The current backend URL
 */
export const getBackendUrl = () => {
  return window.BACKEND_URL;
};

/**
 * Get user feedback setting
 * @returns {string} The user feedback setting
 */
export const getUserFeedback = () => {
  return sessionStorage.getItem('userFeedback') || 'false';
};

/**
 * Check if user feedback is enabled
 * @returns {boolean} True if user feedback is enabled
 */
export const isUserFeedbackEnabled = () => {
  return getUserFeedback() === 'true';
};
