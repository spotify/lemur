# Lemur Ops Handbook

## Source Repositories

* public upstream [Netflix/lemur](https://github.com/Netflix/lemur/) 
* public fork [spotify/lemur](https://github.com/spotify/lemur/) (pulled in as submodule in internal lemur-frontend and spotify-lemur)
* internal [lemur-frontend](https://ghe.spotify.net/wasabi/lemur-frontend/) (static frontend code, used as base-image for spotify-lemur)
* internal [spotify-lemur](https://ghe.spotify.net/wasabi/spotify-lemur/) (main internal repository, including build pipeline, GKE deployment definitions and docs) 📍 you are here
* internal [spotify-lemur-redis](https://ghe.spotify.net/wasabi/spotify-lemur-redis/) (plain redis instance for celery)

## Architecture and components

* [System `certificate-management` in backstage](https://backstage.spotify.net/system/certificate-management/services), [celo secrets role `spotifylemur`](https://backstage.spotify.net/services/spotify-lemur/celo)

* [GCP project `xpn-cert-management`](https://console.cloud.google.com/home/dashboard?organizationId=642708779950&project=xpn-cert-management)

* [GKE namespace `cert-management`](https://ghe.spotify.net/kubernetes/system-resource-manifests/blob/master/manifests/cert-management/namespace.yaml)

* Web interface [certs.spotify.net](https://certs.spotify.net) edge-proxy configuration [lemur-perimeter.yaml](https://ghe.spotify.net/edge/edge-control-service/blob/06177be6ca8fa9a376c7b72cbe2582e5c342728d/exposed-services/lemur-perimeter.yaml)

* On GKE we deploy the following workloads (all in the `cert-management` namespace):
  * [lemur frontend/api proxy](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur/overview?project=gke-xpn-1), serving the web interface (containers: nginx)
  * [lemur backend](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur-backend/overview?project=gke-xpn-1), serving the backend (containers: lemur, cloudsql-proxy)
  * [lemur-celery-beat](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur-celery-beat?project=gke-xpn-1) scheduler (containers: lemur, cloudsql-proxy)
  * [lemur-celery-worker](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/lemur-celery-worker?project=gke-xpn-1) (containers: lemur, cloudsql-proxy)
  * [celery-flower](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-j1b3/cert-management/celery-flower?project=gke-xpn-1) (containers: celery)
  * [lemur-redis-primary-deployment](https://console.cloud.google.com/kubernetes/deployment/europe-west1/europe-west1-4133/cert-management/lemur-redis-primary-deployment?project=gke-xpn-1) (containers: redis)


## Logging and Monitoring

* [Logs in xpn-cert-management project](https://console.cloud.google.com/logs/query?organizationId=642708779950&project=xpn-cert-management) for lemur and celery containers and cloud sql database

* [Celery Flower](https://certs.spotify.net/celery-flower/) - celery task overview

* [Grafana dashboard with ops metrics](https://grafana.spotify.net/d/hlLWwxBGk/lemur)

## Database - manually viewing and changing the production database content

[xpn-cert-management:europe-west1:lemur](
https://console.cloud.google.com/sql/instances/lemur/overview?organizationId=642708779950&project=xpn-cert-management) is the production database.

Authentication relies on IAM, so the username/password is `lemur:lemur`.

### Connect using the cloud_sql_proxy

Connect with the [cloud_sql_proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy):
```
cloud_sql_proxy -instances=xpn-cert-management:europe-west1:lemur=tcp:5432 &
```
And then use a postgresql client, eg:
```
psql -h localhost -p 5432 -U lemur
```

### Connect with gcloud

Run 
```
gcloud sql connect lemur --project xpn-cert-management --user lemur
```
and you will get a postgres prompt.

### Useful postgres commands

`\?` - help

`\dt` - list tables

`select * from TABLE;` - view content of a table

`\q` - quit

### Deleting a certificate 

To delete a certificate and all references from the database, run these commands, replacing `CERT_ID` with the numerical id of the certificate (eg check with `select id,name,cn from certificates;`):

```
delete from certificate_associations where certificate_id=CERT_ID;
delete from roles_certificates where certificate_id=CERT_ID;
delete from logs where certificate_id=CERT_ID;
delete from certificates where id=CERT_ID;
delete from certificate_destination_associations where certificate_id=CERT_ID;
delete from certificate_source_associations where certificate_id=CERT_ID;
delete from certificate_notification_associations where certificate_id=CERT_ID;
delete from certificate_replacement_associations where certificate_id=CERT_ID;
```

Note that the `domains` table might still have entries with the domains the certificate used.

## Celery Tasks

The [Celery Beat schedule is defined in lemur.conf.py](https://ghe.spotify.net/wasabi/spotify-lemur/blob/master/lemur.conf.py#L221).

Tasks can be inpsected with celery-flower on https://certs.spotify.net/celery-flower.

### Manually triggering a celery task

1. Use `kubectx` to make sure you're in the `gke_gke-xpn-1_europe-west1_europe-west1-j1b3` context.
1. Run `kubectl get pods --namespace cert-management` to find out the name of the currently running celery beat pod name.
1. Run `kubectl exec $LEMUR_CELERY_BEAT_POD_NAME celery -- celery -A lemur.common.celery call lemur.common.celery.$TASK_NAME` to run the task $TASK_NAME, so for example `kubectl exec lemur-celery-beat-7cc6d47c4f-qqbkh celery -- celery -A lemur.common.celery call lemur.common.celery.fetch_all_pending_certs`

You will see some log output of lemur/celery starting (a couple of "Skip loading plugin.." messages) and finally a task id. You can check with [celery flower](https://certs.spotify.net/celery-flower) that the task succeeded. 

## Onboarding a new project (destination/source) - IAM permissions

When adding a GCP project as a new destination and source in Lemur, the Lemur service account needs IAM permissions in that project to operate on it. 

On the [IAM page](https://console.cloud.google.com/iam-admin/iam) of the GCP project that will be onboarded, add the following binding: 
- Member: `cert-management@gke-accounts.iam.gserviceaccount.com`
- Role: `Compute Load Balancer Admin`

Or using gsutil in a terminal, run:
```
gcloud projects add-iam-policy-binding <project> --member serviceAccount:cert-management@gke-accounts.iam.gserviceaccount.com --role roles/compute.loadBalancerAdmin
```
