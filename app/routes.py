import os
from datetime import datetime, timedelta
import json
from pythonwhois import get_whois
from flask import send_from_directory, render_template, redirect, url_for

from app import app
from app.utils import utils
from app.models import *

domain_health_threshold_days = 90

domain_names = ['itsupportguys.com']

domains_data = {}

mxtoolbox_reports = ['a', 'dns', 'mx', 'spf', 'blacklist']

@app.route('/')
def index():
    return render_template('index.j2', domains_data = domains_data)

@app.route('/detail/<domain_name>')
def domain_detail(domain_name):
    whois = get_whois(domain_name, normalized = True)
    ssl_expiry_date = utils.ssl_expiry_datetime(domain_name)
    mxtoolbox_report = utils.get_mxtoolbox_report(domain_name, mxtoolbox_reports)

    return render_template('domain_detail.j2',
        domain_name = domain_name,
        whois = whois,
        ssl_expiry_date = ssl_expiry_date,
        mxtoolbox_report = mxtoolbox_report
        )

@app.route('/detail2/<domain_name>')
def domain_detail2(domain_name):
    domain_data = domains_data[domain_name]
    return render_template('domain_detail2.j2', domain_name = domain_name, domain_data = domain_data)


@app.route('/build', methods = ['POST'])
def build():
    domain_health_threshold_date = datetime.now() + timedelta(days = domain_health_threshold_days) 

    for domain_name in domain_names:
        domain_whois = get_whois(domain_name, normalized = True)
        domain_registration_expiry_date = domain_whois['expiration_date'][0]
        domain_ssl_expiry_date = utils.ssl_expiry_datetime(domain_name)
        
        domain_health = True
        domain_registration_expiry_health = (True, domain_registration_expiry_date)
        domain_ssl_expiry_health = (True, domain_ssl_expiry_date)

        if domain_registration_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_registration_expiry_health = False

        if domain_ssl_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_ssl_expiry_health = False

        domain = Domain.create(
            domain_name = domain_name,
            domain_health = domain_health,
            domain_registration_expiry_date = domain_registration_expiry_date,
            domain_registration_expiry_health = domain_registration_expiry_health,
            domain_ssl_expiry_date = domain_ssl_expiry_date,
            domain_ssl_expiry_health = domain_ssl_expiry_health
        )

        for report in mxtoolbox_reports:
            mxtoolbox_response_json = utils.get_mxtoolbox_response(domain_name, report)
            mxtoolbox_response = json.loads(mxtoolbox_response_json)

            domain_mx_toolbox_health = True
            if len(mxtoolbox_response['Failed']) > 0:
               domain_mx_toolbox_health = False
               domain.domain_health = False
               domain.save()

            report = MXToolboxReport.create(
                domain = domain,
                mx_toolbox_api_query_batch = None,
                command = report,
                response = mxtoolbox_response,
                domain_mx_toolbox_health = domain_mx_toolbox_health
                )

    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    dir = os.path.join(app.root_path, 'static')
    print(dir)
    return send_from_directory(dir ,'favicon.ico', mimetype = 'image/vnd.microsoft.icon')