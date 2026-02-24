const DEFAULT_BACKEND = 'flask';

const SUPPORTED_BACKEND_TYPES = {
  flask: process.env.NEXT_PUBLIC_FLASK_BACKEND,
  express: process.env.NEXT_PUBLIC_EXPRESS_BACKEND,
  'spring-boot': process.env.NEXT_PUBLIC_SPRINGBOOT_BACKEND,
  aspnetcore: process.env.NEXT_PUBLIC_ASPNETCORE_BACKEND,
  laravel: process.env.NEXT_PUBLIC_LARAVEL_BACKEND,
  'ruby-on-rails': process.env.NEXT_PUBLIC_RUBYONRAILS_BACKEND,
  'flask-otlp': process.env.NEXT_PUBLIC_FLASKOTLP_BACKEND,
  'spring-boot-otlp': process.env.NEXT_PUBLIC_SPRINGBOOTOTLP_BACKEND,
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
  console.log("Supported backend types: ", SUPPORTED_BACKEND_TYPES);
  return SUPPORTED_BACKEND_TYPES[backendType];
};

export { determineBackendType, determineBackendUrl };
