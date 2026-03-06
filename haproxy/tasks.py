from invoke import task


@task(name='container-image-build')
def build_container_image(c, version=None, beta=False, alpha=False):
    if version is not None:
        c.run(f'sudo docker buildx build --platform linux/amd64 -t nilsost/nlpt-kiosk-controller-haproxy:{version} --load .')
        c.run(f'sudo docker buildx build --platform linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:{version} .')
    if alpha:
        c.run('sudo docker buildx build --platform linux/amd64 -t nilsost/nlpt-kiosk-controller-haproxy:alpha --load .')
        c.run('sudo docker buildx build --platform linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:alpha .')
    elif beta:
        c.run('sudo docker buildx build --platform linux/amd64 -t nilsost/nlpt-kiosk-controller-haproxy:beta --load .')
        c.run('sudo docker buildx build --platform linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:beta .')
    else:
        c.run('sudo docker buildx build --platform linux/amd64 -t nilsost/nlpt-kiosk-controller-haproxy:latest --load .')
        c.run('sudo docker buildx build --platform linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:latest .')


@task(name='container-image-push')
def push_container_image(c, version=None, beta=False, alpha=False):
    if version is not None:
        c.run(f'sudo docker buildx build --platform linux/amd64,linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:{version} --push .')
    if alpha:
        c.run('sudo docker buildx build --platform linux/amd64,linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:alpha --push .')
    elif beta:
        c.run('sudo docker buildx build --platform linux/amd64,linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:beta --push .')
    else:
        c.run('sudo docker buildx build --platform linux/amd64,linux/arm64 -t nilsost/nlpt-kiosk-controller-haproxy:latest --push .')
