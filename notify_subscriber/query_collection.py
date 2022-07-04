from gql import gql

 
def query_collection_creator(collectionId, gql_client):
    collection_creator = '''
    query{
        collection(where:{id:"%s"}){
            creator{
                id
            }
        }
    }'''% collectionId
    result = gql_client.execute(gql(collection_creator))
    print(result)
    if isinstance(result,dict) and 'collection' in result:
        collection = result['collection']
        if isinstance(collection,dict) and 'creator' in collection:
            return [collection['creator']['id']]
        else:
            print("Collection creator not found.")
    else:
        print("Collection not found.")
    return False
def query_collection_follower(collectionId, gql_client):
    membersId = []
    collection_follower = '''
        query{
            members(where:{following_collection:{some:{id:{equals:"%s"}}}}){
                id
                }
        }'''% collectionId
    result = gql_client.execute(gql(collection_follower))
    print(result)
    if isinstance(result,dict) and 'members' in result:
        members = result['members']
        if isinstance(members,list):
            if members:
                for member in  members:
                    membersId.append(member['id'])
            else:
                print("no member following this collection")
            return membersId
    
    print("collection_follower query error")
    return False

def query_collection_creator_follower(senderId, gql_client):
    membersId = []
    collection_creator_follower = '''
    query{
        member(where:{id:%s}){
            follower{
                id
            }
        }
    }''' % senderId
    result = gql_client.execute(gql(collection_creator_follower))
    print(result)
    if isinstance(result,dict) and 'member' in result:
        member = result['member']
        if isinstance(member,dict) and 'follower' in member:
            followers = member['follower']
            if isinstance(followers,list):
                if followers:
                    for follower in  followers:
                        membersId.append(follower['id'])
            else:
                print("no member following this collection")
            return membersId
        else:
            print("Collection creator(member) not found.")
    else:
        print("collection_creator_follower query error.")
    return False

def query_collection_picker(collectionId, gql_client):
    membersId = []
    collection_picker = '''
    query{
        picks(where:{collection:{id:{equals:"%s"}}, kind:{equals:"read"}, is_active:{equals:true}}){
            member{
                id
            }
        }
    }'''% collectionId
    result = gql_client.execute(gql(collection_picker))
    print(result)
    if isinstance(result,dict) and 'picks' in result:
        picks = result['picks']
        if isinstance(picks,list):
            if picks and 'member' in picks:
                for pick in picks:
                    membersId.append(pick['member']['id'])
            else:
                print("collection pick not exists.")
            return membersId
    print("collection_picker query error")
    return False

def query_collection_comment_member(collectionId, gql_client):
    membersId = []
    collection_comment_member = '''
        query{
            comments(where:{collection:{id:{equals:"%s"}}, is_active:{equals:true}}){
            id
            member{
                id
            }
            }
    }'''% collectionId
    result = gql_client.execute(gql(collection_comment_member))
    print(result)
    if isinstance(result,dict) and 'comments' in result:
        comments = result['comments']
        if isinstance(comments,list):
            if comments and 'members' in comments:
                for comment in comments:
                    membersId.append(comment['member']['id'])
            else:
                print("collection comment not exists.")
            return membersId
    print("collection_comment_member query error")
    return False





  