import { createBrowserHistory } from 'history';
const history = createBrowserHistory();

// ERRORS
const notAFunctionError = () => {
  const someArray = [{ func: function () {}}];
  someArray[1].func();
}
const referenceError = () => {
  throw new ReferenceError('undefinedVariable is not defined')
};
//eslint-disable-next-line
const syntaxError = () => eval('foo bar');
const rangeError = () => {
  throw new RangeError('Parameter must be between 1 and 100');
}
const unhandledError = () => {
  throw new UnhandledException('unhandled error')
}

const randomErrors = [
  notAFunctionError,
  referenceError,
  syntaxError,
  rangeError,
  unhandledError
]

const throwRandomError = () => {
  const randomNum = parseInt(Math.random()*randomErrors.length)
  randomErrors[randomNum]()
}

// if n is 0.2 then this will return false 20% of the time
var probability = function(n) {
  return !!n && Math.random() <= n;
};

const crasher = () => {
  const queryParams = new URLSearchParams(history.location.search)
  if (queryParams !== "") {
    const crash = queryParams.get("crash")
    if (crash) {
      console.log("> crash", crash)
      if (crash === "true" || probability(parseFloat(crash))) {
        throwRandomError();
      }
    }
  } else {
    console.log("> queryParam was", queryParams)
  }
}

// Useful for fingerprinting examples and R&D. You can check `if (exception instanceof UnhandledException)`
// Based on the official example https://docs.sentry.io/platforms/javascript/usage/sdk-fingerprinting/#group-errors-with-greater-granularity
class UnhandledException extends Error {
  constructor(message, functionName) {
    super(message);
  }
}

export { crasher, UnhandledException }
