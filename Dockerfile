FROM piranha/cyrax

RUN mkdir /src /app
WORKDIR /src
COPY . /src/
COPY vhost.conf /etc/nginx/conf.d/default.conf
COPY CHECKS /app/CHECKS
EXPOSE 5000

RUN cyrax /src -d /www
