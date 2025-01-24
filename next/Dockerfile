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
    REACT_APP_ASPNETCORE_BACKEND=http://localhost:8091 \
    REACT_APP_EXPRESS_BACKEND=http://localhost:8088 \
    REACT_APP_FLASK_BACKEND=http://localhost:8080 \
    REACT_APP_LARAVEL_BACKEND=http://localhost:8000 \
    REACT_APP_RUBYONRAILS_BACKEND=http://localhost:5000 \
    REACT_APP_RUBY_BACKEND=http://localhost:4567 \
    REACT_APP_SPRINGBOOT_BACKEND=http://localhost:8090 \
        ./build.sh

CMD ["serve", "-s", "build"]
