import { createBrowserHistory } from 'history';
const history = createBrowserHistory();

var probability = function(n) {
  return !!n && Math.random() <= n;
};

const crasher = () => {
  let queryParams = new URLSearchParams(history.location.search)
  if (queryParams !== "") {
      let crash = queryParams.get("crash")
      if (crash) {
            console.log("> crash", crash)
            if (crash === "true" || probability(parseFloat(crash))) {
              throw new UnhandledException('unhandled error')
            }
      }
  } else {
      console.log("> queryParam was", queryParams)
  }
}

// Based on the official example https://docs.sentry.io/platforms/javascript/usage/sdk-fingerprinting/#group-errors-with-greater-granularity
class UnhandledException extends Error {
  constructor(message, functionName) {
    super(message);
  }
}

export { crasher, UnhandledException }