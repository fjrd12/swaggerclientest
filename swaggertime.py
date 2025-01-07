from ServiceCatalog_ import ServiceCatalog

try:
    CatalogoServicios = ServiceCatalog('source2')
except ValueError as e:
    print(e)    

#Time tracking tests
print(CatalogoServicios.routes_dict)

try:
    response = CatalogoServicios.ExecuteService('GetCategories', [])
    print(response)
except ValueError as e:
    print(e)
try:
    response = CatalogoServicios.ExecuteService('getUsers', [])
    print(response)
except ValueError as e:
    print(e)

try:
    body = {
            "name": "New Categoria 3",
        }
    response = CatalogoServicios.ExecuteService('createcategory', [], body)
    print(response.content)
except ValueError as e:
    print(e)