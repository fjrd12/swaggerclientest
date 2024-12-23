from pyswaggerapiwrap.http_client import HttpClient
from pyswaggerapiwrap.api_filter import APIDataFrameFilter
import pandas as pd 
import numpy as np0
import json
import inspect
import requests

def make_request(method, url, headers=None, params=None, data=None, json=None):
    method = method.upper() 
    try: 
        response = requests.request(method, url, headers=headers, params=params, data=data, json=json)
        response.raise_for_status() 
        return response 
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}") 
    except Exception as err:
        print(f"Other error occurred: {err}")


ENDPOINT = "https://petstore.swagger.io/v2"
AUTH_TOKEN = "special-key"

http_client = HttpClient(base_url=ENDPOINT, auth_token=AUTH_TOKEN)
routes_dict = http_client.get_routes_df(swagger_route="/swagger.json")
jsonapi = routes_dict.to_json()
parsed = json.loads(jsonapi)
print("==================Service metadata===================")
print(json.dumps(parsed, indent=4))
print("==================Routes of swagger==================")
print(routes_dict)
api_filter = APIDataFrameFilter(routes_dict)
out = api_filter.filter(method="GET")

print("==================All get methods====================")
print(out)
print("==================Get Methods applied================")
data = api_filter.store.get_inventory.run(http_client)
print(data)
print("==================Get methods applied================")
data1 = api_filter.pet.get_with_petId.run(http_client=http_client, petId=1)
print(data1)

api_filter = APIDataFrameFilter(routes_dict)
out = api_filter.filter(method="POST")
print("==================All post methods====================")
print(out)
#print("==================Post Method applied=================")
#bodyvar = {"id": 9999, "username": 'fjrd12', "firstName": "Francisco", "lastName": "Rodriguez", "email": "fjrd12@gmail.com", "password": "test", "phone": "test", "userStatus": 1}
#json_string = json.dumps(bodyvar)
#signature = inspect.signature(api_filter.user.post.run)
#data2 = api_filter.user.post.run(http_client=http_client, body = json_string)
#data3 = api_filter.user.get_with_username.run(http_client=http_client, username="fjrd12")
#print(data3)
print("=================Post methods applied by request================")
row = routes_dict.loc[routes_dict['route'] == '/store/inventory']
method = row.method.values[0]
route = row.route.values[0]
response = make_request(method, f"{ENDPOINT}{route}")
print(response.json())

row = routes_dict.loc[routes_dict['route'] == '/pet']
method = row.method.values[0]
route = row.route.values[0]
body = {
    'id': 1635,
    'category': {
        'id': 0,
        'name': 'Pomerania'
    },
    'name': 'Pepe',
    'photoUrls': ['https://plus.unsplash.com/premium_photo-1734203007981-0cfdae356886?q=80&w=2835&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'],
    'tags': [
        {
            'id': 0,
            'name': 'small'
        }
    ],
    'status': 'available'
}
response = make_request(method, f"{ENDPOINT}{route}", headers={'Content-Type': 'application/json'}, json=body)
print(response.json())

print("==================Get methods applied================")
data1 = api_filter.pet.get_with_petId.run(http_client=http_client, petId=1635)
print(data1)


row = routes_dict.loc[routes_dict['route'] == '/pet/findByStatus']
parameters = row.parameters.values[0]
method = row.method.values[0]
route = row.route.values[0]