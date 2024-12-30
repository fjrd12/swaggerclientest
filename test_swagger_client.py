import unittest
from src.ServiceCatalog import ServiceCatalogMS
import urllib3
# Disable InsecureRequestWarning

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TestServiceCatalogMS(unittest.TestCase):
    FirstTime = True
    Catalog = None
    Close = False

    @classmethod
    def setUp(cls):
        #Setup the connection
        if cls.FirstTime:
            try:
                cls.Catalog = ServiceCatalogMS()
                try:
                    cls.Catalog.DeleteCatalog('https://petstore.swagger.io/v2','Petstore','token')
                except Exception as e:
                    pass
            except Exception as e:
                print(e)
                cls.Close = True
        cls.FirstTime =  False    

    def test_00Configcomplete(self):
        #Validate the setup is valid
        self.assertFalse(self.FirstTime)        

    def test_01CreateServiceCatalog(self):
        #Validate if the catalog is successfully created
        e = None
        try:
            self.Catalog.CreateCatalog('https://petstore.swagger.io/v2','Petstore','token')
            print('Catalog creation test pass')
        except Exception as e:
            self.Close = True
            print(f"Exception at Service Catalog creation: {e}")
        self.assertIsNone(e)

    def test_02RefreshServiceCatalog(self):
        #Validate if the catalog generate a version
        e = None
        try:
           self.Catalog.RefreshCatalog('https://petstore.swagger.io/v2','Petstore','token')
           print('Catalog version creation test pass')
        except Exception as e:
            self.Close = True
            print(f"Exception at Service Catalog refresh: {e}")
        self.assertIsNone(e)

    def test_03RetrieveVersionVer1(self):
        #Validate if the catalog generate a version
        e = None
        try:
           self.Catalog.RetrieveVersion('https://petstore.swagger.io/v2',1)
           print('Catalog version 1 retrieve test pass')
        except Exception as e:
            self.Close = True
            print(f"Exception at Service Catalog retrieve: {e}")
        self.assertIsNone(e)

    def test_04RetrieveVersionVer2(self):
        #Validate if the catalog generate a version
        e = None
        try:
           self.Catalog.RetrieveVersion('https://petstore.swagger.io/v2',2)
           print('Catalog version 2 retrieve test pass')
        except Exception as e:
            self.Close = True
            print(f"Exception at Service Catalog refresh: {e}")
        self.assertIsNone(e)

    def test_05ListandGetVersion2(self):
        #Get the catalog and validate the version 2
        e = None
        try:
           catalog = self.Catalog.GetCatalog()
           version2 = next((item for item in catalog if item['source_url'] == 'https://petstore.swagger.io/v2'), None)
           self.assertEqual(2, version2['version'], 'The retrieve version should be 2')
           print('Catalog list and rterieve version 2 test pass')
        except Exception as e:
            self.Close = True
            print(f"Exception at Service Catalog retrieve: {e}")
        self.assertIsNone(e)

    def test_06Delete(self):
        #Execute the delete catalog
        e = None
        try:
           catalog = self.Catalog.DeleteCatalog('https://petstore.swagger.io/v2','Petstore','token')
           print('Catalog deletion test pass')
        except Exception as e:
            self.Close = True
            print(f"Exception at Service Catalog deletion: {e}")
        self.assertIsNone(e)


    def test_07ListandGetVersion2(self):
        #Validate that the catalog is deleted
        e = None
        try:
           catalog = self.Catalog.GetCatalog()
           deletedarray = next((item for item in catalog if item['source_url'] == 'https://petstore.swagger.io/v2'), None)
        except Exception as e:
            print(f"Exception at Service Catalog retrieve: {e}")
        self.Close = True
        self.assertIsNone(deletedarray)

    def tearDown(self):
        #Disconnect the connection
        if self.Catalog is not None and self.Close:
            self.Catalog.CloseConnection()
    
if __name__ == '__main__':
    unittest.main()