from gql import gql

def query_comment_creator(commentId, gql_client):
    membersId = []
    comment_creator = '''
    query{
        comment(where:{id:"%s"}){
            member{
                id
            }
        }
    }'''% commentId
    result = gql_client.execute(gql(comment_creator))
    print(result)
    if isinstance(result,dict) and 'comment' in result:
        comment = result['comment']
        if isinstance(comment,dict) and 'member' in comment:
            membersId.append(comment['member']['id'])
            return membersId
        else:
            print("comment creator(member) not found.")
    else:
        print("comment not found.")
    return False

def query_comment_picker(commentId, gql_client):
    membersId = []
    comment_picker = '''
    query{
        picks(where:{comment:{id:{equals:"%s"}}, kind:{equals:"read"}, objective:{equals:"comment"}, is_active:{equals:true}}){
            member{
                id
            }
        }
    }'''% commentId
    result = gql_client.execute(gql(comment_picker))
    print(result)
    if isinstance(result,dict) and 'picks' in result:
        picks = result['picks']
        if isinstance(picks,list):
            if picks and 'member' in picks:
                for pick in picks:
                    membersId.append(pick['member']['id'])
            else:
                print("comment pick not exists.")
            return membersId
    print("comment_picker query error")
    return False


def query_comment_member(commentId, gql_client):
    membersId = []
    comment_member = '''
    query{
        comments(where:{root:{id:{equals:"%s"}}, is_active:{equals:true}}){
            member{
            id
            }
        }
    }'''% commentId
    result = gql_client.execute(gql(comment_member))
    print(result)
    if isinstance(result,dict) and 'comments' in result:
        comments = result['comments']
        if isinstance(comments,list):
            if comments and 'members' in comments:
                for comment in comments:
                    membersId.append(comment['member']['id'])
            else:
                print("comment in comment not exists.")
            return membersId
    print("comment_member query error")
    return False