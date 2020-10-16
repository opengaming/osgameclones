FROM nginx:1.17-alpine

RUN mkdir /src /app
WORKDIR /src
COPY . /src/
COPY vhost.conf /etc/nginx/conf.d/default.conf
COPY CHECKS /app/CHECKS
EXPOSE 80

ENV LANG C
RUN apk add --no-cache python3 py3-yaml && \
    pip3 --disable-pip-version-check install pipenv && \
    pipenv install
RUN env
RUN pipenv run /src/render.py -d /www && pipenv run htmlmin /www/index.html /www/index.html
