## About

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Deploy

See [../README.md](../README.md)

## Query Parameter Options

(These query parameters can be stacked on top of one another)

- `?backend=flask` - [sets the backend url](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L175-L177) (we have multiple backends with similar functionality). [Here](https://github.com/sentry-demos/empower/blob/master/react/src/utils/backendrouter.js#L4-L10) are all the options for backends). Additionally recorded in `backendType` tag.  **Default**: flask
- `?userFeedback=true` - displays [(old) user feedback modal](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L208-L212) 5 seconds after checkout crash.
- `?se=<yourname` - put your name here, for example `?se=chris`, `?se=kosty`, etc. This results in an `se` tag [added to events triggered during the demo](https://github.com/sentry-demos/empower/blob/ea51c3dbce9d50ac32519546e1c772ea5a91722f/react/src/index.js#L191-L198), and [adjust the fingerprint](https://github.com/sentry-demos/empower/blob/ea51c3dbce9d50ac32519546e1c772ea5a91722f/react/src/index.js#L130-L138) to segment issues depending on the SE.
- `?crash=true` - forces [a crash](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/utils/errors.js#L41) of one of predefined types, selected randomly.
- `?crash=true&errnum=3` - forces crash of specific type depending on `errnum` value
- `?userEmail=someemail@example.com` - lets you [pass in a specific user email](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L218-L219)
- `?frontendSlowdown=true` - used in the [frontend-only demo flow](https://github.com/sentry-demos/empower/blob/fce289530f72ce47fe2c7482cdbd9aa8bcc13b6e/react/src/index.js#L200-L207), which showcases a frontend slowdown via profiling.
