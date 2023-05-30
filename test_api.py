import requests
import json
import os

address= "localhost:8000"

session = requests.Session()
session.auth = (os.getenv("TEST_LOG"), os.getenv("TEST_PW"))
auth = session.post('http://' + address)

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
    url='http://{url}/admin/{name}'.format(url = address, name = name),
    json= {
        'name': name,
        'password': "test2",
        'role': "user"}
    )
    status_code = r.status_code
    assert status_code == 200 

     
def test_delete_user():
    r = session.delete(
    url='http://{url}/admin/{name}'.format(url = address, name = name))
    status_code = r.status_code

    assert status_code == 204


def test_predict():
    r = session.post(
    url='http://{url}/predict'.format(url = address),
    json= {
        'designation': "un livre",
        'description': "un livre contenant une histoire avec un resumé des personnages un début une fin et une intrigue",
        }
    )

    status_code = r.status_code

    assert status_code == 200
