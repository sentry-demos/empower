import { createBrowserHistory } from 'history';
let history;
//needed to prevent next SSR errors
if (typeof window !== 'undefined') {
  history = createBrowserHistory();
}

// ERRORS
const handleError = (errorFn) => {
  try {
    errorFn();
  } catch (error) {
    if (error instanceof UnhandledException) {
      throw error;
    } else {
      throw new UnhandledException(
        error.message || ErrorMessages[ErrorTypes.UNHANDLED],
        errorFn.name
      );
    }
  }
};

const notAFunctionError = () => {
  try {
    const someArray = [{ func: function () {} }];
    someArray[1].func();
  } catch (error) {
    throw new UnhandledException(
      'Attempted to call function on undefined object',
      'notAFunctionError'
    );
  }
};

const referenceError = () => {
  throw new ReferenceError('undefinedVariable is not defined');
};

//eslint-disable-next-line
const syntaxError = () => {
  try {
    eval('foo bar');
  } catch (error) {
    throw new UnhandledException('Invalid syntax encountered', 'syntaxError');
  }
};

const rangeError = () => {
  throw new RangeError('Parameter must be between 1 and 100');
};

const unhandledError = () => {
  throw new UnhandledException('unhandled error', 'unhandledError');
};

const randomErrors = [
  notAFunctionError,
  referenceError,
  syntaxError,
  rangeError,
  unhandledError,
];

const throwErrorNumber = (i) => {
  const selectedError = randomErrors[i % randomErrors.length];
  handleError(selectedError);
};

// if n is 0.2 then this will return false 20% of the time
var probability = function (n) {
  return !!n && Math.random() <= n;
};


const crasher = () => {
  const queryParams = new URLSearchParams(history.location.search);
  try {
    if (queryParams !== '') {
      const crash = queryParams.get('crash');
      if (crash) {
        console.log('> crash', crash);
        const errnum =
          queryParams.get('errnum') ||
          parseInt(Math.random() * randomErrors.length);
        if (crash === 'true' || probability(parseFloat(crash))) {
          throwErrorNumber(errnum);
        }
      }
    } else {
      console.log('> queryParam was', queryParams);
    }
  } catch (error) {
    if (error instanceof UnhandledException) {
      throw error;
    } else {
      throw new UnhandledException(
        'An unexpected error occurred while simulating crashes',
        'crasher'
      );
    }
  }
};

// Error type definitions
const ErrorTypes = {
  UNHANDLED: 'UnhandledException',
  REFERENCE: 'ReferenceError',
  RANGE: 'RangeError',
  SYNTAX: 'SyntaxError',
  TYPE: 'TypeError'
};

const ErrorMessages = {
  [ErrorTypes.UNHANDLED]: 'An unhandled error occurred',
  [ErrorTypes.REFERENCE]: 'Reference to undefined variable or function',
  [ErrorTypes.RANGE]: 'Value is outside acceptable range',
  [ErrorTypes.SYNTAX]: 'Invalid syntax encountered',
  [ErrorTypes.TYPE]: 'Invalid type operation attempted'
};

// Useful for fingerprinting examples and R&D. You can check `if (exception instanceof UnhandledException)`
// Based on the official example https://docs.sentry.io/platforms/javascript/usage/sdk-fingerprinting/#group-errors-with-greater-granularity
class UnhandledException extends Error {
  constructor(message, functionName) {
    super(message);
    this.name = ErrorTypes.UNHANDLED;
    this.functionName = functionName;
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, UnhandledException);
    }
  }
}

export { crasher, UnhandledException, ErrorTypes, ErrorMessages };
