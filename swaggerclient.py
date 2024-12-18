from pyswaggerapiwrap.http_client import HttpClient
from pyswaggerapiwrap.api_filter import APIDataFrameFilter
import pandas as pd 
import numpy as np0
import json

ENDPOINT = "https://petstore.swagger.io/v2"
AUTH_TOKEN = "special-key"

http_client = HttpClient(base_url=ENDPOINT, auth_token=AUTH_TOKEN)
routes_dict = http_client.get_routes_df(swagger_route="/swagger.json")
jsonapi = routes_dict.to_json()
print(jsonapi)
parsed = json.loads(jsonapi)
print(json.dumps(parsed, indent=4))
print(routes_dict)
api_filter = APIDataFrameFilter(routes_dict)
out = api_filter.filter(method="GET")
print(out)

data = api_filter.store.get_inventory.run(http_client)
print(data)

data1 = api_filter.pet.get_with_petId.run(http_client=http_client, petId=1)
print(data1)