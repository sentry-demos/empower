const DEFAULT_BACKEND = 'flask';

const SUPPORTED_BACKEND_TYPES = {
  flask: process.env.NEXT_PUBLIC_FLASK_BACKEND,
  express: process.env.NEXT_PUBLIC_EXPRESS_BACKEND,
  springboot: process.env.NEXT_PUBLIC_SPRINGBOOT_BACKEND,
  aspnetcore: process.env.NEXT_PUBLIC_ASPNETCORE_BACKEND,
  laravel: process.env.NEXT_PUBLIC_LARAVEL_BACKEND,
  rails: process.env.NEXT_PUBLIC_RUBYONRAILS_BACKEND,
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
  console.log("Supported backend types: ", SUPPORTED_BACKEND_TYPES);
  return SUPPORTED_BACKEND_TYPES[backendType];
};

export { determineBackendType, determineBackendUrl };
