import os
import json
from flask import send_from_directory, render_template, redirect, url_for

from app import app
from app.utils import crud

from app.models import *

domain_mxtoolbox_reports = {}

@app.route('/')
def index():
    domains = Domain.select()
    # Instantiate MXToolbox report python objects
    for domain in domains:
        # Create a dict to map report type to report object
        mxtoolbox_reports = {}
        for mxtoolbox_report in domain.mxtoolbox_reports:
            # Add object, generated from saved JSON, to our dict, using report type as key
            mxtoolbox_reports[mxtoolbox_report.command] = json.loads(mxtoolbox_report.response)
        domain_mxtoolbox_reports[domain.domain_name] = mxtoolbox_reports
    return render_template('index.j2', domains = domains, domain_mxtoolbox_reports = domain_mxtoolbox_reports)

# @app.route('/detail/<domain_name>')
# def domain_detail(domain_name):
#     whois = get_whois(domain_name, normalized = True)
#     ssl_expiry_date = utils.ssl_expiry_datetime(domain_name)
#     mxtoolbox_report = utils.get_mxtoolbox_report(domain_name, mxtoolbox_reports)

#     return render_template('domain_detail.j2',
#         domain_name = domain_name,
#         whois = whois,
#         ssl_expiry_date = ssl_expiry_date,
#         mxtoolbox_report = mxtoolbox_report
#         )

# @app.route('/detail2/<domain_name>')
# def domain_detail2(domain_name):
#     domain_data = domains_data[domain_name]
#     return render_template('domain_detail2.j2', domain_name = domain_name, domain_data = domain_data)

@app.route('/build', methods = ['POST'])
def build():
    crud.build()
    return redirect(url_for('index'))

@app.route('/update', methods = ['POST'])
def update():
    crud.update()
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    dir = os.path.join(app.root_path, 'static')
    print(dir)
    return send_from_directory(dir ,'favicon.ico', mimetype = 'image/vnd.microsoft.icon')