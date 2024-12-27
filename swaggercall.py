from ServiceCatalogMS import ServiceCatalogMS

# Create a new ServiceCatalog instance
catalog = ServiceCatalogMS()
try:
    catalog.CreateCatalog('https://petstore.swagger.io/v2','Petstore','token')
except Exception as e:
    print(e)