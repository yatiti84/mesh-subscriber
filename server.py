import base64
import ast
from flask import Flask, request, Response
from follow import follow_handler

app = Flask(__name__)

@app.route("/mesh-sub", methods=['POST'])
def process_data():
    req = request.get_json(silent=True)
    print(req)
    if not req:
        return  Response("{'error': 'no Pub/Sub message received'}", status=500, mimetype='application/json')
    if not isinstance(req, dict) or "message" not in req:
        return Response("{'error': 'invalid Pub/Sub message format'}", status=500, mimetype='application/json')
    if  not isinstance(req["message"], dict) or "data" not in req["message"]:
        return  Response("{'error': 'no data in message received'}", status=500, mimetype='application/json')
    content = base64.b64decode(req["message"]["data"]).decode("utf-8")
    content = ast.literal_eval(content)
    print(content)
    action = content['action']
    if 'follow' in action:
        if follow_handler(content):
            return "success"
        else:
            return Response("{'error': 'update data error'}", status=500, mimetype='application/json')
        
@app.route("/")
def healthcheck():
    return "ok"

if __name__ == "__main__":
    app.run()