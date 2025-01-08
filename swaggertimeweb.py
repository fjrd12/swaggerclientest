from src.ServiceCatalog import ServiceCatalogMS
service_catalog_ms = ServiceCatalogMS()
source_url = 'http://127.0.0.1:5000'
Catalogname = 'Timetracking'
authkey = '123'
try:
    service_catalog_ms.CreateCatalog(source_url, Catalogname, authkey)
    service_catalog_ms.CloseConnection()
except Exception as e:
    print(e)


# try:
#     CatalogoServicios = ServiceCatalog('source2')
# except ValueError as e:
#     print(e)    

# #Time tracking tests
# print(CatalogoServicios.routes_dict)

# try:
#     response = CatalogoServicios.ExecuteService('GetCategories', [])
#     print(response)
# except ValueError as e:
#     print(e)
# try:
#     response = CatalogoServicios.ExecuteService('getUsers', [])
#     print(response)
# except ValueError as e:
#     print(e)

# try:
#     body = {
#             "name": "New Categoria 3",
#         }
#     response = CatalogoServicios.ExecuteService('createcategory', [], body)
#     print(response.content)
# except ValueError as e:
#     print(e)