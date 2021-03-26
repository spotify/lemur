# Lemur Ops Handbook

## Source Repositories

* public upstream [Netflix/lemur](https://github.com/Netflix/lemur/) 
* public fork [spotify/lemur](https://github.com/spotify/lemur/) (pulled in as submodule in internal lemur-frontend and spotify-lemur)
* internal [lemur-frontend](https://ghe.spotify.net/wasabi/lemur-frontend/) (static frontend code, used as base-image for spotify-lemur)
* internal [spotify-lemur](https://ghe.spotify.net/wasabi/spotify-lemur/) (main internal repository, including build pipeline, GKE deployment definitions and docs) 📍 you are here
* internal [spotify-lemur-redis](https://ghe.spotify.net/wasabi/spotify-lemur-redis/) (plain redis instance for celery)

## Architecture and components

* [System `certificate-management` in backstage](https://backstage.spotify.net/system/certificate-management/services)

* [GKE namespace `cert-management`](https://ghe.spotify.net/kubernetes/system-resource-manifests/blob/master/manifests/cert-management/namespace.yaml)

* [GCP project `xpn-cert-management`](https://console.cloud.google.com/home/dashboard?organizationId=642708779950&project=xpn-cert-management)

* Web interface [certs.spotify.net](https://certs.spotify.net) edge-proxy configuration [lemur-perimeter.yaml](https://ghe.spotify.net/edge/edge-control-service/blob/06177be6ca8fa9a376c7b72cbe2582e5c342728d/exposed-services/lemur-perimeter.yaml)

* On GKE we deploy the following workloads (all in the `cert-management` namespace):
  * [lemur frontend/api proxy](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur/overview?project=gke-xpn-1), serving the web interface (containers: nginx)
  * [lemur backend](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur-backend/overview?project=gke-xpn-1), serving the backend (containers: lemur, cloudsql-proxy)
  * [lemur-celery-beat](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur-celery-beat?project=gke-xpn-1) scheduler (containers: lemur, cloudsql-proxy)
  * [lemur-celery-worker](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur-celery-worker?project=gke-xpn-1) (containers: lemur, cloudsql-proxy)
  * [lemur-redis-primary-deployment](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-4133/cert-management/lemur-redis-primary-deployment?project=gke-xpn-1) (containers: redis)
  * [celery-flower](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/celery-flower?project=gke-xpn-1) (containers: celery)


## Logging and Monitoring

* [Logs in xpn-cert-management project](https://console.cloud.google.com/logs/query?organizationId=642708779950&project=xpn-cert-management) for lemur and celery containers and cloud sql database

* [Celery Flower](https://certs.spotify.net/celery-flower/) - celery task overview

* [Grafana dashboard with ops metrics](https://grafana.spotify.net/d/hlLWwxBGk/lemur)
