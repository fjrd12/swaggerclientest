from fastapi import FastAPI, HTTPException
from src.ServiceCatalog import ServiceCatalogMS
import uvicorn
import json
import yaml

app = FastAPI()

@app.post("/CreateCatalog")
async def CreateCatalog(source_url: str, Catalogname: str, authkey: str | None ):
    service_catalog_ms = ServiceCatalogMS()
    try:
        service_catalog_ms.CreateCatalog(source_url, Catalogname, authkey)
        service_catalog_ms.CloseConnection()
        return {"message": "Catalog created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/RefreshCatalog")
async def refresh_catalog(source_url: str, Catalogname: str, authkey: str | None ):
    service_catalog_ms = ServiceCatalogMS()
    try:
        service_catalog_ms.RefreshCatalog(source_url, Catalogname, authkey)
        service_catalog_ms.CloseConnection()
        return {"message": "Catalog refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/RetrieveVersion")
async def retrieve_version(source_url: str, version: int ):
    
    try:        
        service_catalog_ms = ServiceCatalogMS()
        Response = service_catalog_ms.RetrieveVersion(source_url,version)
        service_catalog_ms.CloseConnection()            
        return {"message": f"Retrieved Version {version}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/GetCatalog")
async def get_catalog():
    try:
        Response = []
        service_catalog_ms = ServiceCatalogMS()
        CatalogObjects = service_catalog_ms.GetCatalog()
        for item in CatalogObjects:
            Response.append(item)   
        service_catalog_ms.CloseConnection()
        if len(Response) == 0:
            raise HTTPException(status_code=400, detail='No Catalogs found')
        return Response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/DeleteCatalog")
async def delete_catalog(source_url: str, Catalogname: str, authkey: str | None ):
    try:
        service_catalog_ms = ServiceCatalogMS()
        service_catalog_ms.DeleteCatalog(source_url, Catalogname, authkey)
        service_catalog_ms.CloseConnection()
        return {"message": f"Catalog deleted{source_url}"}        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/GetMethods")
async def get_methods(source_url: str):
    try:
        service_catalog_ms = ServiceCatalogMS()
        Response = {}
        Response = service_catalog_ms.GetCatalogServices(source_url)
        service_catalog_ms.CloseConnection()
        return Response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/ExecuteMethod")
def execute_method(source_url: str, path: str, context: str):
    service_catalog_ms = ServiceCatalogMS()
    try:
        context_parsed = json.loads(context)
        response = service_catalog_ms.ExecuteServiceMS(source_url, path, context_parsed) 
        service_catalog_ms.CloseConnection()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    with open("./config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
        try:
            # Validate the configuration
            if config['port'] is not None:                    
                port = config['port']
                uvicorn.run(app, host="0.0.0.0", port=port)
        except Exception as e:
            print("Error in reading the config file")
    
