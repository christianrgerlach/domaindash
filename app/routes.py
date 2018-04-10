import os
from datetime import datetime, timedelta

from flask import send_from_directory, render_template
from pythonwhois import get_whois

from app import app
from app.utils import utils

domain_health_threshold_days = 90

domain_names = ['google.com', 'bing.com', 'yahoo.com']

@app.route('/')
def index():
    domains_data = []
    domain_health_threshold_date = datetime.now() + timedelta(days = domain_health_threshold_days) 

    for domain_name in domain_names:
        domain_whois = get_whois(domain_name, normalized = True)

        domain_registration_expiry_date = domain_whois['expiration_date'][0]
        domain_ssl_expiry_date = utils.ssl_expiry_datetime(domain_name)

        print (type(domain_registration_expiry_date))
        print (type(domain_ssl_expiry_date))

        domain_health = True
        domain_registration_expiry_health = (True, domain_registration_expiry_date)
        domain_ssl_expiry_health = (True, domain_ssl_expiry_date)

        if domain_registration_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_registration_expiry_health = (False, domain_registration_expiry_date)

        if domain_ssl_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_ssl_expiry_health = (False, domain_ssl_expiry_date)

        domain_data = (domain_name, domain_health, domain_registration_expiry_health, domain_ssl_expiry_health)
        domains_data.append(domain_data)

    print(domains_data)

    return render_template('index.j2', domains_data = domains_data)

@app.route('/<domain_name>')
def domain(domain_name):
    whois = get_whois(domain_name, normalized = True)
    ssl_expiry_date = utils.ssl_expiry_datetime(domain_name)
    return render_template('domain_detail.j2', domain_name = domain_name, whois = whois, ssl_expiry_date = ssl_expiry_date)


@app.route('/favicon.ico')
def favicon():
    dir = os.path.join(app.root_path, 'static')
    print(dir)
    return send_from_directory(dir ,'favicon.ico', mimetype = 'image/vnd.microsoft.icon')