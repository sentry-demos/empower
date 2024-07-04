module.exports = function overrideConfig(config) {
  // TODO: Remove once we revert to classical JSX runtime
  //       in the react SDK.
  //       The current version of the react SDK (8.14.0)
  //       breaks with react 17 due to react 17 lacking
  //       exports for jsx-runtime. We therefore rewrite
  //       these to point to the actual file.
  //       See: https://github.com/getsentry/sentry-javascript/pull/12204
  config.resolve.alias = {
    ...config.resolve.alias,
    "react/jsx-dev-runtime": "react/jsx-dev-runtime.js",
    "react/jsx-runtime": "react/jsx-runtime.js",
  }
  return config;
};
