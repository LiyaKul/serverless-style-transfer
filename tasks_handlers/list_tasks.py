from utils import *

def handle_api(event, context):
    tasks = get_docapi_table().scan()['Items']
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": tasks
    }
