import os
import requests
import json

def get_root_collection():
    response = requests.get(
        'http://sevahub.es/rootCollections',
        headers={
            'Accept': 'text/plain',
            'X-authorization': '<token>'
            },
    )
    rns = json.loads(response.content)
    for rn in rns:
        print(rn)

def login():
    response = requests.post(
        'http://sevahub.es/login',
        headers={
            'X-authorization': '<token>',
            'Accept': 'text/plain'
        },
        data={
            'email': 'angel.goni@upm.es',
            'password' : 'horse8ports3',
            },
    )
    return response.content

def create_collection(token):
    response = requests.post(
        'http://sevahub.es/submit',
        headers={'X-authorization': token,
                'Accept': 'text/plain'},
        data={
            'id': "test",
            'version' : '1',
            'name' : "test",
            'rootCollections' : 'http://sevahub.es/public/Test/1',
            'overwrite_merge' : '3',
            "description" : "test"})
    print(response.status_code)
    print(response.content)

def upload_originals(token):
    response = requests.post(
        'http://sevahub.es/submit',
        headers={'X-authorization': token,
                'Accept': 'text/plain'},
        files={'files': open(os.path.join(s_dir,fn),'rb')},
        data={
            'id': name,
            'version' : '1',
            'name' : name,
            'rootCollections' : 'http://sevahub.es/user/SEVAhub/Tessy/Tessy_collection/1',
            'overwrite_merge' : '3',
            "description" : name})
    print(response.status_code)
    print(response.content)

def upload(token):
    s_dir = "uploads"
    for fn in os.listdir(s_dir):
        name = fn.split(".")[0]
        print(f'Uploading: {name}')
        response = requests.post(
            'http://sevahub.es/submit',
            headers={'X-authorization': token,
                    'Accept': 'text/plain'},
            files={'files': open(os.path.join(s_dir,fn),'rb')},
            data={
                'id': name,
                'version' : '1',
                'name' : name,
                'rootCollections' : 'http://sevahub.es/user/SEVAhub/Tessy/Tessy_collection/1',
                'overwrite_merge' : '3',
                "description" : name})
        print(response.status_code)
        print(response.content)

def move(token,name):
    response = requests.post(
        f'http://sevahub.es/user/SEVAhub/{name}/{name}_collection/1/addToCollection',
        headers={
            'X-authorization': token,
            'Accept': 'text/plain'
        },
        data={
            'collections': 'Cannonical',
            },
    )
    print(response.status_code)
    print(response.content)

def remove(token):
    s_dir = "uploads"
    for fn in os.listdir(s_dir):
        name = fn.split(".")[0]
        print(f'Removing: {name}')
        response = requests.get(
            f'http://sevahub.es/user/SEVAhub/{name}/{name}_collection/1/remove',
            headers={
                'Accept': 'text/plain',
                'X-authorization': token
                },
        )

        print(response.status_code)
        print(response.content)

def make_public(token,collection):
    response = requests.post(
        f'http://sevahub.es/user/SEVAhub/{collection}/{collection}_collection/1/makePublic',
        headers={
            'X-authorization': token,
            'Accept': 'text/plain'
        },  
        data={
            "id" : collection,
            "version" : "1",
            "tabState" : "new"}
    )
    print(response.status_code)
    print(response.content)
    print("\n\n")


if __name__ == "__main__":
    x_token = login()
    create_collection(x_token)
    exit()
    remove(x_token)
    upload(x_token)