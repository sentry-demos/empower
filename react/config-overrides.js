const fs = require('fs');
const cp = require('child_process');
const path = require('path');

const SentryWebpackPlugin = require('@sentry/webpack-plugin');

class RewireReactSourceMapsPlugin {
  name = 'rewire-react-sourcemaps';
  apply(compiler) {
    compiler.hooks.afterEmit.tap(
      'rewire-react-sourcemaps',
      (compilation, callback) => {
        const outputPath = compilation.outputOptions.path ?? path.resolve();
        const jsAssetsPath = path.join(outputPath, 'static/js');

        fs.readdirSync(jsAssetsPath).forEach((file) => {
          if (!file.endsWith('.map')) return;

          cp.spawnSync('./node_modules/.bin/react-prod-sourcemaps', [
            '--inputFile',
            path.join(jsAssetsPath, file),
          ]);

          let remappedPath = path.join(
            jsAssetsPath,
            file.replace('.js.map', '.remapped.js.map')
          );

          if (fs.existsSync(remappedPath)) {
            console.log('✅ Remapped', file);
            fs.unlinkSync(path.join(jsAssetsPath, file));
            fs.renameSync(
              path.join(
                jsAssetsPath,
                file.replace('.js.map', '.remapped.js.map')
              ),
              path.join(
                jsAssetsPath,
                file.replace('.remapped.js.map', '.js.map')
              )
            );
          }
        });
      }
    );
  }
}

module.exports = function override(config, env) {
  config.plugins.push(new RewireReactSourceMapsPlugin());
  //do stuff with the webpack config...
  config.plugins.push(
    SentryWebpackPlugin.sentryWebpackPlugin({
      authToken: process.env.SENTRY_AUTH_TOKEN,
      include: '.',
      org: 'testorg-az',
      project: 'frontend-javascript',
      ignoreFile: '.sentrycliignore',
      ignore: ['webpack.config.js'],
      configFile: 'sentry.properties',
    })
  );
  return config;
};
