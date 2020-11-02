FROM gcr.io/xpn-cert-management/lemur:latest AS builder
RUN python setup.py bdist_wheel -d /app/dist/

# TODO(jonaspalm): Switch to Spotify base image when they support Python 3.7
FROM python:3.7
RUN apt-get update
RUN apt-get install -y libldap2-dev libsasl2-dev libldap2-dev libssl-dev
RUN apt-get install -y nginx
RUN apt-get install -y supervisor

WORKDIR /app

# install lemur wheel from builder
COPY --from=builder /app/dist/lemur-0.7.0-py2.py3-none-any.whl .
RUN pip install lemur-0.7.0-py2.py3-none-any.whl

# copy static files from builder
COPY --from=builder /app/lemur/static/dist /opt/lemur/static

COPY lemur.conf.py /opt/lemur/
ENV LEMUR_CONF /opt/lemur/lemur.conf.py

# setup nginx
COPY nginx.conf /etc/nginx/sites-available/default

# setup supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf .

EXPOSE 80

# ENTRYPOINT [ "lemur" ]
CMD ["/usr/bin/supervisord", "-c", "supervisord.conf"]
