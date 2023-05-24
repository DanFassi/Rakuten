import requests
import json

address= "localhost:8000"

login_data =  {'name':'dan', 'password':'amwa'}

session = requests.Session()
session.auth = ("dan", "amwa")
auth = session.post('http://' + address)
#response = session.post(url + "token", login_data)
#response = json.loads(response.content.decode('utf-8'))
#session.headers.update({"Authorization": 'Bearer ' + response['access_token']})

name = "testeur"

def test_new_user():
    r = session.post(
    url='http://{url}/user/'.format(url= address),
    json= {
        'name': name,
        'password': "test",
        'role' : 'user'
        }
    )
    status_code = r.status_code
    assert status_code == 201 

def test_change_user():
    r = session.put(
    url='http://{url}/user/{name}'.format(url = address, name = name),
    json= {
        'name': name,
        'password': "test2",
        }
    )
    status_code = r.status_code
    assert status_code == 200 

     
def test_delete_user():
    r = session.delete(
    url='http://{url}/user/{name}'.format(url = address, name = name))
    status_code = r.status_code

    assert status_code == 204


def test_predict():
    r = session.get(
    url='http://{url}/predict'.format(url = address),
    params= {
        'designation': "un livre",
        'description': "un livre contenant une histoire avec un resumé des personnages un début une fin et une intrigue",
        }
    )

    status_code = r.status_code

    assert status_code == 200
