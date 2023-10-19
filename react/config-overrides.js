const SentryWebpackPlugin = require('@sentry/webpack-plugin');
const reactsourceMapPlugin = require('@acemarke/react-prod-sourcemaps');

module.exports = function override(config, env) {
  //do stuff with the webpack config...
  config.plugins.push(
    reactsourceMapPlugin.WebpackReactSourcemapsPlugin({
      mode: 'strict',
    })
  );

  config.plugins.push(
    SentryWebpackPlugin.sentryWebpackPlugin({
      authToken: process.env.SENTRY_AUTH_TOKEN,
      include: '.',
      org: 'demo',
      project: 'react',
      ignoreFile: '.sentrycliignore',
      ignore: ['webpack.config.js'],
      configFile: 'sentry.properties',
    })
  );
  return config;
};
