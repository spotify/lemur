FROM gcr.io/xpn-cert-management/lemur:latest AS builder
RUN python setup.py bdist_wheel -d /app/dist/

# TODO(jonaspalm): Switch to Spotify base image when they support Python 3.7
FROM python:3.7
RUN apt-get update
RUN apt-get install -y libldap2-dev libsasl2-dev libldap2-dev libssl-dev

WORKDIR /app

# install lemur wheel from builder
COPY --from=builder /app/dist/lemur-0.7.0-py2.py3-none-any.whl .
RUN pip install lemur-0.7.0-py2.py3-none-any.whl

# copy static files from builder
COPY --from=builder /app/lemur/static/dist /opt/lemur/static

COPY lemur.conf.py /opt/lemur/
ENV LEMUR_CONF /opt/lemur/lemur.conf.py

ENTRYPOINT [ "lemur" ]
