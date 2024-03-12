import os
import json

from style_transfer import process_image
from utils import *

def handle_process_event(event, context):
    for message in event['messages']:
        task = json.loads(message['details']['message']['body'])
        object_name = task['task_id']
        tmp_file_path = '/tmp/' + object_name
        result_file_path = '/tmp/result_' + object_name

        task = get_docapi_table().get_item(Key={'task_id': object_name})['Item']
        model_path = os.getcwd() + '/models/' + task['model'] + '.t7'

        client = get_boto_session().client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            region_name='ru-central1'
        )
        upload_bucket = os.environ['UPLOADS_BUCKET']
        result_bucket = os.environ['RESULTS_BUCKET']

        client.download_file(upload_bucket, object_name, tmp_file_path)
        process_image(tmp_file_path, model_path, result_file_path)
        client.upload_file(result_file_path, result_bucket, object_name)

        get_docapi_table().update_item(
            Key={'task_id': object_name},
            AttributeUpdates={
                'status': {'Value': 'DONE', 'Action': 'PUT'}
            }
        )
    return "OK"
