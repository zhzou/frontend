from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import os, smtplib, random, string, json, hashlib, datetime, time
from email.mime.text import MIMEText
import pymysql, pymongo, pylibmc
from bson.objectid import ObjectId

@csrf_exempt
def search(request):
	result_json = {"status":"error"}
	if request.method == 'POST':
		if 'SESSION' in request.COOKIES:
			session = request.COOKIES['SESSION']
		else:
			result_json["error"] = "log in first"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		
		time_search = int(time.time())
		limit = 25
		following = True
		search_query = None
		search_username = None
		mc = pylibmc.Client(["127.0.0.1"],binary=True,behaviors={"tcp_nodelay": True,"ketama":True})
		if session not in mc:
			result_json["error"] = "log in first"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		else:
			username = mc[session]

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
			if "username" in post_var:
				search_username = post_var["username"]
			if "following" in post_var:
				if post_var["following"] == False:
					following = False
			if "q" in post_var:
				search_query = post_var["q"]



		client = pymongo.MongoClient()
		mdb = client['356project']
		item_collection = mdb['Item']
		#print(type(time_search))
		result_set = None
		if search_username != None:
			if search_query == None:
				result_set = item_collection.find({"timestamp":{ "$lt": time_search}, "username":search_username}).limit(limit)
			else:
				item_collection.create_index([("content","text")])
				
				result_set = item_collection.find({"$text": {"$search": search_query},"timestamp":{ "$lt": time_search}, "username":search_username}).limit(limit)
		elif not following:
			if search_query == None:
				result_set = item_collection.find({"timestamp":{ "$lt": time_search}}).limit(limit)
			else:
				item_collection.create_index([("content","text")])
				result_set = item_collection.find({"$text": {"$search": search_query},"timestamp":{ "$lt": time_search}}).limit(limit)
		else:
			follow_collection = mdb['Follow']
			name_set = follow_collection.find_one({"username":username})
			following_set = name_set["following"]
			if search_query == None:

				result_set = item_collection.find({"timestamp":{ "$lt": time_search}, "username":{"$in":following_set}}).limit(limit)
			else:
				
				item_collection.create_index([("content","text")])
				result_set = item_collection.find({"$text": {"$search": search_query},"timestamp":{ "$lt": time_search}, "username":{"$in":following_set}}).limit(limit)


		if result_set == None:
			client.close()
			result_json['error']= "Invalid id"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		
		items = []
		print("+++++++++++++++++++++")
		print(result_set)
		print("+++++++++++++++++++++")
		for result in result_set:
			result['property']['likes'] = int(result['property']['likes'])
			item_data = {"id":str(result['id']),"username":result['username'],"property":result['property'],"retweeted":int(result['retweeted']),"content":result["content"],"timestamp":result["timestamp"] }
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
				#print("error1")
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
			cursor.execute("SELECT vkey, username, verified FROM ACCOUNTS WHERE email=\""+email+"\"")
			vkey = cursor.fetchone()
			if vkey == None:
				db.close()
				result_json['error'] = "Invalid key or email"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			else:
				username = vkey[1]
				verified = vkey[2]
				if verified == 1:
					db.close()
					result_json['error'] = "Already verified"
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			
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
			client = pymongo.MongoClient()
			mdb = client['356project']
			followCollection = mdb['Follow']
			followCollection.insert_one({"username":username,"following":[],"follower":[],"email":email})
			client.close()

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
			cursor.execute("SELECT vkey,username, verified FROM ACCOUNTS WHERE email=\""+email+"\"")
			vkey = cursor.fetchone()
			if vkey == None:
				db.close()
				result_json['error'] = "Invalid key or email"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			else:
				username = vkey[1]
				verified = vkey[2]
				if verified == 1:
					db.close()
					result_json['error'] = "Already verified"
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			
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
			client = pymongo.MongoClient()
			mdb = client['356project']
			followCollection = mdb['Follow']
			followCollection.insert_one({"username":username,"following":[],"follower":[],"email":email})
			client.close()
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
				db.close()
				username = username[0]
				session = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))
				mc = pylibmc.Client(["127.0.0.1"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
				mc[session] = username
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
			mc = pylibmc.Client(["127.0.0.1"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
			del mc[session]
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
			mc = pylibmc.Client(["127.0.0.1"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
			if session in mc:
				username = mc[session]
			else:
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			client = pymongo.MongoClient()
			mdb = client['356project']
			item_collection = mdb['Item']
			
			utime = int(time.time())
			#item_id = str(item_collection.count())
			item_id = str(ObjectId())
			new_Item = {"username":username,"id":item_id, "property":{"likes":int(0)},"retweeted":int(0),"content":content, "timestamp":utime}
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
                item_data = {"id":result['id'],"username":result['username'],"property":result['property'],"retweeted":result['retweeted'],"content":result["content"],"timestamp":result["timestamp"]}
                result_json = {"item":item_data}
                result_json["status"] = "OK"
                client.close()
                return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
        if request.method == 'DELETE':
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
                #item_data = {"id":result['id'],"username":result['username'],"property":result['property'],"retweeted":result['retweeted'],"content":result["content"],"timestamp":result["timestamp"]}
                item_collection.delete_many({"id":iid})
                #result_json = {"item":item_data}
                result_json["status"] = "OK"
                client.close()
                return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")


@csrf_exempt
def user_followers(request,username):
	result_json = {"status":"error"}
	if request.method == 'GET' or request.method == 'POST':
		limit = 50
		try:
			post_var = json.loads(request.body.decode('utf8'))
			if "limit" in post_var:
				limit = int(post_var["limit"])
				if limit > 200:
					limit = 200
				elif limit < 0:
					limit = 50
		except:
			pass
		client = pymongo.MongoClient()
		mdb = client['356project']
		follow_collection = mdb['Follow']
		result_set = follow_collection.find_one({"username":username})
		if result_set == None:
			client.close()
			result_json['error']= "Invalid username"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		result_json["users"] = result_set["follower"]
		if len(result_json["users"]) > limit:
			result_json["users"] = result_json["users"][0:limit]
		result_json["status"] = "OK"
		return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

@csrf_exempt
def user_following(request,username):
	result_json = {"status":"error"}
	if request.method == 'GET' or request.method == 'POST':
		limit = 50
		try:
			post_var = json.loads(request.body.decode('utf8'))
			if "limit" in post_var:
				limit = int(post_var["limit"])
				if limit > 200:
					limit = 200
				elif limit < 0:
					limit = 50
		except:
			pass
		client = pymongo.MongoClient()
		mdb = client['356project']
		follow_collection = mdb['Follow']
		result_set = follow_collection.find_one({"username":username})
		if result_set == None:
			client.close()
			result_json['error']= "Invalid username"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		result_json["users"] = result_set["following"]
		if len(result_json["users"]) > limit:
			result_json["users"] = result_json["users"][0:limit]
		result_json["status"] = "OK"
		return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")


@csrf_exempt
def user(request,username):
	result_json = {"status":"error"}
	if request.method == 'GET':
		client = pymongo.MongoClient()
		mdb = client['356project']
		follow_collection = mdb['Follow']
		result_set = follow_collection.find_one({"username":username})
		if result_set == None:
			client.close()
			result_json['error']= "Invalid username"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		user_set = {}
		user_set["email"] = result_set["email"]
		user_set["followers"] = result_set["follower"]
		user_set["following"] = result_set["following"]
		result_json["user"] = user_set
		result_json["status"] = "OK"
		return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		
@csrf_exempt
def follow(request):
	result_json = {"status":"error"}

	if request.method == 'POST':
		if request.META.get('CONTENT_TYPE') == 'application/json':
			if 'SESSION' in request.COOKIES:
				session = request.COOKIES['SESSION']
			else:
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			post_json  = json.loads(request.body.decode('utf8'))
			follow_boolean = True
			if "follow" in post_json:
				follow_boolean = post_json["follow"]
			username = post_json["username"]
			
			#current username == follower
			
			mc = pylibmc.Client(["127.0.0.1"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
			if session in mc:
				follower = mc[session]
			else:
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			
			#check username exist
			client = pymongo.MongoClient()
			mdb = client['356project']
			follow_collection = mdb["Follow"]
			result = follow_collection.find_one({"username":username})
			if result == None:
				result_json["error"] = "Invalid username"
				client.close()
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")


			if username == follower:
				result_json["error"] = "Cannot follow yourself"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			
			###################
			
			result = follow_collection.find_one({"username":username,"follower":{"$in":[follower]}})
			
			if follow_boolean:
				if result == None:
					follow_collection.update_one({"username":username},{"$push":{"follower":follower}})
					follow_collection.update_one({"username":follower},{"$push":{"following":username}})
					result_json["status"] = "OK"
					client.close()
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
				else:
					client.close()
					result_json["error"] = "already followed"
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			else:
				if result == None:
					client.close()
					result_json["error"] = "You did not follow he/she"
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
				else:
					r = follow_collection.update(
						{"username":username},{'$pull':{"follower":follower}}
						)
					r = follow_collection.update(
						{"username":follower},{'$pull':{"following":username}}
						)
					result_json["status"] = "OK"
					
					client.close()
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

def like(request,iid):
	result_json = {"status":"error"}
	if request.method == 'POST':
		if 'SESSION' in request.COOKIES:
				session = request.COOKIES['SESSION']
		else:
			result_json["error"] = "log in first"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		post_json  = json.loads(request.body.decode('utf8'))
		like_boolean = True
		if "like" in post_json:
			like_boolean = post_json["like"]
		client = pymongo.MongoClient()
		mdb = client['356project']
		item_collection = mdb["Item"]
		likes = item_collection.find_one({"id":iid})
		if likes == None:
			result_json["error"] = "Item not exist"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		likes = likes["property"]["likes"]

		if like_boolean:
			likes += 1
			r = item_collection.update({"id":iid},{"property":{"likes":likes}})
			result_json["status"] = "OK"
			client.close()
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		else:
			if likes > 0:
				likes -= 1
				r = item_collection.update({"id":iid},{"property":{"likes":likes}})
				result_json["status"] = "OK"
			client.close()
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")



			
