import os
import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport


def check_pick_exists(memberId, obj, targetId, gql_client):
    query = '''
    query{
        picks(where:{member:{id:{in:%s}},
                                objective:{equals:"%s"},
                                %s:{id:{in:%s}},
                                kind:{equals:"read"},

        }, orderBy:{id:desc}){
            id
            is_active
            pick_comment{
            id
            is_active
            }
        }
    }''' % (memberId, obj, obj, targetId)
    result = gql_client.execute(gql(query))
    if isinstance(result, dict) and 'picks' in result:
        if isinstance(result['picks'], list):
            return result['picks']
    return False


def create_pick_mutation(memberId, obj, targetId, state, published_date, pick_comment, gql_client):
    mutation = '''
            mutation{
                createPick(data:{
                    member:{connect:{id:%s}},
                    objective: "%s",
                    %s:{connect:{id:%s}},
                    kind:"read",
                    state:"%s",
                    is_active:true,
                    picked_date:"%s",
                    %s
                }){
                    id,
                }
        }''' % (memberId, obj, obj, targetId, state, published_date, pick_comment)
    result = gql_client.execute(gql(mutation))
    if isinstance(result, dict) and 'createPick' in result:
        return True
    return False


def update_pick_mutation(update_data, gql_client):
    mutation = '''
                mutation{
                updatePicks(data:[%s]){
                        id
                        is_active
                    }
                }''' % (update_data)
    result = gql_client.execute(gql(mutation))
    if isinstance(result, dict) and 'updatePicks' in result:
        return True
    return False


def add_pick_mutatioin(content, gql_client):
    memberId = content['memberId']
    targetId = content['targetId']
    obj = content['objective']
    published_date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    state = content['state']

    check_picks = check_pick_exists(memberId, obj, targetId, gql_client)
    if check_picks == []:  # pick not exitsts create new pick
        pick_comment = ''
        return create_pick_mutation(memberId, obj, targetId, state, published_date, pick_comment, gql_client)
    elif check_picks:  # update pick is_active to true
        pickId = check_picks[0]['id']
        update_data = '{where:{id:%s}, data:{is_active:true}}' % (pickId)
        return update_pick_mutation(update_data, gql_client)
    else:
        print("query picks failed")
        return False


def pick_and_comment_mutation(content, gql_client):
    memberId = content['memberId']
    targetId = content['targetId']
    obj = content['objective']
    pick_content = content['content']
    published_date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    state = content['state']
    if content['objective'] == 'comment':
        comment_obj = 'root'
    else:
        comment_obj = content['objective']
    pick_comment = '''
            pick_comment:{
                create:{
                    member:{connect:{id:%s}},
                    state: "%s",
                    published_date:"%s",
                    content:"%s"
                    %s:{connect:{id:%s}}
                }
            }''' % (memberId, state, published_date, pick_content, comment_obj, targetId)

    return create_pick_mutation(memberId, obj, targetId, state, published_date, pick_comment, gql_client)


def unpick_mutation(content, gql_client):
    memberId = content['memberId']
    targetId = content['targetId']
    obj = content['objective']
    check_picks = check_pick_exists(memberId, obj, targetId, gql_client)
    if check_picks:
        update_data_pick = []
        update_data_comment = []
        for pick in check_picks:
            picksId = pick['id']
            update_data_pick.append(
                '{where:{id:%s}, data:{is_active:false}}' % (picksId))
            if pick['pick_comment']:
                for pick_comment in pick['pick_comment']:
                    pick_comment_data = '{where:{id:%s},data:{is_active:false}}' % (
                        pick_comment['id'])
                    update_data_comment.append(pick_comment_data)
        update_data_comment = ', '.join(set(update_data_comment))
        update_data_pick = ', '.join(set(update_data_pick))
        if update_data_comment:
            mutation_comment = '''
            mutation{
                updateComments(data:[%s]){
                    id
                    is_active
                }
            }''' % (update_data_comment)
            result = gql_client.execute(gql(mutation_comment))
            if not(isinstance(result, dict) or 'updateComments' in result):
                return False
        return update_pick_mutation(update_data_pick, gql_client)


def pick_handler(content, gql_client):

    if content['action'] == 'add_pick':
        return add_pick_mutatioin(content, gql_client)
    elif content['action'] == 'pick_and_comment':
        return pick_and_comment_mutation(content, gql_client)
    elif content['action'] == 'unpick':
        return unpick_mutation(content, gql_client)
    else:
        print("action not exitsts")
        return False


if __name__ == '__main__':
    gql_endpoint = os.environ['GQL_ENDPOINT']
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    gql_client = Client(transport=gql_transport,
                        fetch_schema_from_transport=True)

    content = {
        'action': 'add_pick',
        'memberId': '2',
        'objective': 'story',
        'targetId': '8',
        'state': 'friend',
    }
    content = {
        'action': 'pick_and_comment',
        'memberId': '2',
        'objective': 'story',
        'targetId': '8',
        'state': 'private',
        'content': '我是content while pick'
    }
    content = {
        'action': 'unpick',
        'memberId': '2',
        'objective': 'story',
        'targetId': '8',
    }

    print(pick_handler(content, gql_client))
