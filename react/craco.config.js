const path = require('path');
const { codecovWebpackPlugin } = require('@codecov/webpack-plugin');

module.exports = {
  /* ... */
  plugins: [
    // Put the Codecov webpack plugin after all other plugins
    codecovWebpackPlugin({
      enableBundleAnalysis: process.env.CODECOV_TOKEN !== undefined,
      bundleName: 'empower',
      uploadToken: process.env.CODECOV_TOKEN,
    }),
  ],
};
