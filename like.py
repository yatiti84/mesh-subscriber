import os
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

def like_handler(content, gql_client):
    memberId = content['memberId'] if 'memberId' in content and content['memberId'] else False
    commentId = content['commentId'] if 'commentId' in content and content['commentId'] else False
    
    if not(memberId and commentId):
        print("no required data for action")
        return False

    if content['action'] == 'add_like':
        action = 'connect'
    elif content['action'] == 'remove_like':
        action = 'disconnect'
    else:
        print("action not exitsts")
        return False
    
    mutation = '''
            mutation{
            updateComment(where:{id:"%s"}, data:{like:{%s:{id:%s}}}){
                like{
                id
                }
            }
            
            }''' % (commentId,action, memberId)
    result = gql_client.execute(gql(mutation))
    print(result)
    return True if isinstance(result, dict) and 'updateComment' in result  else False
    


if __name__ == '__main__':
    gql_endpoint = os.environ['GQL_ENDPOINT']
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport, fetch_schema_from_transport=True)
 
    # print(like_handler(content, gql_client))