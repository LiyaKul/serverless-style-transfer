from utils import *
from urllib.parse import urlparse, parse_qs

def handle_api(event, context):
    task_id = parse_qs(urlparse(event['url']).query)['task_id'][0]
    task_ = get_docapi_table().get_item(Key={'task_id': task_id})
    if 'Item' not in task_.keys():
        return {
            'statusCode': 400,
            'headers': {'content-type': 'application/json'},
            'body': 'No such task'
        }
    task = task_['Item']
    client = get_storage_client()
    bucket = os.environ['RESULTS_BUCKET']
    body = None
    if task['status'] == 'DONE':
        url = client.generate_presigned_url(ClientMethod='get_object', ExpiresIn=3600, Params={'Bucket': bucket, 'Key': task_id})
        body = {
            'status': 'DONE',
            'mode': task['model'],
            'url': url
        }
    else:
        body = {
            'status': task['status'],
            'mode': task['model']
        }
    return {
        'statusCode': 200,
        'headers': {'content-type': 'application/json'},
        'body': body
    }
