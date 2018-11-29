from datetime import datetime, timedelta
import json
from pythonwhois import get_whois
from app.utils import utils
from app.models import *

domain_names = ['google.com', 'itsupportguys.com']
domain_health_threshold_days = 90
mxtoolbox_reports = ['a', 'dns', 'mx', 'spf', 'blacklist']
mxtoolbox_daily_queries = 64
# Calculate number of domains we can process
mxtoolbox_query_limit =  mxtoolbox_daily_queries // len(mxtoolbox_reports)

def update():
    # Create a new batch
    batch = MXToolboxBatch.create(mxtoolbox_batch_time = datetime.now())


    # Get domains without MXToolbox report
    new_domains = Domain.select().where(Domain.mxtoolbox_batch == None)

    # Initialize used_queries to track how many queries are accounted for
    used_queries = len(new_domains) * mxtoolbox_reports

    # Remaining queries is query limit - used_queries
    remaining_queries = mxtoolbox_query_limit - used_queries

    # Number of domains we can process is remaining limit divided by the number of reports we request
    domain_queries = remaining_queries // len(mxtoolbox_reports)

    # Select $domain_queries domains, sorted by timestamp of the most recent batch

    # Get the 
    MXToolboxReport.select().join(Domain).where(MXToolboxReport.domain == Domain)

    print(len(oldest_domains))

    for domain in oldest_domains:
        print(domain.domain_name)

        for report in mxtoolbox_reports:
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
                mxtoolbox_check_time = datetime.now(),
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
