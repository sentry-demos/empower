// Usage: 'await sleep(1000)'
export async function sleep(milliseconds) {
  await new Promise((resolve) => setTimeout(resolve, milliseconds));
}

// TODO: need to update ../env.sh to populate this value on deployment
export const NEXT_APP_RELEASE = '2024.10.1';

// Consistent with "weeks" as defined in release.sh for calendar version so that
// in Trends improved/regressed change time matches release.
export function isOddReleaseWeek() {
  return getReleaseWeek(NEXT_APP_RELEASE) % 2 == 1;
  // return getReleaseWeek(process.env.REACT_APP_RELEASE) % 2 == 1;
}

function getReleaseWeek(release) {
  var [year, month, week] = release.split('.').map((x) => parseInt(x));
  var pastYears = (year - 22) * 59 - Math.floor((year - 21) / 4);
  return (
    pastYears + (month - 1) * 5 + (month > 2 && year % 4 != 0 ? -1 : 0) + week
  );
}

// is blocking, unlike setTimeout
export function busy_sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if (new Date().getTime() - start > milliseconds) {
      break;
    }
  }
}
