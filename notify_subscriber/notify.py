import os
from datetime import datetime
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from query_collection import query_collection_creator, query_collection_follower, query_collection_creator_follower, query_collection_picker, query_collection_comment_member
from query_comment import query_comment_creator, query_comment_picker, query_comment_member
from query_story import query_story_picker, query_story_comment_member


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
    print(result)
    if isinstance(result, dict) and 'createNotifies' in result:
        if isinstance(result['createNotifies'], list) and result['createNotifies']:
            return True
    return False


def query_members(senderId, type_str, obj, object_id):
    if type_str == 'follow':
        if obj == 'member':
            return [object_id]
        elif obj == 'collection':
            return query_collection_creator(object_id, gql_client)
        else:
            print("follow objective not exists.")

    elif type_str == 'comment':
        if obj == 'story':
            story_picker = query_story_picker(object_id, gql_client)
            story_comment_member = query_story_comment_member(object_id, gql_client)
            # story_picker and story_comment_member could be empty list
            return story_picker + story_comment_member if isinstance(story_picker, list) and isinstance(story_comment_member, list) else False

        elif obj == 'comment':
            comment__creator = query_comment_creator(object_id, gql_client)
            comment_picker = query_comment_picker(object_id, gql_client)
            comment_member = query_comment_member(object_id, gql_client)
            return comment__creator + comment_picker + comment_member if comment__creator and isinstance(comment_picker, list) and isinstance(comment_member, list) else False
        elif obj == 'collection':
            collection__creator = query_collection_creator(object_id, gql_client)
            collection__picker = query_collection_picker(object_id, gql_client)
            collection_comment_member = query_collection_comment_member(object_id, gql_client)
            return collection__creator + collection__picker + collection_comment_member if collection__creator and isinstance(collection__picker, list) and isinstance(collection_comment_member, list) else False

        else:
            print('comment objective not exists')

    elif type_str == 'pick':
        if obj == 'comment':
            return query_comment_creator(object_id, gql_client)
        elif obj == 'collection':
            collection__creator = query_collection_creator(object_id, gql_client)
            collection_follower = query_collection_follower(object_id, gql_client)
            # collection__creator must exists or this is a query error # collection_follower could be a empty list
            return collection__creator + collection_follower if collection__creator and isinstance(collection_follower, list) else False
        else:
            print("pick objective not exists.")
    elif type_str == 'like':
        return query_comment_creator(object_id, gql_client)
    elif type_str == 'create_collection':
        return query_collection_creator_follower(senderId, gql_client)
    else:
        print("action type not exists.")
        return False


def notify_processor(content):
    gql_endpoint = os.environ['GQL_ENDPOINT']
    gql_transport = AIOHTTPTransport(url=gql_endpoint)
    global gql_client
    gql_client = Client(transport=gql_transport, fetch_schema_from_transport=True)
    senderId = content['memberId'] if 'memberId' in content and content['memberId'] else False
    type_str = content['action'].split('_')[-1] if 'action' in content and content['action'] else False

    if 'objective' in content and content['objective']:
        obj = content['objective']
    elif type_str == 'like':
        obj = 'comment'
    elif type_str == 'collection':
        type_str = 'create_collection'
        obj = 'collection'

    else:
        obj = False
    # object_id is targetId or commentId or storyId.
    if 'targetId' in content and content['targetId']:
        object_id = content['targetId']
    elif'commentId' in content and content['commentId']:
        object_id = content['commentId']
    elif'storyId' in content and content['storyId']:
        object_id = content['storyId']
    elif'collectionId' in content and content['collectionId']:
        object_id = content['collectionId']
    else:
        object_id = False
    # examination of conetent data validation
    if not(senderId and type_str and obj and object_id):
        print("no required data for notify")
        return False
    members = query_members(senderId, type_str, obj, object_id)
    members = remove_same_member_sender(members, senderId)
    print(members)
    if members:
        return create_notify(members, senderId, type_str, obj, object_id)

    if members is False:
        return False
    else:
        print("No members.")
        return True


if __name__ == '__main__':

    # content =
    # print(notify_processor(content))
    print("done")
