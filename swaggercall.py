from ServiceCatalogMS import ServiceCatalogMS

# Create a new ServiceCatalog instance
catalog = ServiceCatalogMS()
catalog.CreateCatalog('https://petstore.swagger.io/v2','Petstore','token')