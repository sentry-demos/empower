import config from 'eslint-config-prettier';

export default [
  {
    languageOptions: {
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
  },
  ...([].concat(config)),
];
