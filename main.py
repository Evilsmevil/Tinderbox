from flask import Flask, render_template, request
import urllib2
import urllib
import json
import pprint
import re

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def home():
    """Return a friendly HTTP greeting."""
    return render_template('home.html')

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/runSearch/', methods=['POST'])
def runSearch():
	searchTerm = request.form['searchName'] + ' music' + ' *@*' #+ 'music +*@*'
	url = 'https://www.googleapis.com/customsearch/v1?q=' + searchTerm + '&key=AIzaSyCxI21xhbKxiuXPMEv_DXYKURFFQEwhKdo&cx=000191502597213523554:tr_xxzw3jwa'
	response = urllib.urlopen(url)
	data = json.load(response)
	app.logger.info('num things found ' + str(data['queries']['request'][0]['count']))

	if data['queries']['request'][0]['count'] > 0 :
		searchTerm=data['queries']['request'][0]['searchTerms']
		#app.logger.info('looking at ' + data['items'][0]['title'])
		#firstResult=data['items'][0]['title']

		num = len(data['items'])
		for i in range(0, num) :
			siteurl = data['items'][i]['link']
			try:
				if '.pdf' in siteurl:
					raise Exception('unable to parse pdfs')
				siteResponse = urllib.urlopen(siteurl)
				match = re.findall(r'[\w\.-]+@[\w\.-]+', siteResponse.read())
				phonematch = re.findall(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', siteResponse.read())
				data['items'][i]['emails'] = match
				data['items'][i]['emailcount'] = len(match)
				data['items'][i]['phones'] = phonematch
				data['items'][i]['phonecount'] = len(phonematch)
			except:
				data['items'][i]['emails'] = 'error'
				data['items'][i]['emailcount'] = 0
				data['items'][i]['phones'] = 'error'
				data['items'][i]['phonecount'] = 0
	
			return render_template('searchResults.html', searchTerm=searchTerm, results=data['items'])
	else :
		return render_template('home.html')


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404
    
