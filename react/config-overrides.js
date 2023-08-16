const SentryWebpackPlugin = require('@sentry/webpack-plugin');

module.exports = function override(config, env) {
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
