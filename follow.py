import os
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

gql_endpoint = os.environ['GQL_ENDPOINT']
gql_transport = AIOHTTPTransport(url=gql_endpoint)
gql_client = Client(transport=gql_transport, fetch_schema_from_transport=True)


def follow_handler(content, gql_client):

    memberId = content['memberId']
    targetId = content['targetId']

    if content['action'] == 'add_follow':
        action = 'connect'
    elif content['action'] == 'remove_follow':
        action = 'disconnect'
    else:
        print("action not exitsts")
        return False

    if content['objective'] == 'member':
        obj_following = 'following'
    elif content['objective'] == 'publisher':
        obj_following = 'follow_publisher'
    elif content['objective'] == 'collection':
        obj_following = 'following_collection'
    else:
        print("objective not exitsts")
        return False
        
    mutation = '''
    mutation{
    updateMember(where:{id:%s}, data:{%s:{%s:{id:%s}}},){
        following{
        id
        }
    }
    }''' % (memberId, obj_following, action, targetId)
    result = gql_client.execute(gql(mutation))
    print(result)
    if isinstance(result, dict) and 'updateMember' in result:
        follow_item = [follow_item['id'] for follow_item in result['updateMember'][obj_following]]
        if targetId in follow_item and action == 'connect':
            return True
        if targetId not in follow_item and action == 'disconnect':
            return True
    return False


if __name__ == '__main__':
    content = {
        'action': 'remove_follow',
        'memberId': '2',
        'objective': 'member',
        'targetId': '3'
    }

    print(follow_handler(content, gql_client))
