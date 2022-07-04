from gql import gql

def query_story_picker(storyId, gql_client):
    membersId = []
    story_picker = '''
    query{
        picks(where:{story:{id:{equals:"%s"}}, kind:{equals:"read"}, objective:{equals:"story"}, is_active:{equals:true}}){
            member{
                id
            }
        }
    }'''% storyId
    result = gql_client.execute(gql(story_picker))
    print(result)
    if isinstance(result,dict) and 'picks' in result:
        picks = result['picks']
        if isinstance(picks,list):
            if picks and 'member' in picks:
                for pick in picks:
                    membersId.append(pick['member']['id'])
            else:
                print("story pick not exists.")
            return membersId
    print("story_picker query error")
    return False


def query_story_comment_member(storyId, gql_client):
    membersId = []
    story_comment_member = '''
    query{
        comments(where:{story:{id:{equals:"%s"}}, is_active:{equals:true}}){
            member{
                id
            }
        }
    }'''% storyId
    result = gql_client.execute(gql(story_comment_member))
    print(result)
    if isinstance(result,dict) and 'comments' in result:
        comments = result['comments']
        if isinstance(comments,list):
            if comments and 'members' in comments:
                for comment in comments:
                    membersId.append(comment['member']['id'])
            else:
                print("story comment not exists.")
            return membersId
    print("story_comment_member query error")
    return False