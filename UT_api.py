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
checklist_api = {}

r = session.post(
url='http://{url}/user/'.format(url= address),
 json= {
    'name': name,
    'password': "test",
    'role' : 'user'
    }
)
status_code = r.status_code

if status_code == 201 :
    checklist_api["get_users"] = 1 
else:
    checklist_api["get_users"] = 0 
     

r = session.put(
url='http://{url}/user/{name}'.format(url = address, name = name),
 json= {
    'name': name,
    'password': "test2",
    }
)
status_code = r.status_code

if status_code == 200 :
    checklist_api["put_users"] =1 
else:
    checklist_api["put_users"] = 0 
     

r = session.delete(
url='http://{url}/user/{name}'.format(url = address, name = name))
status_code = r.status_code

if status_code == 204:
    checklist_api["delete_users"] =1 
else:
    checklist_api["delete_users"] = 0 


r = session.get(
url='http://{url}/predict'.format(url = address),
 params= {
    'designation': "un livre",
    'description': "un livre contenant une histoire avec un resumé des personnages un début une fin et une intrigue",
    }
)

status_code = r.status_code

if status_code == 200:
    checklist_api["prediction"] = 1 
else:
    checklist_api["prediction"] = 0 


#Enregistrement des données dans un fichier logs
output = '''\n
***********************************************
Tests unitaires de l'API \n
'''

with open('logs/units_test.txt', 'a') as file:
    
    file.write(output)
    for i in checklist_api.items():
        file.write((str(i[0]) + " : " + str(i[1]) + "\n"))
    #si l'ensemble des 3 tests précédents sont ok alors on considere la partie entrainement comme fonctionnelle
    file.write("-----------------------------")
    if sum(checklist_api.values()) == 4:
        file.write("\nAPI : OK")
    else:
        file.write("\nAPI : NOT OK") 