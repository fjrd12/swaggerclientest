from fastapi import FastAPI, HTTPException,Query
from pydantic import BaseModel
from src.ServiceCatalog import ServiceCatalogMS
from contextlib import asynccontextmanager
from typing import Annotated
import json
from bson import ObjectId


app = FastAPI()

@app.post("/CreateCatalog")
async def CreateCatalog(source_url: str, Catalogname: str, authkey: str | None ):
    service_catalog_ms = ServiceCatalogMS()
    try:
        service_catalog_ms.CreateCatalog(source_url, Catalogname, authkey)
        service_catalog_ms.CloseConnection()
        return {"message": "Catalog created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/RefreshCatalog")
async def refresh_catalog(source_url: str, Catalogname: str, authkey: str | None ):
    service_catalog_ms = ServiceCatalogMS()
    try:
        service_catalog_ms.RefreshCatalog(source_url, Catalogname, authkey)
        service_catalog_ms.CloseConnection()
        return {"message": "Catalog refreshed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        arraylist = []
        service_catalog_ms = ServiceCatalogMS()
        Response = service_catalog_ms.GetCatalog()   
        for item in Response:
            del item['ObjectId']
            arraylist.append(item)
        service_catalog_ms.CloseConnection()
        return arraylist
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/DeleteCatalog")
async def delete_catalog(source_url: str, Catalogname: str, authkey: str | None ):
    try:
        service_catalog_ms = ServiceCatalogMS()
        service_catalog_ms.DeleteCatalog(source_url, Catalogname, authkey)
        service_catalog_ms.CloseConnection()
        return {"message": f"Catalog deleted{source_url}"}        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
