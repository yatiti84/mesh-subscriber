import os
import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

gql_endpoint = os.environ['GQL_ENDPOINT']
gql_transport = AIOHTTPTransport(url=gql_endpoint)
gql_client = Client(transport=gql_transport, fetch_schema_from_transport=True)

def check_pick_exists(memberId, storyId, gql_client):

    query = '''
            query{
                picks(where:{member:{id:{in:%s}}, story:{id:{in:%s}}, kind:{equals:"bookmark"}}, orderBy:{id:asc}){
                    id
                }
            }''' % (memberId, storyId)
    result = gql_client.execute(gql(query))
    print(result)
    if isinstance(result, dict) and 'picks' in result:
        if isinstance(result['picks'], list):
            return result['picks']
    return False

def bookmark_handler(content, gql_client):
    memberId = content['memberId']
    storyId = content['storyId']
    check_picks = check_pick_exists(memberId, storyId, gql_client)
    if content['action'] == 'add_bookmark':
        picked_date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        if check_picks == []:# bookmark not exitsts
            mutation = '''
                mutation{
                    createPick(data:{
                        member:{connect:{id:%s}}, 
                        story:{connect:{id:%s}}, 
                        objective:"story", 
                        state:"private",
                        is_active:true,
                        picked_date:"%s",
                        kind:"bookmark",
                    }){
                        id
                        member{
                        id
                        }
                        objective
                        story{
                        id
                        }
                        state
                        is_active
                        kind
                        picked_date                                
                    }
                    }
            ''' % (memberId, storyId, picked_date)
        elif check_picks:# bookmark in pick already existed
            pickId = check_picks[0]['id']
            mutation = '''
            mutation{
                updatePick(where:{id:%s}, data:{is_active:true}){
                    id
                    is_active
                    }
                }
            ''' % (pickId)
        else:
            print("query picks failed")
            return False
        
    elif content['action'] == 'remove_bookmark':
        if check_picks:
            update_data = []
            for pick in check_picks:
                picksId = pick['id']
                update_data.append(
                    '{where:{id:%s}, data:{is_active:false}}' % (picksId))
            update_data = ', '.join(update_data)
            mutation = '''
            mutation{
                    updatePicks(data:[%s]){
                        id
                        kind
                        is_active
                    }
                    }''' % (update_data)
        else: 
            print("query picks failed or remove bookmark not exists")
            return False
   
    else:
        print("action not exitsts")
        return False

    result = gql_client.execute(gql(mutation))
    print(result)
    if isinstance(result, dict) and 'createPick' in result or 'updatePicks' or 'updatePick' in result:
        return True
    return False


if __name__ == '__main__':
    content = {
        'action': 'add_bookmark',
        'memberId': '2',
        'storyId': '6',
    }

    content = {
        'action': 'remove_bookmark',
        'memberId': '2',
        'storyId': '98',
    }

    print(bookmark_handler(content, gql_client))
