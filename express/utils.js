const pests = ["aphids", "thrips", "spider mites", "lead miners", "scale", "whiteflies", "earwigs", "cutworms", "mealybugs", "fungus gnats"]

const getIterator = function(n){
    if (n < 0) {
        console.log("Incorrect Input");
    }
    else if (n == 0) {
        return 0
    } 
    else if (n == 1 || n == 2) {
        return 1
    }
    else {
        return getIterator(n-1) + getIterator(n-2)
    }
}

const getIteratorProcessor = async function(products){
    let start = new Date();
    let loop = getIterator(products.length * 6)
    let descriptions = products.filter(p => p.description);
    for (let i = 0; i < loop; i++) {
      let timeDelta = (new Date() - start)/1000
      if (timeDelta > 4) {
        break;
      }

      for (let description in descriptions) {
        for (let pest in pests) {
          if (pests[pest].includes(descriptions[description])) {
            delete products[description]
          }
        }
      }
    }

}

module.exports = { getIteratorProcessor }