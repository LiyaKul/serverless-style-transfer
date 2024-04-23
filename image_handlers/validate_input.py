import filetype
import json
import sys

from utils import *

def validate_input(event, context):
    for message in event['messages']:
        object_name = message['details']['object_id']
        tmp_file_path = '/tmp/' + object_name
        client = get_boto_session().client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            region_name='ru-central1'
        )
        upload_bucket = os.environ['UPLOADS_BUCKET']

        client.download_file(upload_bucket, object_name, tmp_file_path)
        if not filetype.is_image(tmp_file_path):
            print(object_name, 'is not a file', file=sys.stderr)
            continue
        if os.path.getsize(tmp_file_path) > 1024**2:
            print(object_name, 'size is more than 1Mb', file=sys.stderr)
            continue
            
        get_docapi_table().update_item(
            Key={'task_id': object_name},
            AttributeUpdates={
                'status': {'Value': 'PROCESSING', 'Action': 'PUT'}
            }
        )

        task = get_docapi_table().get_item(Key={'task_id': object_name})['Item']
        get_ymq_queue().send_message(MessageBody=json.dumps({
            'task_id': object_name,
            'model': task['model']
        }))

    return "OK"
