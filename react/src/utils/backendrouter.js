const DEFAULT_BACKEND = 'flask';

const SUPPORTED_BACKEND_TYPES = {
  flask: process.env.REACT_APP_BACKEND_URL_FLASK,
  express: process.env.REACT_APP_BACKEND_URL_EXPRESS,
  'spring-boot': process.env.REACT_APP_BACKEND_URL_SPRINGBOOT,
  aspnetcore: process.env.REACT_APP_BACKEND_URL_ASPNETCORE,
  laravel: process.env.REACT_APP_BACKEND_URL_LARAVEL,
  'ruby-on-rails': process.env.REACT_APP_BACKEND_URL_RUBYONRAILS,
  'flask-otlp': process.env.REACT_APP_BACKEND_URL_FLASKOTLP,
  'spring-boot-otlp': process.env.REACT_APP_BACKEND_URL_SPRINGBOOTOTLP,
};

const determineBackendType = (desiredBackend) => {
  if (desiredBackend) {
    if (SUPPORTED_BACKEND_TYPES[desiredBackend]) {
      return desiredBackend;
    } else {
      const supportedBackendsList = Object.keys(SUPPORTED_BACKEND_TYPES)
        .map(type => `- ${type}`)
        .join('\n');
      const warnText =
        "?backend value not recognized.\nSupported backends:\n" +
        supportedBackendsList;
      alert(warnText);
    }
  }
  return DEFAULT_BACKEND;
};

const determineBackendUrl = (backendType) => {
  return SUPPORTED_BACKEND_TYPES[backendType];
};

export { determineBackendType, determineBackendUrl };
