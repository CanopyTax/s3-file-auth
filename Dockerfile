FROM python:3.7-alpine

ENV PYCURL_SSL_LIBRARY=openssl \
    PYTHONPATH=. \
    DOCKER=True

# compile requirements for some python libraries
RUN apk --no-cache add curl-dev bash \
    build-base libffi-dev libressl-dev tini

# install python reqs
COPY ["requirements.txt", "/app/"]
WORKDIR /app

RUN pip install -r /app/requirements.txt

EXPOSE 8080
CMD ["tini", "./startup.sh"]
COPY . /app
