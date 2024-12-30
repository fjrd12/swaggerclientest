from ServiceCatalogMS import ServiceCatalogMS
# Create a new ServiceCatalog instance
catalog = ServiceCatalogMS()
#try:
#    catalog.CreateCatalog('https://petstore.swagger.io/v2','Petstore','token')
#except Exception as e:
#    print(e)
#catalog.RefreshCatalog('https://petstore.swagger.io/v2','Petstore')
#catalog.RefreshCatalog('https://petstore.swagger.io/v2','Petstore')
#catalog.RefreshCatalog('https://petstore.swagger.io/v2','Petstore')
#catalog.RefreshCatalog('https://petstore.swagger.io/v2','Petstore')
#catalog.RefreshCatalog('https://petstore.swagger.io/v2','Petstore')
#catalog.RetrieveVersion('https://petstore.swagger.io/v2',11)
# deleted = catalog.DeleteCatalog('https://petstore.swagger.io/v2','Petstore','token')
# print(deleted)
catalogcontent = catalog.GetCatalog()
for item in catalogcontent:
   print(item)
catalog.CloseConnection()

