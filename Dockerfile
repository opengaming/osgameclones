FROM nginx:alpine

RUN mkdir /src /app
WORKDIR /src
COPY . /src/
COPY vhost.conf /etc/nginx/conf.d/default.conf
COPY CHECKS /app/CHECKS
EXPOSE 80

RUN apk add --no-cache python py-pip py-yaml && pip install pipenv && pipenv install
RUN env
RUN pipenv run cyrax /src -d /www
