# Install NLPT-KioskController

KioskController is designed to run as a docker-compose stack. Therefore the only thing you need is a server, that does hove docker with the compose extension installed.

After this, create directory for nkc, put the *docker-compose.yml* from github in there, maybe define some environment variables (see below), pull the images and start the stack.

The workflow could look something like this:

```bash
mkdir /opt/nkc
cd /opt/nkc
curl -o docker-compose.yml https://raw.githubusercontent.com/nlptournament/nlpt-kiosk/refs/heads/main/docker-compose.yml
touch .env
docker compose pull
docker compose up -d
```

Thats already it, you can now keep reading, to get some additional information, or continue with a [first walktrough](./first-steps.md) to get an idea on how to use the controller.

> [!NOTE]
> All containers are provided as amd64 and arm64, in this manner it is also possible to setup the contoller on a RaspberryPI (A RaspberryPi5 with at least 2GB of RAM is recommended)

## Compose level environment variables

The compose file is desigend to take some variables from a local `.env` file.

As an example, to change the NKC version from the stable branch to the beta branch, the content would look like this:

```
NKC_VERSION=beta
```

Here the full list of all currently supported variables:

| Variable      | Default         | Purpose |
| ------------- | --------------- | ------- |
| NKC_VERSION   | latest          | Any version tag available on docker-hub, special tags are latest, beta and alpha, where latest always points to the latest stable version |
| BIND_IP       | 0.0.0.0         | IP at which NKC should be available at on the server, 0.0.0.0 equals to all |
| MONITORING_IP | 0.0.0.0         | If you have a separate monitoring network, bind the corresponding IP here |
| TZ            | Europe/Berlin   | Timezone of the server |
| NTP_SERVER    | de.pool.ntp.org | Upstream timeserver(s) for the builtin timeserver |
| MINIO_PW      | password        | Password of minio, please see the warning below |

> [!CAUTION]
> If you change the MINIO_PW (where I personally see no reason for) NKC is not able to access the S3 storage by default anymore.
> After starting NKC you need to go to *User->Settings* in the Admin-Interface, and change the corresponding Setting to the new password as well.

## Backend level environment variables

If you like to build you own compose file, or like to use an external mongodb server, be aware that the backend container is able to accept the following
environment varibales to configure the mongodb connection: `MONGO_HOST`, `MONGO_PORT` and `MONGO_DB`.  
The backend is currently not designed to execute authenticated connections, only anonymous...

## Create a backup

As everything is contained within the nkc directory just take the stack down (to ensure mongodb comitted all changes to the disk) and create a compressed tar file of the whole directory content.

```bash
cd /opt/nkc
docker compose down
tar czvpf backup.tar.gz * .env
```

## Behind the Scenes

TBD: some more information on the conatianers involved
