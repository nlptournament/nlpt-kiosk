import boto3
import json
from botocore.exceptions import ConnectionClosedError
from elements import Setting

bkt = {
    'media': 'nkc-media'
}

botoClient = boto3.client(
    's3',
    endpoint_url=f"http://{Setting.value('s3_host')}:{Setting.value('s3_port')}",
    aws_access_key_id=Setting.value('s3_access_key'),
    aws_secret_access_key=Setting.value('s3_access_secret')
)

download_policy = {
  'Version': '2012-10-17',
  'Statement': [
    {
      'Effect': 'Allow',
      'Principal': {
        'AWS': ['*']
      },
      'Action': [
        's3:GetBucketLocation'
      ],
      'Resource': [
        'arn:aws:s3:::BucketName'
      ]
    },
    {
      'Effect': 'Allow',
      'Principal': {
        'AWS': ['*']
      },
      'Action': [
        's3:GetObject'
      ],
      'Resource': [
        'arn:aws:s3:::BucketName/*'
      ]
    }
  ]
}


def is_connected():
    global botoClient
    origCT = botoClient.meta.config.connect_timeout
    botoClient.meta.config.connect_timeout = 1
    origRetries = botoClient.meta.config.retries
    botoClient.meta.config.retries = {'max_attempts': 0}
    result = False
    for i in range(3):
        try:
            botoClient.list_buckets()
            result = True
            break
        except ConnectionClosedError:
            continue
        except Exception:
            break
    botoClient.meta.config.connect_timeout = origCT
    botoClient.meta.config.retries = origRetries
    return result


def setup_storage():
    global botoClient
    global bkt
    buckets = [bucket['Name'] for bucket in botoClient.list_buckets()['Buckets']]
    for bucket in bkt.values():
        if bucket not in buckets:
            botoClient.create_bucket(Bucket=bucket)
        botoClient.put_bucket_policy(Bucket=bucket, Policy=json.dumps(download_policy).replace('BucketName', bucket))


if is_connected():
    setup_storage()


def generic_list(bucket):
    global botoClient
    result = list()
    for c in botoClient.list_objects(Bucket=bucket).get('Contents', list()):
        if c.get('Key'):
            result.append(c.get('Key'))
    return result


def generic_exists(bucket, name):
    global botoClient
    try:
        objects = botoClient.list_objects(Bucket=bucket, Prefix=name)
        objects = [k for k in [obj['Key'] for obj in objects.get('Contents', [])]]
        if name in objects:
            return True
        else:
            return False
    except Exception:
        return False


def generic_get(bucket, name):
    global botoClient
    result = botoClient.get_object(Bucket=bucket, Key=name)
    return result['Body']


def generic_upload(bucket, content, name):
    """
    content = fileobject opened as 'rb'
    """
    global botoClient
    if generic_exists(bucket, name):
        generic_delete(bucket, name)
    try:
        botoClient.upload_fileobj(content, Bucket=bucket, Key=name)
        return True
    except Exception:
        return False


def generic_delete(bucket, name):
    global botoClient
    try:
        botoClient.delete_object(Bucket=bucket, Key=name)
        return True
    except Exception:
        return False


def generic_delete_all(bucket):
    botoResource = boto3.resource(
        's3',
        endpoint_url=f"http://{Setting.value('s3_host')}:{Setting.value('s3_port')}",
        aws_access_key_id=Setting.value('s3_access_key'),
        aws_secret_access_key=Setting.value('s3_access_secret')
    )
    botoResource.Bucket(bucket).objects.all().delete()


"""
Media
"""


def media_exists(id):
    return generic_exists(bucket=bkt['media'], name=id)


def media_get(id):
    return generic_get(bucket=bkt['media'], name=id)


def media_upload(id, content):
    return generic_upload(bucket=bkt['media'], content=content, name=id)


def media_delete(id):
    return generic_delete(bucket=bkt['media'], name=id)
