FROM node:18-buster-slim

RUN : \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        # for envsusbst
        gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g serve

WORKDIR /src
COPY package.json package-lock.json .
RUN npm install

COPY . .

RUN \
    REACT_APP_DSN=http://react@localhost:9989/2 \
    REACT_APP_RELEASE=2023+compose \
    SENTRY_AUTH_TOKEN=ignored \
    REACT_APP_BACKEND_URL_ASPNETCORE=http://localhost:8091 \
    REACT_APP_BACKEND_URL_EXPRESS=http://localhost:8088 \
    REACT_APP_BACKEND_URL_FLASK=http://localhost:8080 \
    REACT_APP_BACKEND_URL_LARAVEL=http://localhost:8000 \
    REACT_APP_BACKEND_URL_RUBYONRAILS=http://localhost:5000 \
    REACT_APP_BACKEND_URL_RUBYONRAILS=http://localhost:4567 \
    REACT_APP_BACKEND_URL_SPRINGBOOT=http://localhost:8090 \
        ./build.sh

CMD ["serve", "-s", "build"]
