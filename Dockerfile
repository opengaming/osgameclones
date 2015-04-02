FROM piranha/cyrax

RUN mkdir /src
WORKDIR /src
COPY . /src/
COPY vhost.conf /etc/nginx/conf.d/default.conf
EXPOSE 5000

RUN cyrax /src -d /www
