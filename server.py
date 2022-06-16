import base64
import ast
import os
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from flask import Flask, request, Response

from follow import follow_handler
from comment import comment_handler
from pick import pick_handler
from bookmark import bookmark_handler

app = Flask(__name__)


@app.route("/mesh-sub", methods=['POST'])
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
    action = content['action']
    gql_endpoint = os.environ['GQL_ENDPOINT']
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport,
                        fetch_schema_from_transport=True)
    if 'follow' in action:
        if follow_handler(content, gql_client):
            return "success"
        else:
            return Response("{'error': 'update data error'}", status=500, mimetype='application/json')
    if 'comment' in action:
        if comment_handler(content, gql_client):
            return "success"
        else:
            return Response("{'error': 'update data error'}", status=500, mimetype='application/json')
    if 'pick' in action:
        if pick_handler(content, gql_client):
            return "success"
        else:
            return Response("{'error': 'update data error'}", status=500, mimetype='application/json')
    if 'bookmark' in action:
        if bookmark_handler(content, gql_client):
            return "success"
        else:
            return Response("{'error': 'update data error'}", status=500, mimetype='application/json')



@app.route("/")
def healthcheck():
    return "ok"


if __name__ == "__main__":
    app.run()
