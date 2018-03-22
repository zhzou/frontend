import json
import urllib.request
import requests
import urllib
from PIL import Image
import requests
from io import BytesIO
import base64
from PIL import Image
import urllib.request
#data = { 'grid': ['O','O',' ','X',' ',' ',' ','X','X'],'winner':' '}

# URL = "http://127.0.0.1:8000/adduser"

# data2 = {'username':"test_a", 'password': "12345", 'email':"zouzhi96@gmail.com"}
# req = urllib.request.Request('http://127.0.0.1:8000/adduser/')
# req.add_header('Content-Type','application/json')

# response = urllib.request.urlopen(req, json.dumps(data2).encode('utf8'))


###########################
# URL = "https://upload.wikimedia.org/wikipedia/commons/2/27/Sus_scrofa_domesticus%2C_miniature_pig%2C_juvenile.jpg"
# with urllib.request.urlopen(URL) as url:
#     f = BytesIO(url.read())

# img = Image.open(f)
# imgs = base64.b64encode(img.tobytes())

# data2 = {'filename':'test1','contents': 'asdsad'}
# req = urllib.request.Request('http://127.0.0.1:8000/ttt/deposit/')
# req.add_header('Content-Type','application/json')

# response = urllib.request.urlopen(req, json.dumps(data2).encode('utf8'))


###########################

# #print(response.read().decode('utf-8'))

data2 = {'email':'zouzhi96@gmail.com','key':'YXC58QNL'}
req = urllib.request.Request('http://127.0.0.1:8000/verify/')
req.add_header('Content-Type','application/json')

response = urllib.request.urlopen(req, json.dumps(data2).encode('utf8'))


#test login
# data = {'username':'a','password':'1234'}
# req = urllib.request.Request('http://127.0.0.1:8000/ttt/login/')
# req.add_header('Content-Type','application/json')
# response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))

# print(response.read().decode('utf-8'))
# print(response.cookies)

# headers = {'content-type': 'application/json'}
# data = {'username':'a','password':'1234'}
# r = requests.post('http://127.0.0.1:8000/ttt/login/', data=json.dumps(data), headers=headers)
# for cookie in r.cookies:
# 	print(r.cookies['SESSION'])