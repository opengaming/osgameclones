FROM alpine AS builder

RUN mkdir /src /app
WORKDIR /src
COPY . /src/
COPY CHECKS /app/CHECKS

RUN apk add --no-cache curl make gcc musl-dev libffi-dev python3 python3-dev
RUN env
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/etc/poetry python3 -

ENV PATH /etc/poetry/bin/:$PATH

RUN poetry install
RUN make run 

FROM nginx:1.27.4-alpine

COPY --from=builder /src/_build /www
COPY vhost.conf /etc/nginx/conf.d/default.conf
COPY CHECKS /app/CHECKS
EXPOSE 80
