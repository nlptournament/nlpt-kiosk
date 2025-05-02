from invoke import task


@task(name='container-image-build')
def build_container_image(c, version=None):
    c.run('sudo docker build -t nilsost/nlpt-kiosk-controller-frontend:latest .')
    if version is not None:
        c.run(f'sudo docker tag nilsost/nlpt-kiosk-controller-frontend:latest nilsost/nlpt-kiosk-controller-frontend:{version}')


@task(name='container-image-push')
def push_container_image(c, version=None):
    if version is not None:
        c.run(f'sudo docker push nilsost/nlpt-kiosk-controller-frontend:{version}')
    c.run('sudo docker push nilsost/nlpt-kiosk-controller-frontend:latest')
