const DEFAULT_BACKEND = 'flask';

const SUPPORTED_BACKEND_TYPES = {
  flask: import.meta.env.VITE_FLASK_BACKEND_URL,
  express: import.meta.env.VITE_EXPRESS_BACKEND_URL,
  springboot: import.meta.env.VITE_SPRINGBOOT_BACKEND_URL,
  aspnetcore: import.meta.env.VITE_ASPNETCORE_BACKEND_URL,
  laravel: import.meta.env.VITE_LARAVEL_BACKEND_URL,
  ruby: import.meta.env.VITE_RUBY_BACKEND_URL,
  rails: import.meta.env.VITE_RUBYONRAILS_BACKEND_URL,
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
