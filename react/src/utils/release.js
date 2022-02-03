const release = (packageName) => {

    var date = new Date();
    var month = date.getUTCMonth() + 1; //months from 1-12
    var day = date.getUTCDate();
    
    var week
    if (day <= 7) {
        week = 1
    } else if (day <= 14) {
        week = 2
    } else if (day <= 21) {
        week = 3
    } else if (day <= 28) {
        week = 4
    } else if (day <= 35) {
        week = 5
    }
    
    var year = date.getUTCFullYear().toString().slice(-2);

    // package@version
    return `${packageName}@${year}.${month}.${week}`
}

export default release
