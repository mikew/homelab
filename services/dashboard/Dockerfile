FROM node:20-alpine

WORKDIR /app

ENV DOCKER_GEN_VERSION=0.10.6
RUN apk add --update bash curl && curl -L \
    https://github.com/nginx-proxy/docker-gen/releases/download/$DOCKER_GEN_VERSION/docker-gen-alpine-linux-amd64-$DOCKER_GEN_VERSION.tar.gz \
    | tar -xzv -C /usr/local/bin

COPY ./data/dashboard-config-generator/package.json /app
COPY ./data/dashboard-config-generator/package-lock.json /app
RUN npm install --production

COPY ./data/dashboard-config-generator /app

ENTRYPOINT ["/app/entrypoint"]
