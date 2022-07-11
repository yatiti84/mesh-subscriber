import os
from datetime import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from query_collection import collection_follower, collection_creator_follower
from query import creator, picker, commenter

def remove_same_member_sender(members, senderId):
    members = set(members)
    members.discard(senderId)
    return members


def create_notify(members, senderId, type_str, obj, objectiveId):
    now_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    mutation_datas = []
    for memberId in members:
        mutation_data = '''{
            member:{
                connect:{
                    id:"%s"
                    }
                },
            sender:{
                connect:{
                    id:"%s"
                    }
                },
            type:"%s",
            objective:"%s",
            object_id:%s,
            state:"unread",
            action_date:"%s"
            }''' % (memberId, senderId, type_str, obj, objectiveId, now_time)
        mutation_datas.append(mutation_data)
    mutation_datas = ','.join(mutation_datas)
    mutation = '''
    mutation{
        createNotifies(data:[%s]){
            id
            member{
                id
            }
            sender{
                id
            }
            type
            state
            action_date
        }
    }''' % mutation_datas
    result = gql_client.execute(gql(mutation))
    if isinstance(result, dict) and 'createNotifies' in result:
        if isinstance(result['createNotifies'], list) and result['createNotifies']:
            return True
    return False


def query_members(senderId, type_str, obj, object_id):
    if type_str == 'follow':
        if obj == 'member':
            return [object_id]
        elif obj == 'collection':
            return creator(gql_client, 'collection', 'creator', object_id)
        elif obj == 'publisher':
            return []
        else:
            print("follow objective not exists.")

    elif type_str == 'comment':
        if obj == 'story':
            story_pickers = picker(gql_client, 'story', object_id)
            story_comment_members = commenter(gql_client, 'story', object_id)
            # story_picker and story_comment_member could be empty list
            return story_pickers + story_comment_members if isinstance(story_pickers, list) and isinstance(story_comment_members, list) else False

        elif obj == 'comment':
            comment_creators = creator(gql_client, 'comment', 'member', object_id)
            comment_pickers = picker(gql_client, 'comment', object_id)
            comment_members = commenter(gql_client, 'root', object_id)
            return comment_creators + comment_pickers + comment_members if comment_creators and isinstance(comment_pickers, list) and isinstance(comment_members, list) else False
        elif obj == 'collection':
            collection_creators = creator(gql_client, 'collection', 'creator', object_id)
            collection_pickers = picker(gql_client, 'collection', object_id)
            collection_comment_members = commenter(gql_client, list_name='collection', targetId=object_id)
            return collection_creators + collection_pickers + collection_comment_members if collection_creators and isinstance(collection_pickers, list) and isinstance(collection_comment_members, list) else False

        else:
            print('comment objective not exists')

    elif type_str == 'pick':
        if obj == 'comment':
            return creator(gql_client, 'comment', 'member', object_id)
        elif obj == 'collection':
            collection_creators = creator(gql_client, 'collection', 'creator', object_id)
            collection_followers = collection_follower(object_id, gql_client)
            # collection__creator must exists or this is a query error # collection_follower could be a empty list
            return collection_creators + collection_followers if collection_creators and isinstance(collection_followers, list) else False
        elif obj == 'story':
            return []
        else:
            print("pick objective not exists.")
    elif type_str == 'heart':
        return creator(gql_client, 'comment', 'member', object_id)
    elif type_str == 'create_collection':
        return collection_creator_follower(senderId, gql_client)
    else:
        print("action type not exists.")
        return False

def notify_processor(content):
    gql_endpoint = os.environ['GQL_ENDPOINT']
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    global gql_client
    gql_client = Client(transport=gql_transport, fetch_schema_from_transport=True)
    
    senderId = content['memberId'] if 'memberId' in content and content['memberId'] else False
    if int(senderId) < 0: 
        print("memberId is visitor")
        return True
    type_str = content['action'].split('_')[-1] if 'action' in content and content['action'] else False
    if 'objective' in content and content['objective']:
        obj = content['objective']
    elif type_str == 'like':
        type_str = 'heart'
        obj = 'comment'
    elif type_str == 'collection':
        type_str = 'create_collection'
        obj = 'collection'
    else:
        return False
    # object_id is targetId or commentId or storyId.
    if 'targetId' in content and content['targetId']:
        object_id = content['targetId']
    elif 'commentId' in content and content['commentId']:
        object_id = content['commentId']
    elif 'storyId' in content and content['storyId']:
        object_id = content['storyId']
    elif 'collectionId' in content and content['collectionId']:
        object_id = content['collectionId']
    else:
        return  False
    # examination of conetent data validation
    if not(senderId and type_str):
        print("no required data for notify")
        return False
    members = query_members(senderId, type_str, obj, object_id)
    if members is False:
        return False
    members = remove_same_member_sender(members, senderId)
    if members:
        return create_notify(members, senderId, type_str, obj, object_id)
    else:
        print("No members.")
        return True


if __name__ == '__main__':

    # content =
    # print(notify_processor(content))
    print("done")
