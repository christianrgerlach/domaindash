from datetime import datetime, timedelta
import json
from pythonwhois import get_whois
from app.utils import utils
from app.models import *

domain_names = ['google.com', 'itsupportguys.com']
domain_health_threshold_days = 90
mxtoolbox_reports = ['a', 'dns', 'mx', 'spf', 'blacklist']
mxtoolbox_daily_query_limit = 64
# Calculate number of domains we can process

def update():
    # Create a new batch
    batch = MXToolboxBatch.create(run_time = datetime.now())

    # Get domains without full reports -- TODO
    new_domains = Domain.select()

    print('### new_domains: ' + str(len(new_domains)))
    # Initialize used_queries to track how many queries are accounted for
    used_queries = len(new_domains) * len(mxtoolbox_reports)

    # Remaining queries is query limit - used_queries
    remaining_queries = mxtoolbox_daily_query_limit - used_queries

    # Get the oldest N (remainging_queries) reports

    oldest_reports = MXToolboxReport.select().order_by(MXToolboxReport.check_time).limit(3)
    print('### oldest_reports: ' + str(len(oldest_reports)))
    for old_report in oldest_reports:
        print('#### ' + str(old_report.check_time))



    # Create or new queries (does this last so as not to potentially process twice)

    for domain in new_domains:
        print('Processing new domain: ' + domain.domain_name)
        for report in mxtoolbox_reports:
            print('Creating report: ' + report)
            mxtoolbox_response_json = utils.get_mxtoolbox_response(domain.domain_name, report)
            mxtoolbox_response = json.loads(mxtoolbox_response_json)

            domain_mxtoolbox_health = True
            if len(mxtoolbox_response['Failed']) > 0:
               domain_mxtoolbox_health = False
               domain.domain_health = False
               domain.domain_mxtoolbox_health = False
               domain.save()

            report = MXToolboxReport.create(
                domain = domain,
                check_time = datetime.now(),
                command = report,
                response = mxtoolbox_response_json
                )

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

        # Get or create our domain
        # Currently no need to get but fetching for possible future usage
        domain = Domain.get_or_create(
            domain_name = domain_name,
            defaults={
                'domain_check_time' : now,
                'domain_health' : domain_health,
                'domain_registration_expiry_date' : domain_registration_expiry_date,
                'domain_registration_expiry_health' : domain_registration_expiry_health,
                'domain_ssl_issuer_cn' : domain_ssl_issuer_cn,
                'domain_ssl_expiry_date' : domain_ssl_expiry_date,
                'domain_ssl_expiry_health' : domain_ssl_expiry_health
            }
        )[0]
        # ^ get_or_create returns tuple, with second value bool representing creation
