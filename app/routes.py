import os
from datetime import datetime, timedelta
import json

from flask import send_from_directory, render_template, redirect, url_for
from pythonwhois import get_whois

from app import app
from app.utils import utils


domain_health_threshold_days = 90

domain_names = ['itsupportguys.com', 'itsupportguys.net']
domains_data = {}

@app.route('/')
def index():
    return render_template('index.j2', domains_data = domains_data)

@app.route('/detail/<domain_name>')
def domain_detail(domain_name):
    whois = get_whois(domain_name, normalized = True)
    ssl_expiry_date = utils.ssl_expiry_datetime(domain_name)
    mxtoolbox_report = utils.get_mxtoolbox_response(domain_name)

    return render_template('domain_detail.j2',
        domain_name = domain_name,
        whois = whois,
        ssl_expiry_date = ssl_expiry_date,
        mxtoolbox_report = mxtoolbox_report
        )

@app.route('/build', methods = ['POST'])
def build():
    global domains_data
    domains_data = {}

    domain_health_threshold_date = datetime.now() + timedelta(days = domain_health_threshold_days) 

    for domain_name in domain_names:
        domain_whois = get_whois(domain_name, normalized = True)
        domain_registration_expiry_date = domain_whois['expiration_date'][0]
        domain_ssl_expiry_date = utils.ssl_expiry_datetime(domain_name)
        domain_mxtoolbox_report = utils.get_mxtoolbox_response(domain_name)

        domain_health = True
        domain_registration_expiry_health = (True, domain_registration_expiry_date)
        domain_ssl_expiry_health = (True, domain_ssl_expiry_date)
        domain_mxtoolbox_report_health = (True, domain_mxtoolbox_report)

        if domain_registration_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_registration_expiry_health = (False, domain_registration_expiry_date)

        if domain_ssl_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_ssl_expiry_health = (False, domain_ssl_expiry_date)

        if len(domain_mxtoolbox_report['Failed']) > 0:
            domain_health = False
            domain_mxtoolbox_report_health = (False, domain_mxtoolbox_report)

        domain_data = (domain_health, domain_registration_expiry_health, domain_ssl_expiry_health)
        domains_data[domain_name] = domain_data

    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    dir = os.path.join(app.root_path, 'static')
    print(dir)
    return send_from_directory(dir ,'favicon.ico', mimetype = 'image/vnd.microsoft.icon')