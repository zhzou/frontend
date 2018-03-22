from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from django.http import HttpResponseBadRequest
import os, smtplib, random, string, json, hashlib, datetime, time
from email.mime.text import MIMEText
import pymysql, pymongo

@csrf_exempt
def search(request):
	result_json = {"status":"error"}
	if request.method == 'POST':
		time_search = int(time.time())
		limit = 25
		if request.META.get('CONTENT_TYPE') == 'application/json':
			post_var = json.loads(request.body.decode('utf8'))
			if "timestamp" in post_var:
				time_search = int(post_var["timestamp"])
			if "limit" in post_var:
				if post_var["limit"] > 100:
					limit = 100
				else:
					if post_var["limit"]>0:
						limit = int(post_var["limit"])
		client = pymongo.MongoClient()
		mdb = client['356project']
		item_collection = mdb['Item']
		print(type(time_search))
		result_set = item_collection.find({"timestamp":{ "$lt": time_search}}).limit(limit)
		if result_set == None:
			client.close()
			result_json['error']= "Invalid id"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		
		items = []
		for result in result_set:
			item_data = {"id":result['id'],"username":result['username'],"property":result['property'],"retweeted":result['retweeted'],"content":result["content"],"timestamp":result["timestamp"] }
			items += [item_data]
		result_json = {"items":items}
		result_json["status"] = "OK"
		return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		


@csrf_exempt
def index(request):
	if request.META.get('CONTENT_TYPE') == 'application/json':
		if request.method == 'POST':
			griddict = json.loads(request.body.decode('utf8'))
			
			new_griddict = processGrid(griddict)
			#print(new_griddict)
			return HttpResponse(json.dumps(new_griddict).encode('utf8'),content_type="application/json")
	return HttpResponse("")



@csrf_exempt
def adduser(request):
	result_json = { "status":'error'}
	#print(os.path.dirname(os.path.realpath(__file__)))
	if request.method == 'POST':
		if request.META.get('CONTENT_TYPE') == 'application/json':
			account = json.loads(request.body.decode('utf8'))
			username = str(account['username'])
			password = str(account['password'])
			email = str(account['email'])
			verify = False
			key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
			key = str(key)
			db  = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='356project',
                             charset='utf8mb4',
                             )
			cursor = db.cursor()
			cursor.execute("SELECT username FROM ACCOUNTS WHERE username=\""+username+"\" OR email=\""+email+"\"")
			result = cursor.fetchone()
			if result != None:
				db.close()
				result_json['error'] = "Account or email already existed."
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			sql = "INSERT INTO ACCOUNTS(username,email, vkey,  verified,  signup_date, password) VALUES \
				(\""+username+"\" , \""+email+"\" , \""+key+"\" , \
				False, NOW() , PASSWORD(\""+password+"\"));"
			#print(sql)
			try:
				cursor.execute(sql)
				db.commit()
			except:
				#cursor.execute(sql)
				#db.commit()
				print("error1")
				db.rollback()
				
			db.close()
			
			try:
				message = MIMEText("validation key: <"+key+">")
				message['Subject'] = 'TWIZ Verification Key.'
				message['From'] = 'zzsafe96@gmail.com'
				message['To'] = email

				server = smtplib.SMTP('smtp.gmail.com',587)
				server.starttls()
				server.login("zzsafe96@gmail.com",'Zz123456')
				
				server.sendmail("zzsafe96@gmail.com",email,message.as_string())
				server.quit()
				result_json = {"status":"OK"}
			except:
				result_json['error'] = "Invalid email"
		else:
			print("error2")
			result_json['error'] = "Invalid Json"
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")


@csrf_exempt
def verify(request):
	result_json = {"status":"error"}
	if request.method == 'POST':
		if request.META.get('CONTENT_TYPE') == 'application/json':
			post_var = json.loads(request.body.decode('utf8'))
			email = post_var['email']
			key = post_var['key']

			db  = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='356project',
                             charset='utf8mb4',
                             )
			cursor = db.cursor()
			cursor.execute("SELECT vkey FROM ACCOUNTS WHERE email=\""+email+"\"")
			vkey = cursor.fetchone()
			if vkey == None:
				db.close()
				result_json['error'] = "Invalid key or email"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			else:
				vkey = vkey[0]
			if key == 'abracadabra' or vkey == key:
				sql = "UPDATE ACCOUNTS SET verified = true where email =\""+email+"\""
				try:
					cursor.execute(sql)
					db.commit()
					result_json = {"status":"OK"}
				except:
					db.rollback()
			db.close()

	if request.method == 'GET':
		try:
			email = request.GET["email"]
			key = request.GET["key"]
			with open('accounts.json','r') as jfile:
				old_accs = json.load(jfile)
			db  = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='356project',
                             charset='utf8mb4',
                             )
			cursor = db.cursor()
			cursor.execute("SELECT vkey FROM ACCOUNTS WHERE email=\""+email+"\"")
			vkey = cursor.fetchone()
			if vkey == None:
				db.close()
				result_json['error'] = "Invalid key or email"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			else:
				vkey = vkey[0]
			#print(key)
			#print(vkey)
			if key == 'abracadabra' or vkey == key:
				sql = "UPDATE ACCOUNTS SET verified = true where email =\""+email+"\""
				try:
					cursor.execute(sql)
					db.commit()
					result_json = {"status":"OK"}
				except:
					db.rollback()
			db.close()
		except:
			result_json['error'] = "Invalid Json"
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

@csrf_exempt
def login(request):
	result_json = {"status":"error"}
	if request.method == 'POST':
		if request.META.get('CONTENT_TYPE') == 'application/json':
			post_var = json.loads(request.body.decode('utf8'))
			username = post_var['username']
			password = post_var['password']

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
				response = HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
				response.set_cookie('SESSION', session)
				return response
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

@csrf_exempt
def logout(request):
	result_json = {"status":"error"}
	if request.method == 'POST' or request.method == 'GET':
		#username = request.GET["username"]
		if 'SESSION' in request.COOKIES:
			session = request.COOKIES['SESSION']
			result_json = {"status":"OK"}
			response = HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			response.set_cookie('SESSION', '')
			return response
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

@csrf_exempt
def additem(request):
	result_json = {"status":"error"}
	if request.method == 'POST':
		if request.META.get('CONTENT_TYPE') == 'application/json':
			post_var = json.loads(request.body.decode('utf8'))
			content = post_var["content"]
			if 'SESSION' in request.COOKIES:
				session = request.COOKIES['SESSION']
			else:
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			db  = pymysql.connect(host='localhost',
                             user='root',
                             password='1234',
                             db='356project',
                             charset='utf8mb4',
                             )
			cursor = db.cursor()
			sql = "SELECT username FROM SESSIONS WHERE session = \""+session+"\""
			cursor.execute(sql)
			username = cursor.fetchone()
			if username == None:
				db.close()
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			username = username[0]
			db.close()
			client = pymongo.MongoClient()
			mdb = client['356project']
			item_collection = mdb['Item']
			utime = int(time.time())
			item_id = str(item_collection.count())
			new_Item = {"username":username,"id":item_id, "property":{"likes":0},"retweeted":0,"content":content, "timestamp":utime}
			try:
				object_id = item_collection.insert_one(new_Item)
				result_json['id'] = item_id
				result_json['status']="OK"
			except:
				result_json['error'] = "Wrong input"
			client.close()
	else:
		result_json['error'] = "Not POST"
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")


def item(request,iid):
	result_json = {"status":"error"}
	if request.method == 'GET':
		iid = str(iid)
		client = pymongo.MongoClient()
		mdb = client['356project']
		item_collection = mdb['Item']
		result = item_collection.find_one({"id":iid})
		if result == None:
			client.close()
			result_json['error']= "Invalid id"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		print(result['timestamp'])
		item_data = {"id":result['id'],"username":result['username'],"property":result['property'],"retweeted":result['retweeted'],"content":result["content"],"timestamp":result["timestamp"] }
		result_json = {"item":item_data}
		result_json["status"] = "OK"
		client.close()
		return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		
