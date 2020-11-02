FROM gcr.io/xpn-cert-management/lemur:latest

COPY lemur.conf.py /opt/lemur/

ENV LEMUR_CONF /opt/lemur/lemur.conf.py

ENTRYPOINT [ "lemur" ]
