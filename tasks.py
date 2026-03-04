from invoke import task


@task(name='dev-start')
def start_development(c):
    r = c.run('sudo docker ps -f name=dev-mongo', hide=True)
    if 'dev-mongo' not in r.stdout:
        print('Starting mongoDB')
        c.run('sudo docker run --name dev-mongo --rm -p 27017:27017 -d mongo:4.4')

    r = c.run('sudo docker ps -f name=dev-minio', hide=True)
    if 'dev-minio' not in r.stdout:
        print('Starting minIO')
        env = '-e MINIO_ROOT_USER=nlptkc -e MINIO_ROOT_PASSWORD=password'
        ports = '-p 9000:9000 -p 9001:9001'
        c.run(f'sudo docker run --name dev-minio --rm {ports} {env} -d minio/minio:RELEASE.2025-04-22T22-12-26Z server /data --console-address ":9001"')


@task(name='dev-stop')
def stop_development(c):
    for name in ['dev-mongo', 'dev-minio']:
        r = c.run(f'sudo docker ps -f name={name}', hide=True)
        if name in r.stdout:
            print(f'Stopping {name}')
            c.run(f'sudo docker stop {name}')


@task(pre=[stop_development], post=[start_development], name='dev-clean')
def cleanup_development(c):
    pass


@task(name='container-images-build', aliases=['cib', ])
def build_container_images(c):
    version = c.run('git describe', warn=True, hide=True)
    version_arg = ''
    if version.return_code > 0:
        version = None
    else:
        version = version.stdout.strip().replace('v', '', 1)
        if '-' in version:
            version, build = version.rsplit('-', 1)[0].rsplit('-', 1)
            major, minor, _ = version.split('.')
            minor = int(minor) + 1
            version = f'{major}.{minor}.0.beta{build}'
            version_arg = f' --version {version} --beta'
        else:
            version_arg = f' --version {version}'

    if version:
        with open('backend/helpers/version.py', 'w') as f:
            f.write(f"version = '{version}'")
    c.run(f'cd backend; invoke container-image-build{version_arg}')
    c.run('git restore backend/helpers/version.py')
    c.run(f'cd frontend; invoke container-image-build{version_arg}')


@task(name='container-images-push', aliases=['cip', ])
def push_container_images(c):
    version = c.run('git describe', warn=True, hide=True)
    version_arg = ''
    if version.return_code > 0:
        version = None
    else:
        version = version.stdout.strip().replace('v', '', 1)
        if '-' in version:
            version, build = version.rsplit('-', 1)[0].rsplit('-', 1)
            major, minor, _ = version.split('.')
            minor = int(minor) + 1
            version = f'{major}.{minor}.0.beta{build}'
            version_arg = f' --version {version} --beta'
        else:
            version_arg = f' --version {version}'

    if version:
        with open('backend/helpers/version.py', 'w') as f:
            f.write(f"version = '{version}'")
    c.run(f'cd backend; invoke container-image-push{version_arg}')
    c.run('git restore backend/helpers/version.py')
    c.run(f'cd frontend; invoke container-image-push{version_arg}')
