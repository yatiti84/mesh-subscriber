import google.cloud.logging as logging
import base64
import ast
import os
from datetime import datetime, timedelta
from flask import Flask, request, Response

app = Flask(__name__)


@app.route("/log-sub", methods=['POST'])
def process_data():
    req = request.get_json(silent=True)
    if not req:
        return Response("{'error': 'no Pub/Sub message received'}", status=400, mimetype='application/json')
    if not isinstance(req, dict) or "message" not in req:
        return Response("{'error': 'invalid Pub/Sub message format'}", status=400, mimetype='application/json')
    if not isinstance(req["message"], dict) or "data" not in req["message"]:
        return Response("{'error': 'no data in message received'}", status=400, mimetype='application/json')
    content = base64.b64decode(req["message"]["data"]).decode("utf-8")
    content = ast.literal_eval(content)
    # action, memberId is must have
    now = (datetime.utcnow() + timedelta(hours = 8)).strftime("%Y.%m.%d %H:%M:%S")
    if 'action' in content and content['action']:
        action = content['action']
    else:
        return Response("{'error': 'parameter error: action missing'}", status=400, mimetype='application/json')
    
    if 'memberId' in content and content['memberId'] and content['memberId'] != 0:
        memberId = content['memberId']
    else:
        return Response("{'error': 'parameter error: memberId missing'}", status=400, mimetype='application/json')

    if 'targetId' in content and content['targetId']:
        objId = content['targetId']
    elif 'commentId' in content and content['commentId']:
        objId = content['commentId']
    elif 'storyId' in content and content['storyId']:
        objId = content['storyId']
    elif 'collectionId' in content and content['collectionId']:
        objId = content['collectionId']
    else:
        objId = ''
    
    objective = content['objective']  if 'objective' in content and content['objective'] else ''
    uuid = content['UUID'] if 'UUID' in content and content['UUID'] else''
    clientOS = content['os'] if 'os' in content and content['os']  else ''
    version = content['version'] if 'version' in content and content['version'] else ''
    device = content['device'] if 'device' in content and content['device'] else ''
    
    project_id = os.environ['project_id']
    log_name = os.environ['log_name'] # readr-mesh-user-log-dev
    logger_name = f'projects/{project_id}/logs/{log_name}'
    resource = logging.Resource(type='global', labels={'project_id': project_id})
    clientInfo = {
    'client-info':
        {
        'current-runtime-start': now,
        'datetime': now,
        'exit-time': now,
        'action': action,
        'memberId': memberId,
        'objId': objId,
        'objective': objective
            },
    'client-os': {
        'UUID': uuid,
        'name': clientOS,
        'version': version,
        'device name': device,
            }
    }
    logging_client = logging.Client()
    logger = logging_client.logger(logger_name)
    logger.log_struct(info = clientInfo, severity = "INFO", resource = resource, log_name = logger_name)
    return "success"


@app.route("/")
def healthcheck():
    return "ok"


if __name__ == "__main__":
    app.run()