FROM python:3.7 AS public-lemur

RUN apt-get update && apt-get install -y \
  curl \
  make \
  software-properties-common

RUN curl -sL https://deb.nodesource.com/setup_7.x | bash -

RUN apt-get update && apt-get install -y \
  npm \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev

RUN pip install pip==20.3.2
RUN pip install -U \
  bandit \
  coveralls \
  setuptools==51.1.1

WORKDIR /app
COPY public-lemur /app/
RUN pip install -e .
RUN pip install "file://`pwd`#egg=lemur[dev]"
RUN pip install "file://`pwd`#egg=lemur[tests]"


# build frontend
# need to delete some left-overs from using submodules
WORKDIR /app
RUN rm /app/.git

# doesn't look like bower likes being root so we need --unsafe-perm here
RUN npm install --unsafe-perm
RUN python setup.py sdist bdist_wheel


# NEW STAGE ========================= (multi-stage build to keep image small)
# TODO(jonaspalm): Switch to Spotify base image when they support Python 3.7
FROM python:3.7
RUN apt-get update && apt-get install -y \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev \
  nginx \
  supervisor \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# install lemur wheel from builder
COPY --from=public-lemur /app/dist/lemur-0.8.0-py2.py3-none-any.whl .
RUN pip install lemur-0.8.0-py2.py3-none-any.whl

# install plugins
COPY lemur-plugin-gcp-destination lemur-plugin-gcp-destination
RUN cd lemur-plugin-gcp-destination && pip install . && cd ..

COPY lemur-plugin-ffwd lemur-plugin-ffwd
RUN cd lemur-plugin-ffwd && pip install . && cd ..

# copy static files from builder
COPY --from=public-lemur /app/lemur/static/dist /opt/lemur/static

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
