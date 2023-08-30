const fs = require('fs');
const cp = require('child_process');
const path = require('path');

const buildDir = path.resolve(__dirname, 'build', 'static', 'js');

fs.readdirSync(buildDir).forEach((file) => {
  if (!file.endsWith('.map')) return;

  cp.spawnSync('./node_modules/.bin/react-prod-sourcemaps', [
    '--inputFile',
    path.join(buildDir, file),
  ]);

  let remappedPath = path.join(
    buildDir,
    file.replace('.js.map', '.remapped.js.map')
  );

  if (fs.existsSync(remappedPath)) {
    // remove old
    fs.unlinkSync(path.join(buildDir, file));
    // rename remapped
    fs.renameSync(
      path.join(buildDir, file.replace('.js.map', '.remapped.js.map')),
      path.join(buildDir, file.replace('.remapped.js.map', '.js.map'))
    );
  }
});
