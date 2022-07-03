import os
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport

from follow import follow_handler
from comment import comment_handler
from pick import pick_handler
from bookmark import bookmark_handler
from like import like_handler

def assign_action_handler(content):
    if 'action' in content and content['action']:
        action = content['action']
        gql_endpoint = os.environ['GQL_ENDPOINT']
        gql_transport = AIOHTTPTransport(url=gql_endpoint)
        gql_client = Client(transport=gql_transport,
                            fetch_schema_from_transport=True)
        if 'follow' in action:
            return follow_handler(content, gql_client)
        if 'pick' in action:
            return pick_handler(content, gql_client)
        if 'comment' in action:
            return comment_handler(content, gql_client)
        if 'bookmark' in action:
            return bookmark_handler(content, gql_client)
        if 'like' in action:
            return like_handler(content, gql_client)
    return False
    
    
    


