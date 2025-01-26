from pymongo.mongo_client import MongoClient
from pymongo import errors
from pymongo.server_api import ServerApi
from pyswaggerapiwrap.http_client import HttpClient
from pyswaggerapiwrap.utils import find_swagger_json
from pyswaggerapiwrap.api_filter import APIDataFrameFilter
import re
import requests
import urllib3
import yaml

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
            with open("./config/config.yaml", "r") as file:
                config = yaml.safe_load(file)
            # Validate the configuration
            if self.ValidConfig(config):
                mongodb_config = config['mongodb']                    
                connectionstring = "mongodb://" + mongodb_config['uri'] + ":" + mongodb_config['port']
                self.client = MongoClient(connectionstring)
                # Validate the connection
                try:
                    self.client.admin.command('ping')
                    print(f"Succesfully connected to presistent storage {mongodb_config['dbname']}")
                    if mongodb_config['dbname'] in self.client.list_database_names():
                        self.database = self.client[mongodb_config['dbname']]
                    else:
                        self.InitDb(self.client, mongodb_config['dbname'])
                except errors.PyMongoError as e:
                    print(f"An error occurred: {e}")
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
        :return: If the validation is correct
        """
        if 'mongodb' not in config:
            raise KeyError("The config mongodb is not in config.yaml.")
            
        required_keys = ['uri','server_api_version','tls','tls_allow_invalid_certificates', 'username', 'password', 'dbname']
        for key in required_keys:
            if key not in config['mongodb']:
                raise KeyError(f"The {key} is not in config.yaml.")
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
            self.database = db
        except Exception as e:
            print(f"Unexpected error: {e}")

    def CompleteBodySchemaServices(self,Catalogentry):
        """
        Once you have a Catalogentry extend the body schema for all the services in the catalog entry
        :param Catalogentry: 
        """
        definitions = []
        items = []
        paths = Catalogentry['jsonraw']['paths']

        if 'definitions' in Catalogentry['jsonraw']:
            definitions = Catalogentry['jsonraw']['definitions']

        for item in Catalogentry['services']:
            listvals = list(item)
            ItemServiceSchema = None
            itemdict = {
                       'index':  listvals[0],
                       'entity': listvals[1],
                       'path':   listvals[2],
                       'method': listvals[3],
                       'parameters': listvals[4],
                       'payload':    ServiceCatalogMS.CompleteBodySchema(item,Catalogentry,definitions, None, True),
                       'summary': paths[item[2]][str(item[3]).lower()]['summary']
                       }
            items.append(itemdict)
        
        Catalogentry['services'] = items
            
        return Catalogentry


    @staticmethod
    def CompleteBodySchema(ServiceEntry,Catalogentry,definitions, schema,firstime):
        """
        Parse the body schema definition
        :param ServiceEntry: Entry to be populated
        :param paths associated with the service
        """
        BodySchema = []
        required = []
        paths = Catalogentry['jsonraw']['paths']
        parameters = paths[ServiceEntry[2]][str(ServiceEntry[3]).lower()]['parameters']
        servicepayload = next((item for item in parameters if item['in'] == 'body'), None)
        if servicepayload:
            if 'schema' in servicepayload:
                if 'type' in servicepayload['schema']:
                    if servicepayload['schema']['type'] == 'array':
                        #Array in the root node definition
                        BodySchema = ServiceCatalogMS.ParseArray(servicepayload['schema']['items'], definitions, required, False, True)    
                else:                
                    #Schema for the component
                    BodySchema = ServiceCatalogMS.ParseSchema(BodySchema, servicepayload['schema']['$ref'],definitions, required, False)
            else:
                #Array of components
                BodySchema = ServiceCatalogMS.ParseArray(servicepayload['schema']['items'], definitions, required, False, False)                    
        return BodySchema

    
    @staticmethod
    def ParseSchema(BodySchema, schemaname,definitions, required,firsttime):
        fields = []
        schema_parts = schemaname.split('/')
        schema_components = definitions[schema_parts[2]]
        if firsttime and 'required' in schema_components:
            required = schema_components['required']
        for item in schema_components['properties'].keys():
            field = {}
            field['name'] = item 
            if '$ref' in schema_components['properties'][item]:
                field['type'] = 'dict'
                #If the schema has schemas inside
                field['components'] = ServiceCatalogMS.ParseSchema(BodySchema,schema_components['properties'][item]['$ref'],definitions,required,False)
            else:
                #If is a single type is added
                field['type'] = schema_components['properties'][item]['type']
                field['required'] = item in required
                #If the component has an array nested go for the array definition
                if schema_components['properties'][item]['type'] == 'array':
                    field['items'] = []
                    #If it has an array process the content of the array
                    field['items'] = ServiceCatalogMS.ParseArray(schema_components['properties'][item]['items'],definitions,required, firsttime, False)
            fields.append(field)
        return fields
    
    @staticmethod
    def ParseArray(items, definitions, required, firstime, firstimearray):
        fields = []
        #If it is a simple schema it process it
        if isinstance(items,dict) and not firstimearray:
            field = {}
            if '$ref' in items:
                field['components'] = []
                field['components'] = ServiceCatalogMS.ParseSchema(field['components'] , items['$ref'],definitions, required, True)
            else:    
                field['type'] = items['type']
            fields.append(field)
        else:
            #If the array has different components its iterate for each component
            for item in items:
                field = {}
                #If it is an array process as an
                if not items['$ref']:
                  field['type'] = item['type']
                  field['required'] = item in required
                  field['items'] = []
                  field['items'] = ServiceCatalogMS.ParseArray(item['items'],definitions,required,False)
                else:
                    #If it is a schema process like that
                    subfield = {}
                    subfield['type'] = 'dict'
                    subfield['components'] = []
                    subfield['components'] = ServiceCatalogMS.ParseSchema(subfield['components'],items['$ref'] ,definitions, required, False)
                    field['type'] = 'array'
                    field['items'] = []
                    field['items'].append(subfield)        
                        
                fields.append(field)
        return fields
    
    def CreateCatalog(self, source_url,Catalogname,authkey=None):
        """
        Import the catalog from a source and create a version for it
        :param source_url: The source to import the catalog from.
        """
        #Validate if there is any service associated with the source url 
        collection = self.database["ServiceCatalog"]
        documents = None
        collectionv = self.database["ServiceCatalogVersion"]
        documents = collection.find_one({ "$or": [ { "source_url":  source_url}, { "catalogname": Catalogname } ] })
        if not documents:
            try:
                # Get the routes dictionary
                http_client = HttpClient(base_url=source_url, auth_token=authkey)
                #Construct the version of the catalog
                routes_dict = http_client.get_routes_df(swagger_route="/swagger.json")
                Catalogentry = { 
                                 "catalogname":  Catalogname, 
                                 "source_url": source_url, 
                                 "authkey": authkey, 
                                 "version": 1,
                                 "jsonraw": find_swagger_json(source_url),
                                 "services": routes_dict.to_records().tolist()
                                }
                Catalogentry = self.CompleteBodySchemaServices(Catalogentry)
                record = collectionv.insert_one(Catalogentry)
                record_id = record.inserted_id
                #Get the relationship with the version and set the current version
                Catalogentry['version_id'] = record_id
                record = collection.insert_one(Catalogentry)
            except ValueError as e:
                raise ValueError(f"Source '{source_url}' not found in catalog") 
        else:
            raise ValueError(f"Catalog '{Catalogname}' already exists in the database")

    def DeleteCatalog(self, source_url,Catalogname,authkey=None):
        """
        delete the catalog from a source name or url.
        :param source_url: The source url to delete.
        :param Catalogname: The source catalogname to delete.
        """
        #Get the catalog
        collection = self.database["ServiceCatalog"]
        documents = None
        documents = collection.find_one({ "$or": [ { "source_url":  source_url}, { "catalogname": Catalogname } ] })
        if not documents:
            raise ValueError(f"Catalog '{Catalogname}' not found in the database")
        else:
            #Delete the catalog
            documents = collection.delete_many({ "_id":  documents['_id'] })
            #Delete the versions associated with the catalog
            collection = self.database["ServiceCatalogVersion"]
            documents = collection.delete_many({ "source_url": source_url })
        return f"Catalog '{Catalogname}' deleted"
    
    def DeleteVersion(self, source_url, Version):
        """
        Delete a version from a source version.
        :param source_url: The source to import the catalog from.
        :param Version: Version deletion.
        """
        #Get the catalog
        collection = self.database["ServiceCatalog"]
        documents = None
        documents = collection.find_one( { "source_url":  source_url, "version": Version })
        catalogname = documents['catalogname']
        if not documents:
            raise ValueError(f"Catalog {documents['catalogname']}, version {Version} not found")
        else:
            #Delete the catalog
            documents = collection.delete_many({ "_id":  documents['_id'] })
        return f"Catalog {catalogname} deleted"
    
    def GetCatalog(self):
        """
        Get catalog list
        """
        #Get the catalog
        collection = self.database["ServiceCatalog"]
        documents_raw = []
        documents = None
        documents = collection.find({})
        for item in documents:
            item['_id'] = str(item['_id'])
            item['version_id'] = str(item['version_id'])
            documents_raw.append(item)
        return documents_raw

    def GetCatalogServices(self, source_url):
        """
        Get catalog services
        """
        #Get the catalog
        collection = self.database["ServiceCatalog"]
        documents_raw = []
        document = None
        document = collection.find_one({ "source_url":  source_url}, { "services": 1 , "authkey": 1, "version": 1})
        document['_id'] = str(document['_id'])
        return document
    
    def RetrieveVersion(self,source_url,version):
        """
        Get a version of the service catalog
        :param source_url: The source to i-mport the catalog from.
        """
        #Validate if there is any service associated with the source url 
        collectionv = self.database["ServiceCatalogVersion"]
        collection = self.database["ServiceCatalog"]
        document = None
        document  = collection.find_one({ "$or": [ { "source_url":  source_url} ] })
        if document:
            query = {
                        "$or": [
                            {"source_url": source_url}
                        ],
                        "$and": [
                            {"version": version}
                        ]
                    }
            documentsv  = collectionv.find( query)        
            try:
                itemv = documentsv[0]
                Catalogentry = { 
                            "catalogname":  itemv['catalogname'], 
                            "source_url": itemv['source_url'], 
                            "authkey": itemv['authkey'], 
                            "version": itemv['version'],
                            "jsonraw": itemv['jsonraw'],
                            "services": itemv['services']
                            }
                #Get the relationship with the version and set the current version
                Catalogentry['version_id'] = itemv['_id']
                collection = self.database["ServiceCatalog"]
                record = collection.insert_one(Catalogentry)
                #Delete the previous version
                self.DeleteVersion(source_url,document['version'])
                return 'Succesfully retrieved version'
            except ValueError as e:
                raise ValueError(f"The version {version} does not exists for the catalog {document['catalogname']}") 
        else:
            raise ValueError(f"Catalog '{itemv['catalogname']}' does not exists in the database")
        
    def RefreshCatalog(self, source_url=None,Catalogname=None,authkey=None):
        """
        Refresh the catalog from a source.
        :param source_url: The source to import the catalog from.
        """
        #Validate if there is any service associated with the source url 
        collectionv = self.database["ServiceCatalogVersion"]
        collection = self.database["ServiceCatalog"]
        documents = None
        documents  = collection.find_one({ "$or": [ { "source_url":  source_url}, { "catalogname": Catalogname } ] })
        if documents:
            documentsv  = collectionv.find({ "$or": [ { "source_url":  source_url}, { "catalogname": Catalogname } ] }).sort({"_id":-1}).limit(1)        
            try:
                itemv = documentsv[0]
                # Get the routes dictionary
                http_client = HttpClient(base_url=source_url, auth_token=documents['authkey'])
                #Construct the version of the catalog
                routes_dict = http_client.get_routes_df(swagger_route="/swagger.json")
                Catalogentry = { 
                                 "catalogname":  Catalogname, 
                                 "source_url": source_url, 
                                 "authkey": documents['authkey'], 
                                 "version": itemv['version'] + 1,
                                 "jsonraw": find_swagger_json(source_url),
                                 "services": routes_dict.to_records().tolist()
                                }
                Catalogentry = self.CompleteBodySchemaServices(Catalogentry)
                record = collectionv.insert_one(Catalogentry)
                record_id = record.inserted_id
                #Get the relationship with the version and set the current version
                Catalogentry['version_id'] = record_id
                collection = self.database["ServiceCatalog"]
                record = collection.insert_one(Catalogentry)
                #Delete the previous version
                self.DeleteVersion(source_url,documents['version'])

            except ValueError as e:
                raise ValueError(f"Source '{source_url}' not found in catalog") 
        else:
            raise ValueError(f"Catalog '{Catalogname}' does not exists in the database")

    def CloseConnection(self):
        """
        Close the connection to the database.
        """
        self.client.close()

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
    
    def ExecuteServiceMS(self, serviceurl, path, method, context=any, payload=any) -> any: 
        """
        Execute the method related of servicename.
        :servicename: The name of the service to retrieve variables for.
        :context: The context to map the variables to.
        :payload: The body to send in the request.
        :return: A list of variables for the service.
        :raises ValueError: If the service is not found in the catalog.
        """
        params= []
        GetCatalogService = self.GetCatalogServices(serviceurl)

        if 'services' in GetCatalogService:
            service = next((item for item in GetCatalogService['services'] if item['path'] == path and item['method'] == method), None)
            if service: 
            # Get the service method metadata
                variables = service['parameters']
                try:
                    if len(variables) > 0:
                        params = self.MapVars(variables, context)
                except ValueError as e: 
                    raise ValueError(f"Exception at map parameters '{e}'")
                # Prepare the name for the method and route
                method = service['method'].lower()
                route = path
                route = self.__ReplaceVarsInRoute(route, variables, params)
                headers = {'api_key': GetCatalogService['authkey']}
                headers['Content-Type'] = 'application/json'
                try:
                    response = self.__MakeRequest(method, f"{serviceurl}{route}", headers, json=payload)
                except Exception as e:
                    raise ValueError(e)     
            else:
                raise ValueError(f"Service '{path}' not found in catalog")
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
            if itemv['in'] != 'body':
                for item in context:
                    if itemv['name'] == item['name']:
                        match itemv['param_type']:
                            case 'integer':
                                itemv['value'] = int(item['value'])
                            case 'string':    
                                itemv['value'] = str(item['value'])
                            case _:
                                itemv['value'] = item['value']
                contextmap = itemv
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
            raise ValueError(f"HTTP error occurred: {http_err}")
        except Exception as err:
            raise ValueError(f"Other error occurred: {err}")

    def __ReplaceVarsInRoute(self, route, vars, params):
        first = True
        for var in vars:

            if var['in'] != 'body':
                var_value = next((item['value'] for item in params if item['name'] == var['name']), None)
                if var_value is None:
                    if not var['defaultvalue'] is None:
                        var_value = var['defaultvalue']
                    else:
                        raise ValueError(f"Service requires variable '{var['name']}'")
                if var['in'] == 'query':
                    if first:
                        route = route + '?' + var['name'] + '=' + str(var_value)
                    else:
                        route = route + '&' + var['name'] + '=' + str(var_value)
                    first = False
                else:
                    route = route.replace('{'+var['name']+'}', str(var_value), 1)
            
        return route
