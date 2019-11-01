import json
import requests

api_url_base = "https://gft6ixgrq7.execute-api.us-east-2.amazonaws.com/default/PulseLambda-NeptuneLambdaFunction-QI9VKCO1VXK1"
headers = {
      "Content-type": "application/json"
}
body = json.dumps({'vertex': [{'id': 'user-111', 'label': 'user1', 'type': 'user', 'text': 'New User1'}], 'edge': [], 'addOnly': 1})

#def get_chart():
response = requests.get(api_url_base, headers=headers, data=body)

if response.status_code == 200:
    print(response.content)
else:
    print('[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url_base))
