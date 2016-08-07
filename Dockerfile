FROM nginx:alpine

RUN apk add --no-cache python py-pip py-yaml && pip install cyrax
RUN mkdir /src /app
WORKDIR /src
COPY . /src/
COPY vhost.conf /etc/nginx/conf.d/default.conf
COPY CHECKS /app/CHECKS
EXPOSE 80

RUN env
RUN cyrax /src -d /www
