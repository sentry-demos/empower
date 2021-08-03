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
              // TODO make unique fingerprint
              throw new Error('this is a unhandled error test')
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