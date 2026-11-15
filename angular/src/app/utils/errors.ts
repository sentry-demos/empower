// Angular Errors Utility - Replicates React crash functionality EXACTLY

const CRASHER_ENABLED = (window as any).REACT_APP_ENABLE_CRASHER === 'true';

// Custom error class for unhandled exceptions
export class UnhandledException extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'UnhandledException';
  }
}

// ERRORS - EXACTLY matching React implementation
const notAFunctionError = () => {
  const someArray: any[] = [];
  someArray[1].func();  // This will throw TypeError: Cannot read properties of undefined
};

const referenceError = () => {
  throw new ReferenceError('undefinedVariable is not defined');  // Same as React
};

const syntaxError = () => eval('foo bar');  // Same as React

const rangeError = () => {
  throw new RangeError('Parameter must be between 1 and 100');  // Same as React
};

const unhandledError = () => {
  throw new UnhandledException('unhandled error');  // Same as React
};

// Array of different error types - EXACTLY matching React
const randomErrors = [
  notAFunctionError,
  referenceError,
  syntaxError,
  rangeError,
  unhandledError,
];

// Throw a specific error by number - same as React
const throwErrorNumber = (i: number) => {
  const errorFunction = randomErrors[i % randomErrors.length];
  if (errorFunction) {
    errorFunction();
  }
};

// Probability function - if n is 0.2 then this will return false 20% of the time
const probability = (n: number): boolean => {
  return !!n && Math.random() <= n;
};

// Main crash function - EXACTLY matching React implementation
export const crasher = (): void => {
  const queryParams = new URLSearchParams(window.location.search);
  
  // Check if there are any query parameters (like React)
  if (queryParams.toString() !== '') {
    const crash = queryParams.get('crash');
    
    if (crash) {
      if (!CRASHER_ENABLED) {
        console.log('> crasher disabled', crash);
        return;
      }
      console.log('> crash', crash);
      const errnumRaw = queryParams.get('errnum');
      const errnumParsed = parseInt(errnumRaw || '', 10);
      const errnum = !isNaN(errnumParsed) 
        ? errnumParsed 
        : Math.floor(Math.random() * randomErrors.length);
      
      if (crash === 'true' || probability(parseFloat(crash))) {
        // Call immediately like React does (no setTimeout)
        throwErrorNumber(errnum);
      }
    }
  } else {
    console.log('> queryParam was', queryParams);
  }
};

// Export the random errors array for testing
export { randomErrors };
