# swaggerclientest
This is a dockerized service to add source URLs to a have a catalog of microservices that expose Open API 2.0 swwager definition

## Features
- It lets you create for a given url an entry of service available for be executed.
- Allow to get the methods associated to a microservice published in the catalog. With the enough information to be invoked from a client.
- For a given URL delete a Microservice from the catalog.
- Refresh the catalog. Allow to synchronize to pull a new version of the catalog.
- The catalog can be versioned if there is any previous version you need to retrieve you can get it.
- Execute a method base in a context that is a dictionary. For the moment the microservice only receive paramaters for DELETE and GET methods. For the POST is not implemented a context mapping

## Requirements 
- Python version 3.11

## Install
0.- Clone the repository
1.- Create an environment
```sh
pip install virtualenv
```
2.- Install virtual enviroment:
```sh
python -m venv <virtual-environment-name>
```
3.- Install/Upgrade pip
```sh
python -m pip install --upgrade pip
```

4.-Activate the environment for Linux/Unix
```sh
source env/bin/activate
```
Windows:
```sh
.\env\Scripts\activate
```
6.- Install requirements.
```sh
pip install -r requirements.txt
```
7.- Configure the port of the service and the database user and password configuration
```sh
mongodb:
  uri: "mongo:27017"
  server_api_version: "1"
  password: "root"
  username: "rjon2457"
  dbname: "ServiceCatalog"
  tls: true
  tls_allow_invalid_certificates: true
port: 8450
```
8.- Then you can run the command:
```sh
docker compose up
```
