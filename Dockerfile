# build step
FROM lemur:latest AS builder
RUN python setup.py bdist --format=gztar

# installation step
FROM python:3.7 AS setup
RUN apt-get update
RUN apt-get install -y libldap2-dev libsasl2-dev libldap2-dev libssl-dev

WORKDIR /app

## install requirements
COPY --from=builder /app/requirements.txt .
RUN pip install -r requirements.txt

## extract lemur
COPY --from=builder /app/dist/lemur-0.7.0.linux-x86_64.tar.gz .
RUN tar -C / -xvzf lemur-0.7.0.linux-x86_64.tar.gz

## copy static files from builder
COPY --from=builder /app/lemur/static/dist /opt/lemur/static

COPY lemur.conf.py /opt/lemur/
ENV LEMUR_CONF /opt/lemur/lemur.conf.py
