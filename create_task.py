import sys
import uuid

from urllib.parse import urlparse, parse_qs

from utils import *

models = ['feathers', 'mosaic', 'the_scream']

def handle_api(event, context):
    model = parse_qs(urlparse(event['url']).query)['model'][0]
    if model not in models:
        return {
            "statusCode": 400,
            "headers": {"content-type": "application/json"},
            "body": "Unexpected model type. Choose one of ['feathers', 'mosaic', 'the_scream']"
        }

    task_id = str(uuid.uuid4()) + '.jpg'
    get_docapi_table().put_item(Item={
        'task_id': task_id,
        'model': model,
        'status': 'NEW'
    })
    client = get_storage_client()
    bucket = os.environ['UPLOADS_BUCKET']
    presigned_url = client.generate_presigned_url(ClientMethod='put_object', ExpiresIn=3600, Params={'Bucket': bucket, 'Key': task_id})
    answer = {
        'task_id': task_id,
        'presigned_url': presigned_url
    }
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": answer
    }
