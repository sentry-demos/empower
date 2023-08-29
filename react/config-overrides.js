const SentryWebpackPlugin = require('@sentry/webpack-plugin');

module.exports = function override(config, env) {
  //do stuff with the webpack config...
  config.plugins.push(
    SentryWebpackPlugin.sentryWebpackPlugin({
      authToken: process.env.SENTRY_AUTH_TOKEN,
      org: 'testorg-az',
      project: 'frontend-javascript',
      ignore: [],
    })
  );
  return config;
};
