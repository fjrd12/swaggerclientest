from fastapi import FastAPI, HTTPException
from src.ServiceCatalog import ServiceCatalogMS
import uvicorn
import json
import yaml
from typing import Any, List,Optional
from pydantic import BaseModel,Json

class Service(BaseModel):
    source_url: str
    path: str
    method: str
    context: Optional[List[Any]] = None
    payload: Any = None

class Reply(BaseModel):
    reply: Any
    status_code: int
    errormessage: str

app = FastAPI()

@app.post("/CreateCatalog")
def CreateCatalog(source_url: str, Catalogname: str, authkey: str | None ):
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
def execute_method(service: Service, response_model=Reply):
    """
    Ejecuta un método del servicio catalogado.

    :param service: Objeto que contiene los detalles del servicio a ejecutar.
    :param response_model: Modelo de respuesta que se devolverá.
    :return: Respuesta del servicio ejecutado.
    """
    service_catalog_ms = ServiceCatalogMS()
    try:
        response = service_catalog_ms.ExecuteServiceMS(service.source_url, service.path,service.method, service.context,service.payload) 
        service_catalog_ms.CloseConnection()
        response_model = Reply(reply=response.content, status_code=200, errormessage='')
        return response_model
    except Exception as e:
        response_model = Reply(reply='', status_code=500, errormessage=str(e))
        raise HTTPException(status_code=500, detail=response_model.model_dump_json())
    
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
