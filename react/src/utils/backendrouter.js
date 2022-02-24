const DEFAULT_BACKEND = "flask"

const SUPPORTED_BACKEND_TYPES = {
  "flask": {
      "test": "http://localhost:8080",
      "production": process.env.REACT_APP_FLASK_BACKEND || process.env.REACT_APP_BACKEND
  },
  "express": {
      "test": "http://localhost:8088",
      "production": process.env.REACT_APP_EXPRESS_BACKEND
  },
  "springboot": {
      "test": "http://localhost:8090",
      "production": process.env.REACT_APP_SPRINGBOOT_BACKEND
  },
  "ruby": {
    "test": "http://localhost:4567", // 4567 is Sinatra, 3000 is Rails
    "production": process.env.REACT_APP_RUBY_BACKEND
  }
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

const determineBackendUrl = (backendType, environment) => {
    return SUPPORTED_BACKEND_TYPES[backendType][environment]
}

export { determineBackendType, determineBackendUrl }
