from ServiceCatalog_ import ServiceCatalog
from bson import ObjectId
#Get the catalog of services from a source
try:
    CatalogoServicios = ServiceCatalog('source1')
except ValueError as e:
    print(e)    

for i in range(1, 5):
    try:
        response = CatalogoServicios.ExecuteService('getPetById', [{ "name": "petId", "value": i }])
        print(response)
    except ValueError as e:
        print(e)

try:
    response = CatalogoServicios.ExecuteService('deletePetById', [{ "name": "petId", "value": '1' }])
    print(response)
except ValueError as e:
    print(e)

try:
    response = CatalogoServicios.ExecuteService('deletePetById', [{ "name": "petId", "value": '2' }])
    print(response)
except ValueError as e:
    print(e)

try:
    body = {
        'id': 1,
        'category': {
            'id': 1,
            'name': 'Pomerania'
        },
        'name': 'Pepe',
        'photoUrls': ['https://plus.unsplash.com/premium_photo-1734203007981-0cfdae356886?q=80&w=2835&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'],
        'tags': [
            {
                'id': 1,
                'name': 'small'
            }
        ],
        'status': 'available'
    }
    response = CatalogoServicios.ExecuteService('createPet', [], body)
    print(response.content)
except ValueError as e:
    print(e)

try:
    body = {
        'id': 2,
        'category': {
            'id': 2,
            'name': 'Poodle'
        },
        'name': 'Thormenta',
        'photoUrls': ['https://plus.unsplash.com/premium_photo-1734203007981-0cfdae356886?q=80&w=2835&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'],
        'tags': [
            {
                'id': 1,
                'name': 'small'
            }
        ],
        'status': 'available'
    }
    response = CatalogoServicios.ExecuteService('createPet', [], body)
    print(response.content)
except ValueError as e:
    print(e)

