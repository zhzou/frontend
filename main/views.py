from django.shortcuts import render
import datetime
from django.http import HttpResponseBadRequest, HttpResponse
# Create your views here.
import json, requests,os
import urllib.request
from django.views.decorators.csrf import csrf_exempt
import urllib.request
import urllib
import pymysql, pymongo, random, string

@csrf_exempt
def follow_main(request):
	if request.method == 'POST':
		data = {"username":request.POST.get("username")}
		if not request.POST.get("add_bool") == 'true':
			data["follow"] = False
		req = urllib.request.Request('http://127.0.0.1:8000/follow')
		req.add_header('Content-Type','application/json')
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
		response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
		return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def item_main(request):
	if request.method == 'POST':
		iid = request.POST.get("id")
		add_bool = request.POST.get("add_bool")
		print(add_bool)
		if add_bool == 'true':
			req = urllib.request.Request('http://127.0.0.1:8000/item/'+iid)
			req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
			response = urllib.request.urlopen(req)
			return HttpResponse(str(response.read().decode('utf-8')))
		else:

			#req = urllib.request.Request('http://127.0.0.1:8000/item/'+iid)
			#req.method = 'DELETE'
			#req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
			response = requests.delete('http://127.0.0.1:8000/item/'+iid)
			return HttpResponse(str(response))

@csrf_exempt
def additem_main(request):
	if request.method == 'POST':
		content = request.POST.get("content")
		data = {"content":content}
		
		req = urllib.request.Request('http://127.0.0.1:8000/additem')
		req.add_header('Content-Type','application/json')
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
		response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
		return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def search_main(request):
	if request.method == 'POST':
		limit = request.POST.get("limit")
		timestamp = request.POST.get("timestamp")
		data = {}
		if limit != "" and limit != None:
			data["limit"] = int(limit)
		if timestamp != "" and timestamp != None:
			data["timestamp"] = int(timestamp)
		req = urllib.request.Request('http://127.0.0.1:8000/search')
		req.add_header('Content-Type','application/json')
		response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
		return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def register(request):
	if request.method == 'GET':
		return render(request,'html/register.html')
	if request.method == 'POST':
		username = request.POST.get("username")
		password = request.POST.get("password")
		email = request.POST.get("email")
		data = {"username":username,"password":password,"email":email}
		req = urllib.request.Request('http://127.0.0.1:8000/adduser')
		req.add_header('Content-Type','application/json')
		response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
		r = response.read().decode('utf-8')
		if "OK" in r:
			return render(request,'html/index2.html')
	return HttpResponse("Something Wrong")

@csrf_exempt
def verify(request):
	if request.method == 'GET':
		return render(request,'html/verify.html')
	if request.method == 'POST':
		key = request.POST.get("key")
		email = request.POST.get("email")
		data = {"key":key,"email":email}
		# data2 = {'username':"test_a", 'password': "12345", 'email':"zouzhi96@gmail.com"}
		req = urllib.request.Request('http://127.0.0.1:8000/verify')
		req.add_header('Content-Type','application/json')
		response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
		r = response.read().decode('utf-8')
		if "OK" in r:
			return render(request,'html/index2.html')
	return HttpResponse("Something Wrong")

@csrf_exempt
def index(request):
	session = ""
	try:
		session = request.COOKIES.get('SESSION')
	except:
		pass
		
	if request.method == 'GET':
		if session == "" or session == None:
			return render(request,'html/index2.html')
		elif len(session) == 8:

			#session
			db  = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='356project',
                             charset='utf8mb4',
                             )
			cursor = db.cursor()
			cursor.execute("SELECT username FROM SESSIONS WHERE session=\""+session+"\" \
				")
			username = cursor.fetchone()
			if username == None:
				db.close()
				result_json['error'] = "Invalid account, password or not verified"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			data = {"username":username}
			resp = render(request,'html/main_page.html')
			resp.set_cookie('SESSION',session)
			return resp
	elif request.method == 'POST':
		if request.POST.get('username'):
			username = request.POST.get('username')
			password = request.POST.get('password')			
			db  = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='356project',
                             charset='utf8mb4',
                             )
			cursor = db.cursor()
			cursor.execute("SELECT username FROM ACCOUNTS WHERE username=\""+username+"\" \
				AND password=PASSWORD(\""+password+"\") AND verified=true")
			username = cursor.fetchone()
			if username == None:
				db.close()
				result_json['error'] = "Invalid account, password or not verified"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			else:
				username = username[0]
				result_json = {"status":"OK"}
				session = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
				sql = "INSERT INTO SESSIONS(session, username) VALUES(\""+session+"\",\""+username+"\");"
				try:
					cursor.execute(sql)
					db.commit()
				except:
					db.rollback()
				result_json = {"status":"OK"}
				data = {"username":username}
				response = render(request,'html/main_page.html',data)
				response.set_cookie('SESSION', session)
				return response
				
			
	return render(request,'html/index2.html')
