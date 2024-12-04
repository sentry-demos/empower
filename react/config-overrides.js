const SentryWebpackPlugin = require('@sentry/webpack-plugin');
const reactsourceMapPlugin = require('@acemarke/react-prod-sourcemaps');
const { codecovWebpackPlugin } = require("@codecov/webpack-plugin");

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
      reactComponentAnnotation: {enabled:true},
    })
  );
  config.plugins.push(
    codecovWebpackPlugin({
      enableBundleAnalysis: process.env.CODECOV_TOKEN !== undefined,
      bundleName: "example-webpack-bundle",
      uploadToken: process.env.CODECOV_TOKEN,
    })
  )
  return config;
};