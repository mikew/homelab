FROM alpine

RUN apk add --update aws-cli bash

COPY data/docker-entrypoint /

ENTRYPOINT ["/docker-entrypoint"]
