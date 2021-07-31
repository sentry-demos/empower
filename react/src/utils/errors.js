import { createBrowserHistory } from 'history';
const history = createBrowserHistory();


// REDO
// var deltaArray = [{ func: function () {}}];

// TODO
// error1
// error2

var probability = function(n) {
  return !!n && Math.random() <= n;
};

// crash can be .5, 0.5, 1.0
const crasher = () => {
  let queryParams = new URLSearchParams(history.location.search)
  if (queryParams !== "") {
      let crash = queryParams.get("crash")
      if (crash) {
            console.log("> crash", crash)
            if (crash === "true" || probability(parseFloat(crash))) {
              throw new Error('this is unhandled error')
            }
      }
  } else {
      console.log("> queryParam was", queryParams)
  }
}

export default crasher

// check verse a random number twice, for 2 different error types, or for more variable crash rates...
// if (probability(.02)) {
//     deltaArray[1].func();
//   } else if (probability(.02)) {
//     try {
//       throw new SyntaxError('syntactically invalid code')
//     } catch (error) {
//       console.log(error);
//       Sentry.captureException(error);
//     }
//   } else {
//     console.log('no errors on pageload')
//   }