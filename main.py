from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.ServiceCatalog import ServiceCatalogMS
from contextlib import asynccontextmanager
import urllib3
# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

service_catalog_ms = None

# Initialize the ServiceCatalogMS instance
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the ServiceCatalogMS instance
    service_catalog_ms = ServiceCatalogMS()
    yield
    # Close the connection
    service_catalog_ms.CloseConnection()
    
app = FastAPI(lifespan=lifespan)

# @app.post("/CreateCatalog")
# async def create_catalog(url_map: UrlMap):
#     try:
#         service_catalog_ms.CreateCatalog(url_map.source_url, url_map.catalog_name, url_map.auth_key)
#         return {"message": "Catalog created"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/DeleteCatalog")
# async def delete_catalog(url_map: UrlMap):
#     try:
#         service_catalog_ms.DeleteCatalog(url_map.source_url, url_map.catalog_name, url_map.auth_key)
#         return {"message": "Catalog deleted"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/GetCatalog")
# async def get_catalog():
#     try:
#         catalog = service_catalog_ms.GetCatalog()
#         return {"catalog": catalog}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/RetrieveVersion")
# async def retrieve_version(url_map: UrlMap, version: int):
#     try:
#         catalog_entry = service_catalog_ms.RetrieveVersion(url_map.source_url, url_map.catalog_name, version, url_map.auth_key)
#         return {"catalog_entry": catalog_entry}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/RefreshCatalog")
# async def refresh_catalog(url_map: UrlMap):
#     try:
#         service_catalog_ms.RefreshCatalog(url_map.source_url, url_map.catalog_name, url_map.auth_key)
#         return {"message": "Catalog refreshed"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/CloseConnection")
# async def close_connection():
#     try:
#         service_catalog_ms.CloseConnection()
#         return {"message": "Connection closed"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))