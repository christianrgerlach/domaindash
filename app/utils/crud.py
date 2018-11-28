from datetime import datetime, timedelta
import json
from pythonwhois import get_whois
from app.utils import utils
from app.models import *

domain_health_threshold_days = 90
domain_names = ['fraplin.fun', 'example.com', 'ojaimark.com']
mxtoolbox_reports = ['a', 'dns', 'mx', 'spf', 'blacklist']

def update():
    print("Method to update without creating")

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

        # Get or create our domain
        # Currently no need to get but fetching for possible future usage
        domain = Domain.get_or_create(
            domain_name = domain_name,
            defaults={
                'domain_check_time' : datetime.now(),
                'domain_health' : domain_health,
                'domain_registration_expiry_date' : domain_registration_expiry_date,
                'domain_registration_expiry_health' : domain_registration_expiry_health,
                'domain_ssl_expiry_date' : domain_ssl_expiry_date,
                'domain_ssl_expiry_health' : domain_ssl_expiry_health
            }
        )[0]

        for report in mxtoolbox_reports:
            mxtoolbox_response_json = utils.get_mxtoolbox_response(domain_name, report)
            mxtoolbox_response = json.loads(mxtoolbox_response_json)

            domain_mxtoolbox_health = True
            if len(mxtoolbox_response['Failed']) > 0:
               domain_mxtoolbox_health = False
               domain.domain_health = False
               domain.domain_mxtoolbox_health = False
               domain.save()

            report = MXToolboxReport.create(
                domain = domain,
                mxtoolbox_check_time = datetime.now(),
                command = report,
                response = mxtoolbox_response_json
                )
