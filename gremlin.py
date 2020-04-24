import json
import requests
#1
api_url_base = "https://gft6ixgrq7.execute-api.us-east-2.amazonaws.com/default/PulseLambda-NeptuneLambdaFunction-QI9VKCO1VXK1"

headers = {
      "Content-type": "application/json"
}

###
 ## --- node type --- ##
 # id: node_id      format: [type]-[tb_id]
 # label: tb_id
 # type: tb_name    user/project/shcategory/organization/team/stakeholder
 # text: name
 ## --- node type --- ##
 #
 ## --- edge type --- ##
 # from: from_node_id
 # id: edge_id
 # label: edge_type     related/included
 # text: edge_name      ""
 # to: to_node_id
 # weight: line weight  default 5
 ## --- edge type --- ##
###
# test

# body = json.dumps({'vertex': [{'id': 'user-111', 'label': 'user1', 'type': 'user', 'text': 'New User1'}], 'edge': [], 'addOnly': 1})

# response = requests.post(api_url_base, headers=headers, data=body)

# if response.status_code == 200:
#     print(response.content)
# else:
#     print('[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url_base))

def addVertex(data):
    body = json.dumps({'vertex': data, 'edge': [], 'addOnly': 1, 'method': 'add'})

    response = requests.post(api_url_base, headers=headers, data=body)

    if response.status_code == 200:
        return response.content
    else:
        return '[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url_base)

def deleteVertex(id):
    body = json.dumps({'method': 'delete', 'deleteVertex': 1, 'vertexId': id})

    response = requests.post(api_url_base, headers=headers, data=body)

    if response.status_code == 200:
        return response.content
    else:
        return '[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url_base)
