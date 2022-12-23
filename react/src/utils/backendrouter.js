const DEFAULT_BACKEND = "flask"

const SUPPORTED_BACKEND_TYPES = {
  "flask": process.env.REACT_APP_FLASK_BACKEND,
  "express": process.env.REACT_APP_EXPRESS_BACKEND,
  "springboot": process.env.REACT_APP_SPRINGBOOT_BACKEND,
  "aspnetcore": process.env.REACT_APP_ASPNETCORE_BACKEND,
  "laravel": process.env.REACT_APP_LARAVEL_BACKEND,
  "ruby": process.env.REACT_APP_RUBY_BACKEND
}

const determineBackendType = (desiredBackend) => {
    if (desiredBackend) {
        if (SUPPORTED_BACKEND_TYPES[desiredBackend]) {
          return desiredBackend
        } else {
          const warnText = "You tried to set backend type as '" + desiredBackend + "', which is not supported. Proceeding with the default type: '" + DEFAULT_BACKEND + "'"
          alert(warnText)
          console.log(warnText)
        }
    }
    return DEFAULT_BACKEND
}

const determineBackendUrl = (backendType) => {
    return SUPPORTED_BACKEND_TYPES[backendType]
}

export { determineBackendType, determineBackendUrl }
