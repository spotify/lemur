FROM gcr.io/xpn-cert-management/spotify-lemur-frontend@sha256:2d548d4f50ddafd81db9f44026e7183d1f73e84e34c86a5af128aa828adec68d AS public-lemur

RUN apt-get update && apt-get install -y \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev \
  libpq-dev \
  autoconf \
  git \
  gcc

RUN pip install pip==20.3.2
RUN pip install -U \
  bandit \
  coveralls \
  setuptools==51.1.1 \
  wheel

WORKDIR /app
COPY public-lemur /app/
RUN pip install -e .
RUN pip install "file://`pwd`#egg=lemur[dev]"
RUN pip install "file://`pwd`#egg=lemur[tests]"


RUN python setup.py bdist_wheel


# NEW STAGE ========================= (multi-stage build to keep image small)
FROM gcr.io/spotify-base-images/bionic-python3.7:2020.11-1@sha256:4767165cdd16cf6d763c8b2b3d1c83830ff0f5d10aecd4f8a619fbc2fcf9c235
RUN apt-get update && apt-get install -y \
  libldap2-dev \
  libsasl2-dev \
  libssl-dev \
  gcc \
  libpq-dev \
  nginx \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app

# install lemur wheel from builder
COPY --from=public-lemur /app/dist/lemur-0.8.0-py2.py3-none-any.whl .
RUN pip install lemur-0.8.0-py2.py3-none-any.whl

# install plugins
COPY lemur-plugin-gcp lemur-plugin-gcp
RUN cd lemur-plugin-gcp && pip install . && cd ..

COPY lemur-plugin-ffwd lemur-plugin-ffwd
RUN cd lemur-plugin-ffwd && pip install . && cd ..

COPY lemur-plugin-slack lemur-plugin-slack
RUN cd lemur-plugin-slack && pip install . && cd ..

# install flower
RUN pip install flower 
COPY start-flower.sh celery-flower-conf.py /opt/lemur/

# copy static files from builder
COPY --from=public-lemur /app/lemur/static/dist /opt/lemur/static

COPY lemur.conf.py /opt/lemur/
ENV LEMUR_CONF /opt/lemur/lemur.conf.py

# setup nginx
COPY nginx.conf /etc/nginx/sites-available/default

EXPOSE 80