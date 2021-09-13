const DEFAULT_BACKEND = "flask"
const SUPPORTED_BACKEND_TYPES = {
  "flask": {
      "test": "http://localhost:8080",
      "prod": process.env.FLASK_BACKEND || process.env.REACT_APP_BACKEND
  },
  "express": {
      "test": "http://localhost:**TBD**",
      "prod": process.env.EXPRESS_BACKEND
  },
  "springboot": {
      "test": "http://localhost:**TBD**",
      "prod": process.env.SPRINGBOOT_BACKEND
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
    const urlOptions = SUPPORTED_BACKEND_TYPES[backendType]
    if (environment === "test") {
        return urlOptions["test"]
    }
    return urlOptions["prod"]
}

export { determineBackendType, determineBackendUrl }
