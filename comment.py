import os
import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

gql_endpoint = os.environ['GQL_ENDPOINT']
gql_transport = AIOHTTPTransport(url=gql_endpoint)
gql_client = Client(transport=gql_transport, fetch_schema_from_transport=True)

def add_comment_mutation(content):
    memberId = content['memberId']
    targetId = content['targetId']
    state = content['state']
    comment_content = content['content']
    published_date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


    if content['objective'] == 'comment':
        obj = 'root'
    else:
        obj = content['objective']

    mutation = '''
            mutation{
                createComment(data:{
                    member:{connect:{id:%s}}, 
                    %s:{connect:{id:%s}}, 
                    is_active:true, 
                    state:"%s", 
                    published_date:"%s", 
                    content:"%s"
                    })
                    {
                id
                } 
            }''' % (memberId, obj, targetId, state, published_date, comment_content)
    return mutation
def rm_comment_mutation(content):
    commentId = content['commentId']
    mutation = '''
         mutation{
            updateComment(where:{id:%s}, data:{is_active:false}){
                id
                }
            }''' % (commentId)
    return mutation
def edit_comment_mutation(content):
    commentId = content['commentId']
    comment_content = content['content']
    mutation = '''
        mutation{
            updateComment(where:{id:%s}, data:{content:"%s", is_edited:true}){
                id
                }
            }''' % (commentId, comment_content)
    return mutation
    
def comment_handler(content, gql_client):

    if content['action'] == 'add_comment':
        mutation = add_comment_mutation(content)
    elif content['action'] == 'remove_comment':
        mutation = rm_comment_mutation(content)
    elif content['action'] == 'edit_comment':
        mutation = edit_comment_mutation(content)
    else:
        print("action not exitsts")
        return False

    result = gql_client.execute(gql(mutation))
    print(result)
    if isinstance(result, dict) and 'createComment' in result or 'updateComment' in result:
        return True
    return False


if __name__ == '__main__':
    content = {
        'action': 'add_comment',
        'memberId': '2',
        'objective': 'comment',
        'targetId': '96',
        'state': 'public',
        'content': '我是comment content in comment'
    }
    content = {
        'action': 'remove_comment',
        'commentId': '99'
    }
    content = {
        'action': 'edit_comment',
        'commentId': '99',
        'content': 'new content in comment'
    }

    print(comment_handler(content, gql_client))
