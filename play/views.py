from django.shortcuts import render
from django.http import HttpResponseBadRequest, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import os, smtplib, random, string, json, hashlib, datetime, time
from email.mime.text import MIMEText
import pymysql, pymongo, pylibmc
from bson.objectid import ObjectId
from cassandra.cluster import Cluster

#mc = pylibmc.Client(["192.168.1.16"],binary=True,behaviors={"tcp_nodelay": True,"ketama":True})
client = pymongo.MongoClient('192.168.1.14',27017)
mdb = client['356project']
client2 = pymongo.MongoClient('192.168.1.9',27017)
mdb2 = client2['356project']
cluster = Cluster(['192.168.1.24'])
session = cluster.connect("project356")

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
		mc = pylibmc.Client(["192.168.1.16"],binary=True,behaviors={"tcp_nodelay": True,"ketama":True})
		print(mc[session])
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
			rank = "interest"
			if "rank" in post_var:
				rank = post_var["rank"]
			parent = None
			if "parent" in post_var:
				parent = post_var["parent"]
			replies = True
			if "replies" in post_var:
				replies = post_var["replies"]
			hasMedia = False
			if "hasMedia" in post_var:
				hasMedia = post_var["hasMedia"]


		#client = pymongo.MongoClient('192.168.1.14',27017)
		#mdb = client['356project']
		item_collection = mdb['Item']
		#print(type(time_search))
		result_set = None
		#########################################################
		#new approach
		search_dic = {"timestamp":{ "$lt": time_search}}
		if search_username != None:
			search_dic ["username"] = search_username
		elif following:
			follow_collection = mdb['Follow']
			name_set = follow_collection.find_one({"username":username})
			following_set = name_set["following"]
			search_dic ["username"] = {"$in":following_set}
		if search_query != None:
			search_dic ["$text"] = {"$search": search_query}
		if not replies:
			search_dic ["childType"] = {"$ne" : "reply"}
		if parent != None:
			search_dic ["parent"] = parent
		if hasMedia:
			search_dic ["media"] = {"$ne":None}


		##########################################################
		# if search_username != None:
		# 	if search_query == None:
		# 		result_set = item_collection.find({"timestamp":{ "$lt": time_search}, "username":search_username}).limit(limit)
		# 	else:
		# 		item_collection.create_index([("content","text")])
				
		# 		result_set = item_collection.find({"$text": {"$search": search_query},"timestamp":{ "$lt": time_search}, "username":search_username}).limit(limit)
		# elif not following:
		# 	if search_query == None:
		# 		result_set = item_collection.find({"timestamp":{ "$lt": time_search}}).limit(limit)
		# 	else:
		# 		item_collection.create_index([("content","text")])
		# 		result_set = item_collection.find({"$text": {"$search": search_query},"timestamp":{ "$lt": time_search}}).limit(limit)
		# else:
		# 	follow_collection = mdb['Follow']
		# 	name_set = follow_collection.find_one({"username":username})
		# 	following_set = name_set["following"]
		# 	if search_query == None:

		# 		result_set = item_collection.find({"timestamp":{ "$lt": time_search}, "username":{"$in":following_set}}).limit(limit)
		# 	else:
				
		# 		item_collection.create_index([("content","text")])
		# 		result_set = item_collection.find({"$text": {"$search": search_query},"timestamp":{ "$lt": time_search}, "username":{"$in":following_set}}).limit(limit)
		if rank == "interest":
			result_set = item_collection.find(search_dic).sort([("property.likes",-1)]).limit(limit)
		elif rank == "time":
			result_set = item_collection.find(search_dic).sort([("timestamp",-1)]).limit(limit)

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
def additem(request):
	result_json = {"status":"error"}
	if request.method == 'POST':
		if request.META.get('CONTENT_TYPE') == 'application/json':
			post_var = json.loads(request.body.decode('utf8'))
			content = post_var["content"]
			childType = None
			parent = ""
			media = []
			if "childType" in post_var:
				if post_var["childType"]!= None:
					childType = post_var["childType"]
			if "parent" in post_var:
				if post_var["parent"]!= None:
					childType = post_var["parent"]
			if "media" in post_var:
				if post_var["media"]!= None:
					childType = post_var["media"]
			if 'SESSION' in request.COOKIES:
				session = request.COOKIES['SESSION']
			else:
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			mc = pylibmc.Client(["192.168.1.16"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
			if session in mc:
				username = mc[session]
			else:
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			#client = pymongo.MongoClient('192.168.1.9',27017)
			#mdb = client['356project']
			item_collection = mdb2['Item']
			utime = int(time.time())
			#item_id = str(item_collection.count())
			item_id = str(ObjectId())
			new_Item = {"username":username,"id":item_id, "property":{"likes":int(0)},"retweeted":int(0),"content":content, "timestamp":utime,"childType":childType,"parent":parent,"media":media}
			try:
				object_id = item_collection.insert_one(new_Item)
				result_json['id'] = item_id
				result_json['status']="OK"
			except:
				result_json['error'] = "Wrong input"
			#client.close()
	else:
		result_json['error'] = "Not POST"
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

def item(request,iid):
        result_json = {"status":"error"}
        if request.method == 'GET':
                iid = str(iid)
                #Wclient = pymongo.MongoClient('192.168.1.14',27017)
                #mdb = client['356project']
                item_collection = mdb['Item']
                result = item_collection.find_one({"id":iid})
                if result == None:
                        #client.close()
                        result_json['error']= "Invalid id"
                        return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
                print(result['timestamp'])
                item_data = {"id":result['id'],"username":result['username'],"property":result['property'],
                "retweeted":result['retweeted'],"content":result["content"],"timestamp":result["timestamp"],
                "childType":result["childType"],"parent":result['parent'],"media":result['media']}
                result_json = {"item":item_data}
                result_json["status"] = "OK"
                #client.close()
                return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
        if request.method == 'DELETE':
                iid = str(iid)
                #client = pymongo.MongoClient('192.168.1.14',27017)
                #mdb = client['356project']
                item_collection = mdb['Item']
                result = item_collection.find_one({"id":iid})
                if result == None:
                        #client.close()
                        result_json['error']= "Invalid id"
                        return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
                print(result['timestamp'])
                #item_data = {"id":result['id'],"username":result['username'],"property":result['property'],"retweeted":result['retweeted'],"content":result["content"],"timestamp":result["timestamp"]}
                item_collection.delete_many({"id":iid})
                #result_json = {"item":item_data}
                result_json["status"] = "OK"
                #client.close()
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
		#client = pymongo.MongoClient('192.168.1.14',27017)
		#mdb = client['356project']
		follow_collection = mdb['Follow']
		result_set = follow_collection.find_one({"username":username})
		if result_set == None:
			#client.close()
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
		#client = pymongo.MongoClient('192.168.1.14',27017)
		#mdb = client['356project']
		follow_collection = mdb['Follow']
		result_set = follow_collection.find_one({"username":username})
		if result_set == None:
			#client.close()
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
		#client = pymongo.MongoClient('192.168.1.14',27017)
		#mdb = client['356project']
		follow_collection = mdb['Follow']
		result_set = follow_collection.find_one({"username":username})
		if result_set == None:
			#client.close()
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
			mc = pylibmc.Client(["192.168.1.16"],binary=True,behaviors={"tcp_nodelay": True,"ketama": True})
			if session in mc:
				follower = mc[session]
			else:
				result_json["error"] = "log in first"
				return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			#check username exist
			#client = pymongo.MongoClient('192.168.1.9',27017)
			#mdb = client['356project']
			follow_collection = mdb2["Follow"]
			result = follow_collection.find_one({"username":username})
			if result == None:
				result_json["error"] = "Invalid username"
				#client.close()
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
					#client.close()
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
				else:
					#client.close()
					result_json["error"] = "already followed"
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
			else:
				if result == None:
					#client.close()
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
					#client.close()
					return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

@csrf_exempt
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
		#client = pymongo.MongoClient('192.168.1.9',27017)
		#mdb = client['356project']
		item_collection = mdb2["Item"]
		likes = item_collection.find_one({"id":iid})
		if likes == None:
			result_json["error"] = "Item not exist"
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		likes = likes["property"]["likes"]

		if like_boolean:
			likes += 1
			r = item_collection.update({"id":iid},{"$set":{"property":{"likes":likes}}})
			result_json["status"] = "OK"
			#client.close()
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
		else:
			if likes > 0:
				likes -= 1
				r = item_collection.update({"id":iid},{"$set":{"property":{"likes":likes}}})
				result_json["status"] = "OK"
			#client.close()
			return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")


@csrf_exempt
def addmedia(request):
	file = {}
	result_json = {"status":"error"}
	if request.method == 'POST' or request.method == 'GET':
                filea = request.FILES.get('content',False)
                #content = file_c['content']
                #print(file.content_type)
                #content_type = os.path.splitext(str(filea))[1].split(".")[1]
                #print(content_type)
                item_id = str(ObjectId())
                content = b''
                #for chunk in myfile.chunks():
                #        content += chunk
                file = {"id":item_id, "content":filea.read(),"type":"image/jpeg"}

                #cluster = Cluster(['192.168.1.24'])
                #session = cluster.connect('project356')
                stmt = session.prepare("""
			           INSERT INTO media (id, content, type)
			           VALUES (?, ?, ?)
			           """)
                try:
                        session.execute(stmt,file)
                        result_json["status"] = "OK"
                        result_json["id"] = item_id
                except:
			#print("???")
                        pass

                #session.shutdown()
                #cluster.shutdown()
                return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")
	return HttpResponse(json.dumps(result_json).encode('utf8'),content_type="application/json")

@csrf_exempt
def media(request,iid):
	file = {}
	result_json = {"status":"error"}
	#cluster = Cluster(['192.168.1.24'])
	#session = cluster.connect('project356')
	file_lookup = session.prepare("select content, type from media where id = ?")
	contents = session.execute(file_lookup,[iid])
	#session.shutdown()
	#cluster.shutdown()
	if contents != None and contents != '':
		return HttpResponse(contents[0][0], content_type=contents[0][1])
	return HttpResponse("OK")
