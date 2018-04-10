from flask import Flask
from re import sub
    
app = Flask(__name__)

@app.template_filter('type')
def datetimeformat(value):
    return type(value)

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d'):
    return value.strftime(format)

@app.template_filter('google_search')
def google_search(value):
	query = sub(r'\s+', '+', value)
	url = 'http://www.google.com/search?q=' + query
	return url




from app import routes

