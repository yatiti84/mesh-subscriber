import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
import base64
import ast
from flask import Flask, request, Response

app = Flask(__name__)

client = google.cloud.logging.Client()
handler = CloudLoggingHandler(client)
cloud_logger = logging.getLogger('userLogger')
cloud_logger.setLevel(logging.INFO)
cloud_logger.addHandler(handler)

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
    data = {}
    if 'action' in content and content['action']:
        data['action'] = content['action']
    else:
        return Response("{'error': 'parameter error: action missing'}", status=400, mimetype='application/json')
    
    if 'memberId' in content and content['memberId']:
        data['memberId'] = content['memberId']
    else:
        return Response("{'error': 'parameter error: memberId missing'}", status=400, mimetype='application/json')

    if 'targetId' in content and content['targetId']:
        data['objId'] = content['targetId']
    elif 'commentId' in content and content['commentId']:
        data['objId'] = content['commentId']
    elif 'storyId' in content and content['storyId']:
        data['objId'] = content['storyId']
    elif 'collectionId' in content and content['collectionId']:
        data['objId'] = content['collectionId']

    if 'objective' in content and content['objective']:
        data['objective'] = content['objective']

    cloud_logger.info(str(data))
    return "success"
    


@app.route("/")
def healthcheck():
    return "ok"


if __name__ == "__main__":
    app.run()