from quart import Quart,request,Response
import requests
import asyncio
from bs4 import BeautifulSoup

app = Quart(__name__)

website='www.ahmia.fi'

def get(url,headers):
	return requests.get(url,headers=headers)
def post(url,args,headers):
	return requests.post(url,headers=headers,data=args)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>',methods=['GET','POST'])
async def index(path):
	loop = asyncio.get_event_loop()
	url=f'https://{website}/'+request.full_path
	headers = dict(request.headers)
	for i in ['Remote-Addr','Host','Referer','X-Forwarded-For','Accept-Encoding']:  
		try:del headers[i]
		except:pass
	headers['Referer'] = url
	if request.method=='GET':r = await loop.run_in_executor(None, get, url, headers)
	elif request.method=='POST':r = await loop.run_in_executor(None, post, url,await request.data, headers)
	returnheaders=r.headers
	for i in ['Date','Expires','X-XSS-Protection','X-Frame-Options','Content-Encoding','Content-Length']:
		try:del returnheaders[i]
		except:pass
	content=r.content
	try:
		print(r.headers['Content-Type'])
		if r.headers['Content-Type'].startswith('text/html'):
			content=content.decode().replace(website,dict(request.headers)['Host'])
			content=open('inject.html').read()+content
			try:
				soup=BeautifulSoup(content,'html.parser')
				for div in soup.find_all('div', {'class':'native-ad-container'}): #REDDIT ADBLOCK 
					div.decompose()
				content=str(soup)
			except Exception as e:
				print(e)
	except:
		pass
	resp = Response(content)
	resp.headers = returnheaders
	return resp



app.run(host='0.0.0.0', port=8080)
