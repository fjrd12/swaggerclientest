import json
from pyswaggerapiwrap.http_client import HttpClient
from pyswaggerapiwrap import api_filter
from pyswaggerapiwrap.utils import find_swagger_json
from pyswaggerapiwrap.api_filter import APIDataFrameFilter
import re
import requests
import urllib3
import yaml
from pymongo.mongo_client import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ServiceCatalogMS:
    def __init__(self):
        """
        Initialize the ServiceCatalog with a source.
        :param source: The name of the source to load from the catalog.
        """
        # Try to load the configuration from the config.yaml file
        try:
            with open("config.yaml", "r") as file:
                config = yaml.safe_load(file)
            try:
                # Validate the configuration
                if self.ValidConfig(config):
                    mongodb_config = config['mongodb']
                    uri = "mongodb+srv://" + mongodb_config['username'] + ":" + mongodb_config['password']+ "@" +mongodb_config['uri']
                    server_api_version = mongodb_config['server_api_version']
                    tls = mongodb_config['tls']
                    tls_allow_invalid_certificates = mongodb_config['tls_allow_invalid_certificates']
                    # Connect to the MongoDB service
                    client = MongoClient(uri, server_api=ServerApi(server_api_version), tls=tls, tlsAllowInvalidCertificates=tls_allow_invalid_certificates)
                    # Validate the connection
                    try:
                        client.admin.command('ping')
                        print("Succesfully connected to presistent storage.{} ")
                        if mongodb_config['dbname'] in client.list_database_names():
                            self.db = client[mongodb_config['dbname']]
                        else:
                            self.InitDb(client, mongodb_config['dbname'])
                    except errors.PyMongoError as e:
                        print(f"An error occurred: {e}")
            except Exception as e:
                print(e)
        except FileNotFoundError:
            print("The file config.yaml is not found.")
        except yaml.YAMLError as exc:
            print(f"Config.YAML cannot be read: {exc}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def ValidConfig(self, config):
        """
        Validate the configuration.
        :config: The configuration to validate.
        """
        if 'mongodb' not in config:
            raise KeyError("The config mongodb is not in config.yaml.")
        else:
            mongodb_config = config['mongodb']  
        if 'uri' not in mongodb_config:
            raise KeyError("The uri of the connection is not in config.yaml.")
        if 'server_api_version' not in mongodb_config:
            raise KeyError("The server_api_version is not in config.yaml.")
        if 'tls' not in mongodb_config:
            raise KeyError("The tls is not in config.yaml.")
        if 'tls_allow_invalid_certificates' not in mongodb_config:
            raise KeyError("The tls_allow_invalid_certificates is not in config.yaml.")
        if 'username' not in mongodb_config:
            raise KeyError("The username is not in config.yaml.")
        if 'password' not in mongodb_config:
            raise KeyError("The password is not in config.yaml.")
        if  'dbname' not in mongodb_config:
            raise KeyError("The database is not configured in config.yaml.")
        return True
    
    def InitDb(self, client, dbname):
        """
        Initialize the database.
        :param client: The client to connect to the database.
        :param dbname: The name of the database to initialize.
        """
        try:
            db = client[dbname]
            db.create_collection('ServiceCatalog')
            db.create_collection('ServiceCatalogVersion')
            db.create_collection('ServiceRawData')
            self.persistentApi = db
        except Exception as e:
            print(f"Unexpected error: {e}")


    def GetServiceMetadata(self, servicename):
        """
        Get the metadata for a specific service.

        :param servicename: The name of the service to retrieve metadata for.
        :return: The service metadata.
        :raises ValueError: If the service is not found in the catalog.
        """
        service = next((item for item in self.source['services'] if item['name'] == servicename), None)
        if service:
            return service,self.GetServiceVariables(servicename)
        else:
            raise ValueError(f"Service '{servicename}' not found in catalog")
        
    def GetServiceVariables(self, servicename):
        """
        Get the variables for a specific service.
        :param servicename: The name of the service to retrieve variables for.
        :return: A list of variables for the service.
        :raises ValueError: If the service is not found in the catalog.
        """
        TVars = []
        service = next((item for item in self.source['services'] if item['name'] == servicename), None)
        if service:
            for item in service['variables']:
                Varkeypair = { "name": item['name'], "value": item['defaultvalue'] or None, "type": item['type'], "defaultvalue": item['defaultvalue'], "required": item['required'] }
                TVars.append(Varkeypair)
        else:
            raise ValueError(f"Service '{servicename}' not found in catalog")
        return TVars

    def ExecuteService(self, servicename, context=[], body={}) -> any: 
        params= []
        service = next((item for item in self.source['services'] if item['name'] == servicename), None)
        if service: 
            # Get the service method metadata
            try:
                service,variables = self.GetServiceMetadata(servicename)
                variables = self.ClearVars(variables)
                try:
                    params = self.MapVars(variables, context)
                except ValueError as e: 
                    raise ValueError(f"Service '{servicename}' not found in catalog")

                # Prepare the name for the method and route
                method = service['method'].lower()
                route = service['route']
                if method != 'get':
                    route = self.__ReplaceVarsInRoute(service['route'], service['variables'], params)
                    headers = {'api_key': self.api_key}
                    if len(body) > 0:
                        headers['Content-Type'] = 'application/json'
                    response = self.__MakeRequest(method, f"{self.api_url}{route}", headers, json=body)
                else:
                    vars = re.findall(r'\{.*?\}', service['route'])
                    for item in vars:
                        route = service['route'].replace(item,'with_'+ item.replace("{","").replace("}",""))
                    basepath = '/' + service['entity'] + '/'
                    route = route.replace(basepath,"",1)
                    if route.endswith('/'):
                        route = route[:-1] + "_"
                    dmethod = method + '_' + route
                    getobjentity = getattr(self.api_filter, service['entity'])
                    # Transform the array into a dynamic dictionary
                    dynamic_params = {item['name']: item['value'] for item in params}
                    try:
                        response = getattr(getobjentity, dmethod).run(http_client=self.http_client, **dynamic_params)
                        
                    except requests.exceptions.HTTPError as e:
                        error_message = e.response.text if e.response else str(e)
                        raise ValueError(f"HTTP error occurred while calling service '{servicename}': {error_message}")            
            except ValueError as e:
                raise ValueError(f"Service '{servicename}' not found in catalog")
        else:
            raise ValueError(f"Service '{servicename}' not found in catalog")
        return response
    
    def GetRoutes(self):
        """
        Get the routes dictionary.

        :return: The routes dictionary.
        """
        return self.routes_dict

    def ClearVars(self, vars):
        """
        Clear the values of the variables, setting them to their default values.

        :param vars: The list of variables to clear.
        :return: The list of variables with cleared values.
        """
        for item in vars:
            item["value"] = item['defaultvalue'] or None
        return vars

    def MapVars(self, vars, context):
        """
        Map the variables to the context values.

        :param vars: The list of variables to map.
        :param context: The context to map the variables to.
        :return: The list of mapped variables.
        :raises ValueError: If a required variable is not mapped in the context.
        """
        for itemv in vars:
            contextmap = next((item for item in context if item['name'] == itemv['name']), None)
            if contextmap:
                itemv['value'] = contextmap['value']
            elif itemv['required']:
                raise ValueError(f"Variable '{itemv['name']}' is not provided in the context and for method is obligatory")
        return vars
    
    def __MakeRequest(self, method, url, headers=None, params=None, data=None, json=None):
        method = method.upper() 
        try: 
            response = requests.request(method, url, headers=headers, params=params, data=data, json=json)
            response.raise_for_status() 
            return response 
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}") 
        except Exception as err:
            print(f"Other error occurred: {err}")

    def __ReplaceVarsInRoute(self, route, vars, params):
        for var in vars:
            var_value = next((item['value'] for item in params if item['name'] == var['name']), None)
            if var_value is None:
                if not var['defaultvalue'] is None:
                    var_value = var['defaultvalue']
                else:
                    raise ValueError(f"Service requires variable '{var['name']}'")
            route = route.replace('{'+var['name']+'}', str(var_value), 1)
        return route