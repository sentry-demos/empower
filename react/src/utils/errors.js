import * as Sentry from '@sentry/react';
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
              // TODO choose from 1 or 2 error types
              throw new Error('this is a unhandled error test')
              
              // TODO make unique fingerprint
              // Sentry.withScope(function(scope) {
                // // scope.setFingerprint(['{{ default }}', scope._session.release]);
                // scope.setFingerprint(['test']); 
                // Sentry.captureException(new Error('this is a unhandled error test')) // (grouped by custom fingerprint)
                // throw new Error('this is a unhandled error test') // (grouped by exception stack-trace, in-app exception stack-trace)
              // });
              // throw new Error('this is a unhandled error test')

            }
      }
  } else {
      console.log("> queryParam was", queryParams)
  }
}

export default crasher

// REDO
// var deltaArray = [{ func: function () {}}];
// TODO
// error1
// error2