FROM canopytax/python-base

RUN apk add --update \
    ca-certificates && \
    rm -rf /var/cache/apk/*

EXPOSE 8080