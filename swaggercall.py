from ServiceCatalogMS import ServiceCatalogMS

# Create a new ServiceCatalog instance
catalog = ServiceCatalogMS()
#try:
#    catalog.CreateCatalog('https://petstore.swagger.io/v2','Petstore','token')
#except Exception as e:
#    print(e)

#catalog = ServiceCatalogMS()
#catalog.RefreshCatalog('https://petstore.swagger.io/v2','Petstore')
catalog.DeleteVersion('https://petstore.swagger.io/v2',1)
#deleted = catalog.DeleteCatalog('https://petstore.swagger.io/v2','Petstore','token')
#print(deleted)
