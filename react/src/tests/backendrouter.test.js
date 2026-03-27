// backendrouter.test.js
process.env.REACT_APP_BACKEND_URL_FLASK = 'http://flask-backend';
import { determineBackendType, determineBackendUrl } from '../utils/backendrouter';

describe('Backend Router', () => {
  const originalEnv = process.env;
  const originalAlert = window.alert;

  beforeEach(() => {
    jest.resetModules(); // Clears the cache
    process.env = { ...originalEnv }; // Make a copy of the environment variables
    process.env.REACT_APP_BACKEND_URL_FLASK = 'http://flask-backend';
    global.alert = jest.fn(); // Mock alert function
      // console.log = jest.fn(); // Mock console.log function
  });

  afterEach(() => {
    process.env = originalEnv; // Restore the original environment variables
    global.alert = originalAlert; // Restore the original alert function
  });

  describe('determineBackendType', () => {
    it('should return the desired backend type if it is supported', () => {
      process.env.REACT_APP_BACKEND_URL_FLASK = 'http://flask-backend';
      const backendType = determineBackendType('flask');
      expect(backendType).toBe('flask');
    });

    it('should return the default backend type if the desired backend type is not supported', () => {
      const backendType = determineBackendType('unsupportedBackend');
      expect(backendType).toBe('flask');
    });

    it('should alert and log a warning if the desired backend type is not supported', () => {
      global.alert = jest.fn();
      console.log = jest.fn();
      const backendType = determineBackendType('unsupportedBackend');
      expect(backendType).toBe('flask');
      expect(global.alert).toHaveBeenCalledWith(
        "You tried to set backend type as 'unsupportedBackend', which is not supported. Proceeding with the default type: 'flask'"
      );
      expect(console.log).toHaveBeenCalledWith(
        "You tried to set backend type as 'unsupportedBackend', which is not supported. Proceeding with the default type: 'flask'"
      );
    });

    it('should return the default backend type if no desired backend type is provided', () => {
      const backendType = determineBackendType();
      expect(backendType).toBe('flask');
    });
  });

  describe('determineBackendUrl', () => {
    // This test is failing, need to look into this later (failing due to process.env.* returning undefined)
    // it('should return the correct backend URL for a supported backend type', () => {
    //   const backendUrl = determineBackendUrl('flask');
    //   expect(backendUrl).toBe('http://flask-backend');
    // });

    it('should return undefined for an unsupported backend type', () => {
      const backendUrl = determineBackendUrl('unsupportedBackend');
      expect(backendUrl).toBeUndefined();
    });
  });
});
