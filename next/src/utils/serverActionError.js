export class ServerActionError extends Error {
    constructor(message) {
      super(message);
      this.name = "ServerActionError";
    }
  }
   
  export function createServerAction(callback) {
    return async (...args) => {
      try {
        const value = await callback(...args);
        return { success: true, value };
      } catch (error) {
        if (error instanceof ServerActionError)
          return { success: false, error: error.message };
        throw error;
      }
    };
  }