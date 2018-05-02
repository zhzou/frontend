from django.shortcuts import render
import datetime
from django.http import HttpResponseBadRequest, HttpResponse
# Create your views here.
import json, requests,os
import urllib.request
from django.views.decorators.csrf import csrf_exempt
import urllib.request
import urllib
import pymysql, pymongo, random, string, pylibmc, hashlib

@csrf_exempt
def upload(request):
	if request.method == 'POST' and request.FILES['myfile']:
		myfile = request.FILES['myfile']
		print(myfile.content_type)
		content = b''
		for chunk in myfile.chunks():
			content += chunk
		print(content)
		req = urllib.request.Request('http://130.245.169.158/addmedia')
		req.add_header('Content-Type',myfile.content_type)
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
		response = urllib.request.urlopen(req, content)
		return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def getmedia(request):
	iid = request.POST.get("item")
	req = urllib.request.Request('http://130.245.169.158/media/'+iid)
	req.add_header('Content-Type','application/json')
	req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
	response = urllib.request.urlopen(req)
	return HttpResponse(response.read(),content_type="image/jpeg")

@csrf_exempt
def unlike_main(request):
	iid = request.POST.get("item")
	data = {"like":False}
	req = urllib.request.Request('http://130.245.169.158/item/'+iid+'/like')
	req.add_header('Content-Type','application/json')
	req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
	response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
	return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def like_main(request):
	iid = request.POST.get("item")
	data = {"like":True}
	req = urllib.request.Request('http://130.245.169.158/item/'+iid+'/like')
	req.add_header('Content-Type','application/json')
	req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
	response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
	return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt	
def follower_main(request):
	if request.method == 'POST':
		req = urllib.request.Request('http://130.245.169.158/user/'+request.POST.get("username")+'/followers')
		req.add_header('Content-Type','application/json')
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
		response = urllib.request.urlopen(req)
		return HttpResponse(str(response.read().decode('utf-8')))
def following_main(request):
	if request.method == 'POST':
		req = urllib.request.Request('http://130.245.169.158/user/'+request.POST.get("username")+'/following')
		req.add_header('Content-Type','application/json')
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
		response = urllib.request.urlopen(req)
		return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def user_main(request):
	if request.method == 'POST':
		req = urllib.request.Request('http://130.245.169.158/user/'+request.POST.get("username"))
		req.add_header('Content-Type','application/json')
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
		response = urllib.request.urlopen(req)
		return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def follow_main(request):
	if request.method == 'POST':
		data = {"username":request.POST.get("username")}
		if not request.POST.get("add_bool") == 'true':
			data["follow"] = False
		req = urllib.request.Request('http://130.245.169.158/follow')
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
			req = urllib.request.Request('http://130.245.169.158/item/'+iid)
			req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
			response = urllib.request.urlopen(req)
			return HttpResponse(str(response.read().decode('utf-8')))
		else:

			#req = urllib.request.Request('http://130.245.169.158/item/'+iid)
			#req.method = 'DELETE'
			#req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
			response = requests.delete('http://130.245.169.158/item/'+iid)
			return HttpResponse(str(response))

@csrf_exempt
def additem_main(request):
	if request.method == 'POST':
		content = request.POST.get("content")
		data = {"content":content}
		
		req = urllib.request.Request('http://130.245.169.158/additem')
		req.add_header('Content-Type','application/json')
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
		response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
		return HttpResponse(str(response.read().decode('utf-8')))

@csrf_exempt
def search_main(request):
	if request.method == 'POST':
		limit = request.POST.get("limit")
		timestamp = request.POST.get("timestamp")
		following = request.POST.get("following")
		q = request.POST.get("q")
		username = request.POST.get("username")
		data = {}
		if limit != "" and limit != None:
			data["limit"] = int(limit)
		if timestamp != "" and timestamp != None:
			data["timestamp"] = int(timestamp)
		req = urllib.request.Request('http://130.245.169.158/search')
		if following == "true":
			data["following"] = True
		else:
			data["following"] = False
		if q != "" and q != None:
			data["q"] = q
		if username != "" and username != None:
			data["username"] = username
			print("here"+username)
		req = urllib.request.Request('http://130.245.169.158/search')
		req.add_header('Content-Type','application/json')
		req.add_header('Cookie', 'SESSION='+request.COOKIES.get('SESSION'))
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
		req = urllib.request.Request('http://130.245.169.158/adduser')
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
		req = urllib.request.Request('http://130.245.169.158/verify')
		req.add_header('Content-Type','application/json')
		response = urllib.request.urlopen(req, json.dumps(data).encode('utf8'))
		r = response.read().decode('utf-8')
		if "OK" in r:
			return render(request,'html/index2.html')
	return HttpResponse("Something Wrong")

@csrf_exempt
def index(request):
	result_json = {"status":"error"}
	session = ""
	try:
		session = request.COOKIES.get('SESSION')
	except:
		pass
	if request.method == 'GET':
		if session == "" or session == None:
			return render(request,'html/index2.html')
		elif len(session) == 8:
			mc = pylibmc.Client(["127.0.0.1"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
			#session
			if session not in mc:
				result_json['error'] = "Invalid account, password or not verified"
				return render(request,'html/index2.html')
			username = mc[session]
			data = {"username":username}
			resp = render(request,'html/main_page.html')
			resp.set_cookie('SESSION',session)
			return resp
	elif request.method == 'POST':
		if request.POST.get('username'):
			username = request.POST.get('username')
			password = request.POST.get('password')			
			client = pymongo.MongoClient("192.168.1.9",27017)
			mdb2 = client["356project"]
			account_coll = mdb2["Account"]
			acc = account_coll.find_one({"username":username,"password":hashlib.sha256(password.encode("utf-8")).hexdigest()
				,"verified":True})
			if acc == None:
				result_json['error'] = "Invalid account, password or not verified"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			
			else:
				result_json = {"status":"OK"}
				session = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
				mc = pylibmc.Client(["127.0.0.1"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
				mc[session] = username
				result_json = {"status":"OK"}
				data = {"username":username}
				response = render(request,'html/main_page.html',data)
				response.set_cookie('SESSION', session)
				return response
	return render(request,'html/index2.html')

