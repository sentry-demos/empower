const DEFAULT_BACKEND = 'flask';

const SUPPORTED_BACKEND_TYPES = {
  flask: process.env.REACT_APP_BACKEND_URL_FLASK,
  express: process.env.REACT_APP_BACKEND_URL_EXPRESS,
  springboot: process.env.REACT_APP_BACKEND_URL_SPRINGBOOT,
  aspnetcore: process.env.REACT_APP_BACKEND_URL_ASPNETCORE,
  laravel: process.env.REACT_APP_BACKEND_URL_LARAVEL,
  ruby: process.env.REACT_APP_BACKEND_URL_RUBY,
  rails: process.env.REACT_APP_BACKEND_URL_RUBYONRAILS,
};

const determineBackendType = (desiredBackend) => {
  if (desiredBackend) {
    if (SUPPORTED_BACKEND_TYPES[desiredBackend]) {
      return desiredBackend;
    } else {
      const warnText =
        "You tried to set backend type as '" +
        desiredBackend +
        "', which is not supported. Proceeding with the default type: '" +
        DEFAULT_BACKEND +
        "'";
      alert(warnText);
      console.log(warnText);
    }
  }
  return DEFAULT_BACKEND;
};

const determineBackendUrl = (backendType) => {
  return SUPPORTED_BACKEND_TYPES[backendType];
};

export { determineBackendType, determineBackendUrl };
