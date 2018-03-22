from django.shortcuts import render
import datetime
from django.http import HttpResponseBadRequest
# Create your views here.
import json, requests,os
import urllib.request
from django.views.decorators.csrf import csrf_exempt
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
			with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'sessions.json','r') as jfile:
				old_ses = json.load(jfile)
			u = ''
			for i in old_ses['sessions']:
				if session in old_ses['sessions'][i] :
					u = i
			if u == '':
				return render(request,'html/index2.html')

			with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'accounts.json','r') as jfile:
				old_accs = json.load(jfile)
			for i in old_accs['accounts']:
				if i['username'] == u:
					user = i

			###########################################
			################if new grid, add to gamelist
			username = u
			grid = user['grid']
			grid_new = True
			for i in grid:
				if i != ' ':
					grid_new = False
			if grid_new:
				with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'gamelists.json','r') as jfile:
					gamelist = json.load(jfile)
				for i in range(len(gamelist['gamelists'])):
					if username in gamelist['gamelists'][i]:
						gid = len(gamelist['gamelists'][i][username])
						if gid == 0 or gamelist['gamelists'][i][username][gid-1]['winner'] != 'None':
							date = datetime.datetime.now().strftime("%y-%m-%d")
							gamelist['gamelists'][i][username] += [{'id':gid, 'grid':grid, 'start_date':date,'winner':'None'}]
							with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'gamelists.json','w') as ofile:
								json.dump( gamelist,ofile)
			###########################################

			data = {'grid': json.dumps(user['grid']) , 'human':user['human']}
			#print(data)
			#send
			resp = render(request,'html/play2.html',data)
			resp.set_cookie('SESSION',session)
			return resp
	elif request.method == 'POST':
		if request.POST.get('username'):
			username = request.POST.get('username')
			
			if username != None:

				password = request.POST.get('password')
				send_json = {'username':username,'password':password}
				headers = {'content-type': 'application/json'}
				r = requests.post('http://130.245.169.164/ttt/login', data=json.dumps(send_json), headers=headers)
				
				if r.cookies['SESSION'] != "":
					session = r.cookies['SESSION']
					#session
					
					with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'sessions.json','r') as jfile:
						old_ses = json.load(jfile)
					u = ''
					for i in old_ses['sessions']:
						if session in old_ses['sessions'][i] :
							u = i
					if u == '':
						return render(request,'html/index2.html')

					with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'accounts.json','r') as jfile:
						old_accs = json.load(jfile)
					for i in old_accs['accounts']:
						if i['username'] == u:
							user = i
					###########################################
					################if new grid, add to gamelist
					grid = user['grid']
					grid_new = True
					for i in grid:
						if i != ' ':
							grid_new = False
					if grid_new:
						with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'gamelists.json','r') as jfile:
							gamelist = json.load(jfile)
						for i in range(len(gamelist['gamelists'])):
							if username in gamelist['gamelists'][i]:
								gid = len(gamelist['gamelists'][i][username])
								if gid == 0 or gamelist['gamelists'][i][username][gid-1]['winner'] != 'None':
									date = datetime.datetime.now().strftime("%y-%m-%d")
									gamelist['gamelists'][i][username] += [{'id':gid, 'grid':grid, 'start_date':date,'winner':'None'}]
									with open(os.path.dirname(os.path.realpath(__file__))[:-4]+'gamelists.json','w') as ofile:
										json.dump( gamelist,ofile)
					###########################################
					data = {'grid': json.dumps(user['grid']) , 'human':user['human']}
					#send

					resp = render(request,'html/play2.html',data)
					resp.set_cookie('SESSION',r.cookies['SESSION'])
					
				return resp
				
			
	return render(request,'html/index2.html')
