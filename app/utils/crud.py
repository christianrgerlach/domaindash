from datetime import datetime, timedelta
import json
import peewee
from pythonwhois import get_whois
from app.utils import utils
from app.models import *


domain_names = ['google.com', 'fraplin.fun']
domain_health_threshold_days = 90
mxtoolbox_reports = ['a', 'dns', 'mx', 'spf', 'blacklist']
mxtoolbox_daily_query_limit = 64

def update():
    # Get never-run reports without full reports -- TODO
    new_reports = MXToolboxReport.select().where(MXToolboxReport.check_time.is_null(True)).limit(64)

    print('### new_reports: ' + str(len(new_reports)))

    # Remaing queries is limit - length of new ones
    remaining_queries = mxtoolbox_daily_query_limit - len(new_reports)

    # Get the oldest N (remainging_queries) reports
    oldest_reports = MXToolboxReport.select().where( MXToolboxReport.check_time.is_null(False)).order_by(MXToolboxReport.check_time).limit(remaining_queries)
    print('### oldest_reports: ' + str(len(oldest_reports)))
    for old_report in oldest_reports:
        print('#### domain: %s command: %s check time: %s ' % (old_report.domain.domain_name, old_report.command, old_report.check_time))

    # For now treat new reports as all reports
    # TODO join oldest_reports
    reports = new_reports

    for report in reports:
        mxtoolbox_response_json = utils.get_mxtoolbox_response(report.domain.domain_name, report.command)

        report.check_time = datetime.now()
        report.response = mxtoolbox_response_json
        report.save()

        mxtoolbox_response = json.loads(mxtoolbox_response_json)
        domain_mxtoolbox_health = True
        if len(mxtoolbox_response['Failed']) > 0:
           report.domain.domain_mxtoolbox_health = False
           report.domain.domain_health = False
           report.domain.domain_mxtoolbox_health = False
           report.domain.save()

def build():
    domain_health_threshold_date = datetime.now() + timedelta(days = domain_health_threshold_days) 

    for domain_name in domain_names:
        now = datetime.now()
        domain_whois = get_whois(domain_name, normalized = True)
        domain_registration_expiry_date = domain_whois['expiration_date'][0]
        ssl_info = utils.get_ssl_info(domain_name)
        domain_ssl_issuer_cn = ssl_info[0]
        domain_ssl_expiry_date = ssl_info[1]
        
        domain_health = True
        domain_registration_expiry_health = (True, domain_registration_expiry_date)
        domain_ssl_expiry_health = (True, domain_ssl_expiry_date)

        if domain_registration_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_registration_expiry_health = False

        if domain_ssl_expiry_date < domain_health_threshold_date:
            domain_health = False
            domain_ssl_expiry_health = False

        try:
            domain = Domain.get(Domain.domain_name == domain_name)
            domain.domain_check_time = now
            domain.domain_health = domain_health
            domain.domain_registration_expiry_date = domain_registration_expiry_date
            domain.domain_registration_expiry_health = domain_registration_expiry_health
            domain.domain_ssl_issuer_cn = domain_ssl_issuer_cn
            domain.domain_ssl_expiry_date = domain_ssl_expiry_date
            domain.domain_ssl_expiry_health = domain.domain_ssl_expiry_health
            domain.save()
        except peewee.DoesNotExist:
            domain = Domain.create(
                domain_name = domain_name,
                domain_check_time = now,
                domain_health = domain_health,
                domain_registration_expiry_date =   domain_registration_expiry_date,
                domain_registration_expiry_health = domain_registration_expiry_health,
                domain_ssl_issuer_cn = domain_ssl_issuer_cn,
                domain_ssl_expiry_date = domain_ssl_expiry_date,
                domain_ssl_expiry_health = domain_ssl_expiry_health
            )
            # Create our blank MXToolbox reports
            for report in mxtoolbox_reports:
                report = MXToolboxReport.create(
                    domain = domain,
                    command = report,
                    response = '{}'
                    )



