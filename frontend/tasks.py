from invoke import task


@task(name='container-image-build')
def build_container_image(c, version=None):
    if version is not None:
        c.run(f'sudo docker buildx build --platform linux/arm64,linux/amd64,linux/arm/v7 -t nilsost/nlpt-kiosk-controller-frontend:{version}')
    c.run('sudo docker buildx build --platform linux/arm64,linux/amd64,linux/arm/v7 -t nilsost/nlpt-kiosk-controller-frontend:latest .')


@task(name='container-image-push')
def push_container_image(c, version=None):
    if version is not None:
        c.run(f'sudo docker buildx build --platform linux/arm64,linux/amd64,linux/arm/v7 -t nilsost/nlpt-kiosk-controller-frontend:{version} --push .')
    c.run('sudo docker buildx build --platform linux/arm64,linux/amd64,linux/arm/v7 -t nilsost/nlpt-kiosk-controller-frontend:latest --push .')
