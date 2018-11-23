import os
from flask import send_from_directory, render_template, redirect, url_for

from app import app
from app.utils import crud

@app.route('/')
def index():
    return render_template('index.j2', domains_data = None)

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

@app.route('/favicon.ico')
def favicon():
    dir = os.path.join(app.root_path, 'static')
    print(dir)
    return send_from_directory(dir ,'favicon.ico', mimetype = 'image/vnd.microsoft.icon')