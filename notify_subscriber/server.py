import base64
import ast
from flask import Flask, request, Response

from notify import notify_processor
app = Flask(__name__)


@app.route("/notify-sub", methods=['POST'])
def process_data():
    req = request.get_json(silent=True)
    print(req)

    if not req:
        return Response("{'error': 'no Pub/Sub message received'}", status=500, mimetype='application/json')
    if not isinstance(req, dict) or "message" not in req:
        return Response("{'error': 'invalid Pub/Sub message format'}", status=500, mimetype='application/json')
    if not isinstance(req["message"], dict) or "data" not in req["message"]:
        return Response("{'error': 'no data in message received'}", status=500, mimetype='application/json')
    content = base64.b64decode(req["message"]["data"]).decode("utf-8")
    content = ast.literal_eval(content)
    print(content)
    if 'action' in content and content['action']:
        action = content['action']
    else: 
        return Response("{'error': 'data content with error'}", status=500, mimetype='application/json')

    if 'add' or 'remove' in action:
        if notify_processor(content):
            return "success"
        else:
            return Response("{'error': 'update data error'}", status=500, mimetype='application/json')
    


@app.route("/")
def healthcheck():
    return "ok"


if __name__ == "__main__":
    app.run()
